"""Runner behaviour that matters on free tiers: ordering, per-model repeats, call caps, pacing, quota detection."""
import copy
import json
import tempfile
import time
import unittest
from pathlib import Path

from iqaudit.providers.base import quota_exhausted as _quota_exhausted
from iqaudit.runner import RateLimiter, plan_jobs, run

CFG = {
    "run": {"name": "t", "repeats": 2, "empty_repeats": 2},
    "cells": [{"framings": ["third_person"], "variants": ["base", "flawed", "empty"]}],
    "models": [
        {"name": "capped", "provider": "mock", "max_calls_per_run": 5},
        {"name": "triple", "provider": "mock", "repeats": 3},
    ],
}


class RunnerTest(unittest.TestCase):
    def test_repeat_major_order(self):
        jobs, personas = plan_jobs(copy.deepcopy(CFG))
        capped = [j for j in jobs if j.model == "capped"]
        first_pass = len(personas) * 2 + 1  # base + flawed per persona, plus one empty
        self.assertTrue(all(j.repeat == 0 for j in capped[:first_pass]))
        self.assertTrue(all(j.repeat == 1 for j in capped[first_pass:]))

    def test_per_model_repeats(self):
        jobs, personas = plan_jobs(copy.deepcopy(CFG))
        triple = [j for j in jobs if j.model == "triple"]
        self.assertEqual(len(triple), len(personas) * 2 * 3 + 2)

    def test_cell_limited_to_models(self):
        cfg = copy.deepcopy(CFG)
        cfg["cells"].append({"framings": ["self_viral"], "variants": ["base"], "models": ["triple"]})
        jobs, _ = plan_jobs(cfg)
        self.assertTrue(any(j.model == "triple" and j.framing == "self_viral" for j in jobs))
        self.assertFalse(any(j.model == "capped" and j.framing == "self_viral" for j in jobs))

    def test_cap_then_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "r"
            cfg = {**copy.deepcopy(CFG), "models": [{"name": "capped", "provider": "mock", "max_calls_per_run": 5}]}
            run(copy.deepcopy(cfg), out, yes=True, quiet=True)
            first = [json.loads(line) for line in (out / "results.jsonl").read_text(encoding="utf-8").splitlines()]
            run(copy.deepcopy(cfg), out, yes=True, quiet=True)
            both = [json.loads(line) for line in (out / "results.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(first), 5)
        self.assertEqual(len(both), 10)
        self.assertEqual(len({r["key"] for r in both}), 10)

    def test_changed_prompt_is_redone(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "r"
            cfg = {**copy.deepcopy(CFG), "models": [{"name": "triple", "provider": "mock"}]}
            run(copy.deepcopy(cfg), out, yes=True, quiet=True)
            lines = (out / "results.jsonl").read_text(encoding="utf-8").splitlines()
            # Pretend one answer was produced from different text: it must be redone, the rest kept.
            rows = [json.loads(l) for l in lines]
            rows[0]["prompt_sha"] = "stale"
            (out / "results.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
            run(copy.deepcopy(cfg), out, yes=True, quiet=True)
            after = (out / "results.jsonl").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(after), len(lines) + 1)
        self.assertEqual(json.loads(after[-1])["key"], rows[0]["key"])

    def test_rate_limiter_spacing(self):
        lim = RateLimiter(rpm=600)  # 0.1 s apart
        t0 = time.monotonic()
        for _ in range(4):
            lim.wait()
        self.assertGreaterEqual(time.monotonic() - t0, 0.29)
        self.assertEqual(RateLimiter(None).interval, 0.0)

    def test_quota_markers(self):
        self.assertTrue(_quota_exhausted(
            "Error code: 429 - Quota exceeded ... quotaId: GenerateRequestsPerDayPerProjectPerModel-FreeTier"))
        self.assertTrue(_quota_exhausted("Error code: 403 - AllocationQuota.FreeTierOnly: The free tier of the model has been exhausted."))
        self.assertTrue(_quota_exhausted("Error code: 429 - {'error': {'code': 'insufficient_quota'}}"))
        self.assertFalse(_quota_exhausted(
            "Error code: 429 - Quota exceeded ... quotaId: GenerateRequestsPerMinutePerProjectPerModel-FreeTier"))


if __name__ == "__main__":
    unittest.main()
