"""Rater backends. SDK imports are lazy so the offline raters work with the standard library alone."""
from __future__ import annotations

from .base import FatalProviderError, Provider, Request, Response

OFFLINE_PROVIDERS = ("mock", "surface")


def make_provider(cfg: dict) -> Provider:
    kind = cfg.get("provider")
    if kind == "mock":
        from .offline import PlantedMock
        return PlantedMock(cfg)
    if kind == "surface":
        from .offline import SurfaceBaseline
        return SurfaceBaseline(cfg)
    if kind == "anthropic":
        try:
            from .anthropic_provider import AnthropicProvider
        except ImportError as e:
            raise FatalProviderError("the `anthropic` package is not installed: pip install anthropic") from e
        return AnthropicProvider(cfg)
    if kind == "openai_compat":
        try:
            from .openai_compat import OpenAICompatProvider
        except ImportError as e:
            raise FatalProviderError("the `openai` package is not installed: pip install openai") from e
        return OpenAICompatProvider(cfg)
    raise FatalProviderError(f"unknown provider {kind!r} (expected mock, surface, anthropic, openai_compat)")


__all__ = ["FatalProviderError", "Provider", "Request", "Response", "make_provider", "OFFLINE_PROVIDERS"]
