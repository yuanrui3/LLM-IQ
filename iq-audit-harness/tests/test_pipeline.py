"""End-to-end check: run the planted-bias mock through the real runner and analysis,
then confirm the report recovers the effects that were planted."""
import copy
import statistics
import tempfile
import unittest
from pathlib import Path

from iqaudit.analyze import load_rows, summarize_model, write_report
from iqaudit.probes import VARIANT_KINDS
from iqaudit.providers.offline import DEFAULT_EFFECTS
from iqaudit.runner import plan_jobs, run

IRRELEVANT = [v for v, k in VARIANT_KINDS.items() if k == "irrelevant"]

CFG = {
    "run": {"name": "test", "repeats": 10},
    "cells": [
        {"framings": ["third_person"], "variants": ["base", "flawed", *IRRELEVANT, "empty"]},
        {"framings": ["self_viral", "self_flattering", "forensic"], "variants": ["base", "flawed", "empty"]},
        {"framings": ["self_viral_zh"], "variants": ["base", "zh_formal", "zh_casual", "empty"]},
    ],
    "models": [
        {"name": "mock", "provider": "mock"},
        {"name": "surface", "provider": "surface"},
    ],
}


class PipelineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name) / "run"
        run(copy.deepcopy(CFG), cls.out, yes=True, quiet=True)
        cls.rows = load_rows(cls.out)
        cls.mock = summarize_model([r for r in cls.rows if r["model"] == "mock"])
        cls.surface = summarize_model([r for r in cls.rows if r["model"] == "surface"])

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_every_job_ran(self):
        jobs, _ = plan_jobs(copy.deepcopy(CFG))
        self.assertEqual(len(self.rows), len(jobs))
        self.assertFalse([r for r in self.rows if r.get("error")])

    def test_control_effect_recovered(self):
        self.assertAlmostEqual(self.mock["control"].point, -DEFAULT_EFFECTS["variant"]["flawed"], delta=2.0)
        self.assertTrue(self.mock["control"].sig)

    def test_surface_probes_recovered(self):
        ref = [p for p in self.mock["probes"] if p["framing"] == "third_person"]
        self.assertEqual({p["variant"] for p in ref}, set(IRRELEVANT))
        for p in ref:
            planted = DEFAULT_EFFECTS["variant"][p["variant"]]
            self.assertAlmostEqual(p["effect"].point, planted, delta=2.5, msg=p["variant"])

    def test_framing_shifts_recovered(self):
        for fr in self.mock["framings"]:
            planted = DEFAULT_EFFECTS["framing"].get(fr["framing"], 0.0)
            self.assertAlmostEqual(fr["shift"].point, planted, delta=2.5, msg=fr["framing"])

    def test_psi_recovered(self):
        ctrl = -DEFAULT_EFFECTS["variant"]["flawed"]
        expected = statistics.fmean(abs(DEFAULT_EFFECTS["variant"][v]) / ctrl for v in IRRELEVANT)
        self.assertAlmostEqual(self.mock["psi"], expected, delta=0.2)

    def test_empty_log_decline_rates(self):
        for e in self.mock["empty"]:
            expected = 1 - DEFAULT_EFFECTS["empty_decline"][e["framing"]]
            self.assertAlmostEqual(e["gave_number"], expected, delta=0.2, msg=e["framing"])

    def test_surface_baseline_ignores_reasoning(self):
        # It only sees word shapes, so broken reasoning should barely register.
        self.assertLess(abs(self.surface["control"].point), 3.0)
        verbose = next(p for p in self.surface["probes"]
                       if p["variant"] == "verbose" and p["framing"] == "third_person")
        self.assertGreater(verbose["effect"].point, 5.0)

    def test_rerun_resumes_without_new_calls(self):
        before = (self.out / "results.jsonl").read_text(encoding="utf-8").count("\n")
        run(copy.deepcopy(CFG), self.out, yes=True, quiet=True)
        after = (self.out / "results.jsonl").read_text(encoding="utf-8").count("\n")
        self.assertEqual(before, after)

    def test_report_written(self):
        path = write_report(self.out, quiet=True)
        text = path.read_text(encoding="utf-8")
        self.assertIn("## mock", text)
        self.assertIn("## surface", text)
        for name in ("cells.csv", "effects.csv"):
            self.assertTrue((self.out / name).exists())


if __name__ == "__main__":
    unittest.main()
