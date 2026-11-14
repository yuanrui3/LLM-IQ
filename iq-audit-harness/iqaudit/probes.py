"""Probe definitions: turn a persona + variant name into the messages a rater will see.

Each variant has a *kind*, which drives the analysis:
  reference   base: standard English, sound reasoning. Everything is compared to it.
  control     flawed: same style as base, broken reasoning. A valid rater SHOULD score it lower.
  irrelevant  same content as base, different surface. A valid rater should NOT move.
  empty       no messages at all. A valid rater should decline.
"""
from __future__ import annotations

import hashlib
import random
import re
from dataclasses import dataclass

from .data import Paste, Persona

VARIANT_KINDS: dict[str, str] = {
    "base": "reference",
    "flawed": "control",
    # authored surface variants
    "aae": "irrelevant",
    "l2": "irrelevant",
    "zh_formal": "irrelevant",
    "zh_casual": "irrelevant",
    "verbose": "irrelevant",
    "ai_polished": "irrelevant",
    # programmatic surface variants
    "pasted": "irrelevant",
    "phone_style": "irrelevant",
    "format_json": "irrelevant",
    # nothing to judge
    "empty": "empty",
}

VARIANT_LABELS: dict[str, str] = {
    "base": "Standard English, sound reasoning (reference)",
    "flawed": "Same style, flawed reasoning (positive control)",
    "aae": "African American English guise",
    "l2": "Non-native English (Chinese-L1 patterns)",
    "zh_formal": "Chinese, formal written register",
    "zh_casual": "Chinese, WeChat casual register",
    "verbose": "Padded with filler and jargon",
    "ai_polished": "Rewritten as polished AI prose",
    "pasted": "Base + one pasted technical block",
    "phone_style": "Lowercase, no apostrophes, small typos",
    "format_json": "Base rendered as a JSON chat export",
    "empty": "No messages at all",
}

PROGRAMMATIC = ("pasted", "phone_style", "format_json", "empty")
NO_PERSONA = "_none"


@dataclass(frozen=True)
class Condition:
    persona: str           # persona id, or NO_PERSONA for `empty`
    variant: str
    messages: tuple[str, ...]
    lang: str              # language of the messages: "en" | "zh"
    render: str            # "plain" | "json"

    @property
    def kind(self) -> str:
        return VARIANT_KINDS[self.variant]


def build_condition(persona: Persona | None, variant: str, pastes: dict[str, Paste]) -> Condition:
    if variant not in VARIANT_KINDS:
        raise KeyError(f"unknown variant {variant!r}; known: {sorted(VARIANT_KINDS)}")
    if variant == "empty":
        return Condition(NO_PERSONA, "empty", (), "en", "plain")
    assert persona is not None
    if variant in persona.variants:
        v = persona.variants[variant]
        return Condition(persona.id, variant, v.messages, v.lang, "plain")

    base = persona.variants["base"].messages
    if variant == "format_json":
        return Condition(persona.id, variant, base, "en", "json")
    if variant == "phone_style":
        return Condition(persona.id, variant, phone_style(base, seed=persona.id), "en", "plain")
    if variant == "pasted":
        if not persona.paste or persona.paste not in pastes:
            raise KeyError(f"persona {persona.id!r} names paste {persona.paste!r}, not found in pastes.toml")
        p = pastes[persona.paste]
        msgs = list(base)
        msgs.insert(len(msgs) // 2, f"{p.intro}\n{p.text}")
        return Condition(persona.id, variant, tuple(msgs), "en", "plain")
    raise KeyError(f"persona {persona.id!r} has no variant {variant!r}")


_WORD = re.compile(r"[A-Za-z]{5,}")


def phone_style(messages: tuple[str, ...], seed: str) -> tuple[str, ...]:
    """Lowercase, drop apostrophes and final periods, swap two inner letters in one word per message.

    Deterministic for a given seed, so every run sees the same text.
    """
    rng = random.Random(int(hashlib.sha256(seed.encode()).hexdigest(), 16))
    out = []
    for msg in messages:
        m = msg.lower().replace("'", "").replace("’", "")
        m = m.rstrip(".")
        words = list(_WORD.finditer(m))
        if words:
            w = rng.choice(words)
            s = w.group()
            i = rng.randrange(1, len(s) - 2)
            typo = s[:i] + s[i + 1] + s[i] + s[i + 2:]
            m = m[: w.start()] + typo + m[w.end():]
        out.append(m)
    return tuple(out)
