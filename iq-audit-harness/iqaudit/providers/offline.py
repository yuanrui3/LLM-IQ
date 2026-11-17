"""Offline raters that need no API key.

PlantedMock      Simulates a biased rater with known, configurable effects. The test suite runs the
                 whole pipeline against it and checks the analysis recovers the planted numbers.
                 It reads the condition labels from `Request.meta`, which no real provider sees.

SurfaceBaseline  Scores only surface features of the transcript (word length, rare-word share,
                 vocabulary variety, message length) with no understanding at all. It is a
                 reference point: a real model whose profile looks like this one is reacting to
                 presentation, not reasoning.
"""
from __future__ import annotations

import hashlib
import random
import re
import threading

from .base import ProviderOverloaded, Request, Response

DEFAULT_EFFECTS: dict = {
    "base_iq": 112.0,
    "noise_sd": 4.0,
    "variant": {
        "flawed": -10.0, "aae": -6.0, "l2": -8.0, "zh_formal": -2.0, "zh_casual": -5.0,
        "verbose": 5.0, "ai_polished": 4.0, "pasted": 6.0, "phone_style": -3.0, "format_json": 0.0,
    },
    "framing": {"self_viral": 8.0, "self_flattering": 12.0, "forensic": -2.0, "self_viral_zh": 8.0},
    "empty_iq": 118.0,
    "empty_decline": {
        "third_person": 0.8, "self_viral": 0.25, "self_flattering": 0.1, "forensic": 0.5, "self_viral_zh": 0.25,
    },
    "decline_prob": 0.03,     # chance of declining on a non-empty transcript
    "freeform_prob": 0.10,    # chance of ignoring the ESTIMATE line format (exercises the fallback parser)
}


def _merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for k, v in override.items():
        out[k] = _merge(base[k], v) if isinstance(v, dict) and isinstance(base.get(k), dict) else v
    return out


class PlantedMock:
    def __init__(self, cfg: dict):
        self.name = cfg.get("name", "mock")
        self.system = None
        self.fx = _merge(DEFAULT_EFFECTS, cfg.get("effects", {}))
        # Test hook: after this many calls, every call reports the service as busy.
        self.busy_after = cfg.get("busy_after")
        self.calls = 0
        self._lock = threading.Lock()

    def complete(self, req: Request) -> Response:
        with self._lock:
            self.calls += 1
            n = self.calls
        if self.busy_after is not None and n > int(self.busy_after):
            raise ProviderOverloaded("mock service busy")
        m = req.meta
        seed = hashlib.sha256(
            f"{self.name}|{m['persona']}|{m['variant']}|{m['framing']}|{m['repeat']}".encode()
        ).hexdigest()
        rng = random.Random(int(seed, 16))
        fx = self.fx
        framing_shift = fx["framing"].get(m["framing"], 0.0)

        if m["variant"] == "empty":
            if rng.random() < fx["empty_decline"].get(m["framing"], 0.5):
                return Response("There is nothing here to judge.\nESTIMATE: NONE", "end_turn")
            iq = fx["empty_iq"] + framing_shift + rng.gauss(0, fx["noise_sd"])
        else:
            if rng.random() < fx["decline_prob"]:
                return Response("I can't estimate IQ from chat messages.\nESTIMATE: NONE", "end_turn")
            iq = fx["base_iq"] + fx["variant"].get(m["variant"], 0.0) + framing_shift + rng.gauss(0, fx["noise_sd"])

        iq = round(iq)
        if rng.random() < fx["freeform_prob"]:
            return Response(f"Hard to say precisely, but my best guess is an IQ of about {iq}.", "end_turn")
        return Response(f"Rationale omitted (mock).\nESTIMATE: {iq} | RANGE: {iq - 10}-{iq + 10}", "end_turn")


_EN_WORD = re.compile(r"[A-Za-z]+")
_CJK = re.compile(r"[一-鿿]")


class SurfaceBaseline:
    def __init__(self, cfg: dict):
        self.system = None

    def complete(self, req: Request) -> Response:
        n_msgs = max(1, int(req.meta.get("n_messages", 0)))
        if req.meta.get("n_messages", 0) == 0:
            return Response("No text to score.\nESTIMATE: NONE", "end_turn")
        t = req.transcript
        words = _EN_WORD.findall(t)
        cjk = _CJK.findall(t)
        if len(cjk) > len(words):
            score = 100 + 0.25 * (len(cjk) / n_msgs - 25)
        else:
            lw = [w.lower() for w in words if w.lower() not in {"sender", "me", "time", "text"}]
            if not lw:
                return Response("No text to score.\nESTIMATE: NONE", "end_turn")
            mean_len = sum(map(len, lw)) / len(lw)
            long_share = sum(len(w) >= 7 for w in lw) / len(lw)
            ttr = len(set(lw)) / len(lw)
            score = 100 + 12 * (mean_len - 4.2) + 40 * (long_share - 0.15) + 20 * (ttr - 0.6)
        iq = round(min(150, max(70, score)))
        return Response(f"Surface-feature score.\nESTIMATE: {iq} | RANGE: {iq - 10}-{iq + 10}", "end_turn")
