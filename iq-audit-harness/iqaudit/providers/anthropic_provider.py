"""Claude via the official Anthropic Python SDK (`pip install anthropic`).

Credentials resolve the SDK's usual way: ANTHROPIC_API_KEY, ANTHROPIC_AUTH_TOKEN,
or an `ant auth login` profile. No temperature is sent: current API versions reject it,
so repeats measure the model's default sampling.

Refusal fallbacks are deliberately NOT enabled. A fallback would silently answer with a
different model, which would mix two models into one row of the audit. A safety-classifier
refusal is recorded as its own outcome (stop_reason "refusal") instead.
"""
from __future__ import annotations

import anthropic

from .base import FatalProviderError, ProviderOverloaded, Request, Response


class AnthropicProvider:
    def __init__(self, cfg: dict):
        self.model = cfg.get("model", "claude-opus-5-5")
        self.max_tokens = int(cfg.get("max_tokens", 16000))
        self.effort = cfg.get("effort")  # None = model default; else low|medium|high|xhigh|max
        self.system = cfg.get("system")
        self.client = anthropic.Anthropic(
            max_retries=int(cfg.get("max_retries", 4)),
            timeout=float(cfg.get("timeout_s", 300)),
        )

    def complete(self, req: Request) -> Response:
        kwargs: dict = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": req.user}],
        }
        if self.system:
            kwargs["system"] = self.system
        if self.effort:
            kwargs["output_config"] = {"effort": self.effort}

        try:
            msg = self.client.messages.create(**kwargs)
        except (anthropic.AuthenticationError, anthropic.PermissionDeniedError) as e:
            raise FatalProviderError(f"Anthropic credentials rejected: {e.message}") from e
        except anthropic.NotFoundError as e:
            raise FatalProviderError(f"Unknown model {self.model!r}: {e.message}") from e
        except anthropic.BadRequestError as e:
            raise FatalProviderError(f"Request rejected for {self.model!r}: {e.message}") from e
        except anthropic.APITimeoutError as e:
            raise ProviderOverloaded(f"request timed out: {e}") from e
        except anthropic.APIStatusError as e:
            if e.status_code in (503, 529):
                raise ProviderOverloaded(f"service busy ({e.status_code}): {e.message}") from e
            raise
        except TypeError as e:
            # The SDK raises TypeError when no credentials resolve, or for an unsupported argument.
            raise FatalProviderError(
                f"{e}. Set ANTHROPIC_API_KEY or run `ant auth login`." if "authentication" in str(e)
                else f"SDK rejected the request arguments: {e}"
            ) from e
        # RateLimitError / 5xx / connection errors propagate after the SDK's own retries;
        # the runner records them as errors and a re-run retries just those rows.

        text = "".join(b.text for b in msg.content if b.type == "text")
        extra = {"request_id": getattr(msg, "_request_id", None)}
        if msg.stop_reason == "refusal":
            details = getattr(msg, "stop_details", None)
            extra["refusal_category"] = getattr(details, "category", None) if details else None
        return Response(
            text=text,
            stop_reason=msg.stop_reason,
            input_tokens=msg.usage.input_tokens,
            output_tokens=msg.usage.output_tokens,
            served_model=msg.model,
            extra=extra,
        )
