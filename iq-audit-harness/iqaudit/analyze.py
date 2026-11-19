"""Turn results.jsonl into effect estimates, CSVs and a Markdown report.

Core quantities, per model:
  control effect   base - flawed, third-person framing. How much broken reasoning lowers the score.
  probe shift      variant - base, same framing. How much a surface change moves the score.
  ratio            |probe shift| / control effect. Above 1: the surface change mattered more than
                   broken reasoning did.
  PSI              mean ratio over the third-person surface probes ("presentation sensitivity index").

Deltas are paired by persona: each persona contributes one difference of repeat means, and the 95%
interval is a Student t-interval over those differences (n - 1 degrees of freedom). Personas, not
repeats, are the unit of evidence, so intervals narrow only as personas are added.
Only numeric estimates enter the means; declines and unparsed replies are counted separately.
"""
from __future__ import annotations

import csv
import json
import math
import random
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .probes import NO_PERSONA, VARIANT_KINDS, VARIANT_LABELS
from .prompts import FRAMINGS, REFERENCE_FRAMING

CONTROL_MIN = 1.0   # control effects at or below this many IQ points count as "not detected"
BOOTSTRAP_B = 2000


@dataclass
class Effect:
    point: float
    lo: float
    hi: float
    n_personas: int

    @property
    def sig(self) -> bool:
        return self.lo > 0 or self.hi < 0

    def fmt(self) -> str:
        return f"{self.point:+.1f}{'*' if self.sig else ''}"

    def ci(self) -> str:
        if not (math.isfinite(self.lo) and math.isfinite(self.hi)):
            return "n/a (1 persona)"
        return f"[{self.lo:+.1f}, {self.hi:+.1f}]"


def load_rows(run_dir: Path) -> list[dict]:
    """Latest row per job key, preferring successful rows over errored ones."""
    latest: dict[str, dict] = {}
    with (Path(run_dir) / "results.jsonl").open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            prev = latest.get(row["key"])
            if prev is None or not row.get("error") or prev.get("error"):
                latest[row["key"]] = row
    return list(latest.values())


class Cells:
    """Estimates for one model, indexed by (variant, framing) then persona."""

    def __init__(self, rows: list[dict]):
        self.values: dict[tuple[str, str], dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
        self.counts: dict[tuple[str, str], Counter] = defaultdict(Counter)
        for r in rows:
            k = (r["variant"], r["framing"])
            c = self.counts[k]
            if r.get("error"):
                c["error"] += 1
                continue
            c["n"] += 1
            if r.get("stop_reason") == "refusal":
                c["refusal"] += 1
            if r.get("estimate") is not None:
                c["numeric"] += 1
                self.values[k][r["persona"]].append(float(r["estimate"]))
            elif r.get("declined"):
                c["declined"] += 1
            else:
                c["unparsed"] += 1

    def has(self, variant: str, framing: str) -> bool:
        return self.counts.get((variant, framing), Counter())["n"] > 0

    def by_persona(self, variant: str, framing: str) -> dict[str, list[float]]:
        return self.values.get((variant, framing), {})

    def flat(self, variant: str, framing: str) -> list[float]:
        return [x for xs in self.by_persona(variant, framing).values() for x in xs]

    def rate(self, variant: str, framing: str, what: str) -> float | None:
        c = self.counts.get((variant, framing))
        return c[what] / c["n"] if c and c["n"] else None

    def keys(self) -> list[tuple[str, str]]:
        return sorted(self.counts)


# Two-sided 95% Student t critical values, t(0.975, df).
_T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262,
         10: 2.228, 11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110,
         18: 2.101, 19: 2.093, 20: 2.086, 25: 2.060, 30: 2.042, 40: 2.021, 60: 2.000, 120: 1.980}


def t975(df: int) -> float:
    """t(0.975, df), interpolated in 1/df between table rows; 1.96 in the limit."""
    if df in _T975:
        return _T975[df]
    if df > 120:
        return 1.96 + (1.980 - 1.96) * 120 / df
    lo = max(k for k in _T975 if k < df)
    hi = min(k for k in _T975 if k > df)
    w = (1 / df - 1 / hi) / (1 / lo - 1 / hi)
    return _T975[hi] + w * (_T975[lo] - _T975[hi])


def paired_effect(a: dict[str, list[float]], b: dict[str, list[float]], rng: random.Random | None = None,
                  B: int = BOOTSTRAP_B) -> Effect | None:
    """Mean over personas of mean(a) - mean(b), with a small-sample t-interval over personas.

    The persona is the unit: each persona contributes one difference of its repeat means, and the
    interval is mean +/- t(0.975, n-1) * sd / sqrt(n). With few personas a bootstrap over personas is
    too narrow (it was the harness's method until 2026-11-18); the t-interval is honest at n = 4.
    `rng` and `B` are kept for callers but no longer used. One persona gives no interval.
    """
    ps = sorted(p for p in a if p in b and a[p] and b[p])
    if not ps:
        return None
    diffs = [statistics.fmean(a[p]) - statistics.fmean(b[p]) for p in ps]
    point = statistics.fmean(diffs)
    if len(diffs) < 2:
        return Effect(point, -math.inf, math.inf, 1)
    half = t975(len(diffs) - 1) * statistics.stdev(diffs) / math.sqrt(len(diffs))
    return Effect(point, point - half, point + half, len(diffs))


def _pooled_sd(cells: Cells) -> float | None:
    variances = [statistics.variance(xs) for per in cells.values.values() for xs in per.values() if len(xs) >= 2]
    return math.sqrt(statistics.fmean(variances)) if variances else None


def summarize_model(rows: list[dict], seed: int = 12345) -> dict:
    rng = random.Random(seed)
    cells = Cells(rows)
    ref = REFERENCE_FRAMING
    s: dict = {"cells": cells}

    base_vals = cells.flat("base", ref)
    s["base_mean"] = statistics.fmean(base_vals) if base_vals else None
    s["control"] = (paired_effect(cells.by_persona("base", ref), cells.by_persona("flawed", ref), rng)
                    if cells.has("flawed", ref) else None)
    ctrl = s["control"].point if s["control"] else None
    control_ok = ctrl is not None and ctrl > CONTROL_MIN

    probes = []
    framings_present = sorted({f for (_, f) in cells.keys()}, key=lambda f: (f != ref, f))
    for f in framings_present:
        if not cells.has("base", f) and f != ref:
            continue
        for v in [v for v, k in VARIANT_KINDS.items() if k == "irrelevant"]:
            if not cells.has(v, f):
                continue
            eff = paired_effect(cells.by_persona(v, f), cells.by_persona("base", f), rng)
            if eff is None:
                continue
            ratio = abs(eff.point) / ctrl if control_ok else None
            probes.append({"variant": v, "framing": f, "effect": eff, "ratio": ratio,
                           "declined": cells.rate(v, f, "declined"), "n": cells.counts[(v, f)]["n"]})
    s["probes"] = probes

    ref_ratios = [p["ratio"] for p in probes if p["framing"] == ref and p["ratio"] is not None]
    s["psi"] = statistics.fmean(ref_ratios) if ref_ratios else None
    ref_probes = [p for p in probes if p["framing"] == ref]
    s["largest_probe"] = max(ref_probes, key=lambda p: abs(p["effect"].point), default=None)

    # Within-Chinese register contrast (casual WeChat style vs formal written), per framing.
    s["zh_register"] = [
        {"framing": f, "effect": e}
        for f in framings_present
        if cells.has("zh_casual", f) and cells.has("zh_formal", f)
        for e in [paired_effect(cells.by_persona("zh_casual", f), cells.by_persona("zh_formal", f), rng)]
        if e is not None
    ]

    framings = []
    for f in framings_present:
        if f == ref or not cells.has("base", f):
            continue
        shift = paired_effect(cells.by_persona("base", f), cells.by_persona("base", ref), rng)
        ctrl_f = (paired_effect(cells.by_persona("base", f), cells.by_persona("flawed", f), rng)
                  if cells.has("flawed", f) else None)
        framings.append({"framing": f, "shift": shift, "control": ctrl_f,
                         "declined": cells.rate("base", f, "declined")})
    s["framings"] = framings

    empties = []
    for f in framings_present:
        if not cells.has("empty", f):
            continue
        vals = cells.flat("empty", f)
        c = cells.counts[("empty", f)]
        empties.append({"framing": f, "n": c["n"], "numeric": c["numeric"],
                        "gave_number": c["numeric"] / c["n"] if c["n"] else None,
                        "mean": statistics.fmean(vals) if vals else None})
    s["empty"] = empties

    s["noise_sd"] = _pooled_sd(cells)
    total = Counter()
    for c in cells.counts.values():
        total.update(c)
    s["totals"] = total
    return s


def _verdict(s: dict) -> str:
    if s["control"] is None:
        return "No control cell in this run, so presentation effects can't be scaled."
    if s["control"].point <= CONTROL_MIN:
        return ("No detectable response to reasoning quality: broken reasoning did not lower the score. "
                "Any surface shift below is therefore pure presentation effect.")
    psi = s["psi"]
    if psi is None:
        return "Control effect detected, but no third-person surface probes to compare it with."
    if psi > 1:
        return f"Surface changes moved the score more than broken reasoning did (PSI {psi:.2f})."
    if psi > 0.5:
        return f"Surface changes moved the score about as much as broken reasoning did (PSI {psi:.2f})."
    return (f"Reasoning quality moved the score more than surface changes did (PSI {psi:.2f}). "
            "That is necessary for validity, not proof of it.")


def _f(x: float | None, fmt: str = "{:.1f}") -> str:
    return "n/a" if x is None else fmt.format(x)


def _pct(x: float | None) -> str:
    return "n/a" if x is None else f"{100 * x:.0f}%"


def write_report(run_dir: Path, quiet: bool = False) -> Path:
    run_dir = Path(run_dir)
    rows = load_rows(run_dir)
    meta = {}
    if (run_dir / "run_meta.json").exists():
        meta = json.loads((run_dir / "run_meta.json").read_text(encoding="utf-8"))
    by_model: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_model[r["model"]].append(r)
    order = [m["name"] for m in meta.get("config", {}).get("models", []) if m.get("name") in by_model]
    order += sorted(set(by_model) - set(order))
    summaries: dict[str, dict] = {}
    errors_only: dict[str, int] = {}
    for m in order:
        if any(not r.get("error") for r in by_model[m]):
            summaries[m] = summarize_model(by_model[m])
        else:
            errors_only[m] = len(by_model[m])

    _write_csvs(run_dir, summaries)
    md = _render_markdown(run_dir, meta, summaries, errors_only)
    out = run_dir / "report.md"
    out.write_text(md, encoding="utf-8")
    if not quiet:
        print(f"Report: {out}")
    return out


def _write_csvs(run_dir: Path, summaries: dict[str, dict]) -> None:
    with (run_dir / "cells.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["model", "variant", "framing", "n", "numeric", "declined", "unparsed", "refusal", "errors",
                    "mean", "sd"])
        for m, s in summaries.items():
            cells: Cells = s["cells"]
            for v, fr in cells.keys():
                c = cells.counts[(v, fr)]
                vals = cells.flat(v, fr)
                w.writerow([m, v, fr, c["n"], c["numeric"], c["declined"], c["unparsed"], c["refusal"], c["error"],
                            _f(statistics.fmean(vals) if vals else None, "{:.2f}"),
                            _f(statistics.stdev(vals) if len(vals) > 1 else None, "{:.2f}")])
    with (run_dir / "effects.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["model", "contrast", "variant", "framing", "effect", "ci_low", "ci_high", "n_personas",
                    "ratio_to_control"])
        for m, s in summaries.items():
            if s["control"]:
                e = s["control"]
                w.writerow([m, "control(base-flawed)", "flawed", REFERENCE_FRAMING, f"{e.point:.2f}",
                            f"{e.lo:.2f}", f"{e.hi:.2f}", e.n_personas, ""])
            for p in s["probes"]:
                e = p["effect"]
                w.writerow([m, "probe(variant-base)", p["variant"], p["framing"], f"{e.point:.2f}", f"{e.lo:.2f}",
                            f"{e.hi:.2f}", e.n_personas, _f(p["ratio"], "{:.3f}")])
            for fr in s["framings"]:
                if fr["shift"]:
                    e = fr["shift"]
                    w.writerow([m, "framing(base@f-base@ref)", "base", fr["framing"], f"{e.point:.2f}",
                                f"{e.lo:.2f}", f"{e.hi:.2f}", e.n_personas, ""])
            for z in s["zh_register"]:
                e = z["effect"]
                w.writerow([m, "zh_register(casual-formal)", "zh_casual", z["framing"], f"{e.point:.2f}",
                            f"{e.lo:.2f}", f"{e.hi:.2f}", e.n_personas, ""])


def _render_markdown(run_dir: Path, meta: dict, summaries: dict[str, dict],
                     errors_only: dict[str, int] | None = None) -> str:
    cfg = meta.get("config", {})
    run = cfg.get("run", {})
    L: list[str] = []
    L.append(f"# IQ-from-chat audit: {run.get('name', run_dir.name)}")
    L.append("")
    L.append(f"Generated {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC. "
             f"Personas: {', '.join(meta.get('personas', [])) or 'n/a'}. "
             f"Repeats per cell: {run.get('repeats', 'n/a')}. "
             f"Data fingerprint: `{meta.get('data_fingerprint', 'n/a')}`.")
    L.append("")
    L.append("## How to read this")
    L.append("")
    L.append("- Every number is an IQ estimate a model gave for a **synthetic** chat log. Nobody's real IQ is involved.")
    L.append("- **Control effect**: how much lower the model scores the same chats when the reasoning is broken "
             "(`base` minus `flawed`). A rater that tracks thinking should show a clearly positive control effect.")
    L.append("- **Probe shift**: how far the estimate moves when only the surface changes. A valid rater should show about 0.")
    L.append("- **Ratio** = |probe shift| / control effect. Above 1 means that surface change moved the score more than broken reasoning did.")
    L.append("- **PSI** (presentation sensitivity index) = mean ratio across the third-person probes.")
    L.append("- 95% intervals are Student t-intervals over persona-level differences (personas are the unit; "
             "repeats only steady each persona's mean). With few personas they are wide, honestly so. "
             "`*` marks an interval that excludes 0.")
    L.append("- A low PSI shows the model is not fooled by these particular surface changes. It does **not** show its numbers are accurate; that needs real test scores.")
    L.append("")

    L.append("## Summary")
    L.append("")
    L.append("| Model | Base mean IQ | Control effect | PSI | Largest surface shift | First-person shift | Empty log: gave a number |")
    L.append("|---|---|---|---|---|---|---|")
    for m, s in summaries.items():
        lp = s["largest_probe"]
        largest = f"{lp['variant']} {lp['effect'].fmt()}" if lp else "n/a"
        selfv = next((fr for fr in s["framings"] if fr["framing"] == "self_viral"), None)
        self_shift = selfv["shift"].fmt() if selfv and selfv["shift"] else "n/a"
        empty_ref = next((e for e in s["empty"] if e["framing"] == REFERENCE_FRAMING), None)
        empty_any = [e for e in s["empty"]]
        if empty_any:
            gave = sum(e["numeric"] for e in empty_any) / max(1, sum(e["n"] for e in empty_any))
            empty_txt = _pct(gave) + (f" (third person {_pct(empty_ref['gave_number'])})" if empty_ref else "")
        else:
            empty_txt = "n/a"
        L.append(f"| {m} | {_f(s['base_mean'])} | {s['control'].fmt() if s['control'] else 'n/a'} | "
                 f"{_f(s['psi'], '{:.2f}')} | {largest} | {self_shift} | {empty_txt} |")
    L.append("")
    if errors_only:
        L.append("No successful replies yet (left out above): "
                 + ", ".join(f"{m} ({n} errored calls)" for m, n in errors_only.items()) + ".")
        L.append("")

    for m, s in summaries.items():
        L.append(f"## {m}")
        L.append("")
        L.append(f"**Verdict:** {_verdict(s)}")
        L.append("")
        if s["control"]:
            c = s["control"]
            L.append(f"Control effect (base minus flawed, third person): **{c.fmt()}** IQ points, 95% CI {c.ci()}, "
                     f"{c.n_personas} personas. Base mean: {_f(s['base_mean'])}.")
            L.append("")

        ref_probes = [p for p in s["probes"] if p["framing"] == REFERENCE_FRAMING]
        if ref_probes:
            L.append("### Surface probes, third person")
            L.append("")
            L.append("| Probe | What changed | Shift vs base | 95% CI | Ratio to control | Declined | n |")
            L.append("|---|---|---|---|---|---|---|")
            for p in sorted(ref_probes, key=lambda p: -abs(p["effect"].point)):
                e = p["effect"]
                L.append(f"| `{p['variant']}` | {VARIANT_LABELS[p['variant']]} | {e.fmt()} | {e.ci()} | "
                         f"{_f(p['ratio'], '{:.2f}')} | {_pct(p['declined'])} | {p['n']} |")
            L.append("")

        if s["framings"]:
            L.append("### Framing (same chats, different question)")
            L.append("")
            L.append("| Framing | Shift vs third person | 95% CI | Control effect under this framing | Declined |")
            L.append("|---|---|---|---|---|")
            for fr in s["framings"]:
                sh = fr["shift"]
                L.append(f"| {FRAMINGS[fr['framing']]['label']} | {sh.fmt() if sh else 'n/a'} | "
                         f"{sh.ci() if sh else 'n/a'} | {fr['control'].fmt() if fr['control'] else 'n/a'} | "
                         f"{_pct(fr['declined'])} |")
            L.append("")

        other = [p for p in s["probes"] if p["framing"] != REFERENCE_FRAMING]
        if other:
            L.append("### Surface probes under other framings")
            L.append("")
            L.append("| Framing | Probe | Shift vs base (same framing) | 95% CI | Declined |")
            L.append("|---|---|---|---|---|")
            for p in other:
                e = p["effect"]
                L.append(f"| {p['framing']} | `{p['variant']}` | {e.fmt()} | {e.ci()} | {_pct(p['declined'])} |")
            L.append("")

        if s["zh_register"]:
            L.append("### Chinese register (WeChat casual minus formal written)")
            L.append("")
            for z in s["zh_register"]:
                L.append(f"- {z['framing']}: {z['effect'].fmt()} {z['effect'].ci()}")
            L.append("")

        if s["empty"]:
            L.append("### Empty log (no messages at all)")
            L.append("")
            L.append("A valid rater should decline every time.")
            L.append("")
            L.append("| Framing | n | Gave a number | Mean when it did |")
            L.append("|---|---|---|---|")
            for e in s["empty"]:
                L.append(f"| {e['framing']} | {e['n']} | {_pct(e['gave_number'])} | {_f(e['mean'])} |")
            L.append("")

        t = s["totals"]
        L.append("### Data quality")
        L.append("")
        L.append(f"- Replies: {t['n']} ({t['numeric']} numeric, {t['declined']} declined, {t['unparsed']} unparsed, "
                 f"{t['refusal']} safety refusals). Errors still outstanding: {t['error']}.")
        L.append(f"- Run-to-run noise (pooled SD within a persona and cell): {_f(s['noise_sd'])} IQ points.")
        L.append("")

    L.append("## Caveats")
    L.append("")
    L.append("- The personas are synthetic and few. Shifts are specific to these texts until replicated with more personas.")
    L.append("- Variants marked `needs-native-review` (dialect, non-native English, Chinese) were written by the harness "
             "author, not native speakers. Treat their shifts as provisional until a native speaker has checked them.")
    L.append("- API calls are not the consumer apps: no memory, no app system prompt, no account history.")
    L.append("- Means use numeric replies only. If a condition changes how often a model declines, the decline rate "
             "matters as much as the mean.")
    L.append("")
    return "\n".join(L)
