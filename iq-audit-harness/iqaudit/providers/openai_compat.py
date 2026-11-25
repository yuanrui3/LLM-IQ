"""Non-Anthropic models through the OpenAI Python SDK's chat-completions interface (`pip install openai`).

Many vendors expose this interface (OpenAI, DeepSeek, Alibaba Qwen/DashScope, Google Gemini,
xAI, OpenRouter); point `base_url` at the vendor and `api_key_env` at the variable holding its key.
Anything in the model's `extra` table is passed straight through (e.g. temperature,
max_completion_tokens), so vendor-specific parameters stay in config rather than code.
"""
from __future__ import annotations

import os

import openai

from .base import FatalProviderError, ProviderOverloaded, Request, Response
from .base import quota_exhausted as _quota_exhausted
from .base import short_error as _short


def _error_text(e: openai.APIStatusError) -> str:
    """The SDK's str(e) can be just 'Error code: 429'; the quota details live in the response body."""
    parts = [str(e)]
    try:
        parts.append(e.response.text)
    except Exception:
        parts.append(repr(getattr(e, "body", "")))
    return " ".join(parts)


class OpenAICompatProvider:
    def __init__(self, cfg: dict):
        self.model = cfg["model"]
        self.system = cfg.get("system")
        self.extra = dict(cfg.get("extra", {}))
        key_env = cfg.get("api_key_env", "OPENAI_API_KEY")
        key = os.environ.get(key_env)
        if not key:
            raise FatalProviderError(f"{key_env} is not set")
        self.client = openai.OpenAI(
            api_key=key,
            base_url=cfg.get("base_url"),
            max_retries=int(cfg.get("max_retries", 4)),
            timeout=float(cfg.get("timeout_s", 300)),
        )

    def complete(self, req: Request) -> Response:
        messages = []
        if self.system:
            messages.append({"role": "system", "content": self.system})
        messages.append({"role": "user", "content": req.user})
        try:
            resp = self.client.chat.completions.create(model=self.model, messages=messages, **self.extra)
        except openai.RateLimitError as e:
            # Per-minute limits are retried by the SDK and, failing that, recorded as a retryable error.
            # A used-up daily or free quota will not recover within this run, so stop this model instead.
            if _quota_exhausted(_error_text(e)):
                raise FatalProviderError(f"daily or free quota used up; run again after it resets to continue "
                                         f"({_short(Exception(_error_text(e)))})") from e
            raise
        except (openai.AuthenticationError, openai.PermissionDeniedError) as e:
            if _quota_exhausted(_error_text(e)):
                raise FatalProviderError(f"free quota used up ({_short(e)})") from e
            raise FatalProviderError(f"credentials rejected: {_short(e)}") from e
        except (openai.NotFoundError, openai.BadRequestError) as e:
            raise FatalProviderError(f"request rejected for {self.model!r}: {_short(e)}") from e
        except openai.APITimeoutError as e:
            raise ProviderOverloaded(f"request timed out ({_short(e)})") from e
        except openai.APIStatusError as e:
            if e.status_code == 402:
                # Payment required: prepaid credits used up or billing not active. Retrying can't help.
                raise FatalProviderError(f"payment required (credits used up or billing inactive): "
                                         f"{_short(Exception(_error_text(e)))}") from e
            text = _error_text(e).lower()
            if e.status_code in (503, 529) or "high demand" in text or "overloaded" in text:
                raise ProviderOverloaded(f"service busy: {_short(Exception(_error_text(e)))}") from e
            raise

        choice = resp.choices[0]
        usage = resp.usage
        extra = {}
        if usage is not None:
            # Some vendors (Gemini) leave hidden "thinking" tokens out of completion_tokens but count them in
            # total_tokens, and bill them as output. Record them so budgets can count them.
            total = getattr(usage, "total_tokens", None)
            p, c = getattr(usage, "prompt_tokens", None) or 0, getattr(usage, "completion_tokens", None) or 0
            details = getattr(usage, "completion_tokens_details", None)
            reported = getattr(details, "reasoning_tokens", None) if details else None
            hidden = max(0, total - p - c) if total else 0
            extra["reasoning_tokens"] = int(reported) if reported else hidden
        return Response(
            text=choice.message.content or "",
            stop_reason=choice.finish_reason,
            input_tokens=getattr(usage, "prompt_tokens", None) if usage else None,
            output_tokens=getattr(usage, "completion_tokens", None) if usage else None,
            served_model=resp.model,
            extra=extra,
        )
