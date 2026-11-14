"""Provider interface shared by every rater backend."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class Request:
    user: str                       # the full rater prompt
    transcript: str                 # just the rendered messages (used only by the offline baselines)
    meta: dict = field(default_factory=dict)  # condition labels (used only by the planted-effects mock)


@dataclass
class Response:
    text: str
    stop_reason: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    served_model: str | None = None
    extra: dict = field(default_factory=dict)


class FatalProviderError(Exception):
    """Configuration or credential problem: retrying will not help, so the runner stops this model."""


# Phrases vendors use when a daily or free quota (not a per-minute limit) is used up.
# Gemini: quota ids like "GenerateRequestsPerDayPerProjectPerModel-FreeTier".
# Qwen/DashScope with "Free quota only" on: "...FreeTierOnly: The free tier of the model has been exhausted".
# OpenAI: "insufficient_quota".
_QUOTA_MARKERS = ("perday", "per day", "insufficient_quota", "freetieronly",
                  "free tier of the model has been exhausted", "free quota", "allocationquota")


def quota_exhausted(message: str) -> bool:
    m = message.lower()
    return any(k in m for k in _QUOTA_MARKERS)


def load_user_env(names: list[str]) -> list[str]:
    """On Windows, copy variables saved with `setx` (HKCU\\Environment) into this process when missing.

    A terminal that was already open when the key was saved does not see it otherwise.
    Returns the names that were loaded. No-op elsewhere.
    """
    import os
    import sys

    if sys.platform != "win32":
        return []
    import winreg

    loaded = []
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
            for name in names:
                if os.environ.get(name):
                    continue
                try:
                    value, _ = winreg.QueryValueEx(k, name)
                except FileNotFoundError:
                    continue
                if isinstance(value, str) and value.strip():
                    os.environ[name] = value.strip()
                    loaded.append(name)
    except OSError:
        pass
    return loaded


def short_error(e: Exception, limit: int = 300) -> str:
    s = " ".join(str(e).split())
    return s if len(s) <= limit else s[:limit] + "..."


class Provider(Protocol):
    system: str | None

    def complete(self, req: Request) -> Response: ...
