"""Numbers behind reports/IQ from chat mathematical analysis.md.

    python tools/math_analysis.py            (from iq-audit-harness/)

Part A uses the free-run data (qwen, third-person framing). Part B is closed-form math that needs
no data. Standard library only.
"""
from __future__ import annotations

import math
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path
from statistics import NormalDist

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from iqaudit.analyze import load_rows  # noqa: E402

N = NormalDist()
SD_IQ = 15.0
RUN = Path(__file__).resolve().parent.parent / "runs" / "free"
VARIANTS = ["base", "flawed", "aae", "l2", "zh_formal", "zh_casual", "verbose", "ai_polished",
            "pasted", "phone_style", "format_json"]


def bvn_upper(a: float, b: float, r: float, steps: int = 4000) -> float:
    """P(X > a, Y > b) for standard bivariate normal with correlation r (numerical integral over x)."""
    if abs(r) >= 1:
        return 1 - N.cdf(max(a, b))
    s = math.sqrt(1 - r * r)
    hi = a + 10
    h = (hi - a) / steps
    total = 0.0
    for i in range(steps + 1):
        x = a + i * h
        w = 0.5 if i in (0, steps) else 1.0
        total += w * N.pdf(x) * (1 - N.cdf((b - r * x) / s))
    return total * h


def part_a() -> None:
    rows = [r for r in load_rows(RUN) if r["model"] == "qwen" and not r.get("error")]
    num = [r for r in rows if r.get("estimate") is not None]

    # A1. Output resolution: how often estimates are multiples of 5.
    ests = [r["estimate"] for r in num]
    mult5 = sum(e % 5 == 0 for e in ests) / len(ests)
    print(f"A1 outputs: n={len(ests)}, multiples of 5: {mult5:.0%}, distinct values: {len(set(ests))}")

    # A2. Variance components, third person: score = mu + variant + persona + variant x persona + error.
    F = "third_person"
    cell = defaultdict(list)
    for r in num:
        if r["framing"] == F and r["variant"] in VARIANTS:
            cell[(r["variant"], r["persona"])].append(r["estimate"])
    # Variance components need a full variant x persona table: use personas that have every variant.
    personas = sorted(p for p in {p for _, p in cell} if all((v, p) in cell for v in VARIANTS))
    table = {(v, p): cell[(v, p)] for v in VARIANTS for p in personas}
    within = [st.variance(x) for x in table.values() if len(x) >= 2]
    s2e = st.fmean(within)
    R = st.fmean(len(x) for x in table.values())
    means = {k: st.fmean(v) for k, v in table.items()}
    grand = st.fmean(means.values())
    vm = {v: st.fmean(means[(v, p)] for p in personas) for v in VARIANTS}
    pm = {p: st.fmean(means[(v, p)] for v in VARIANTS) for p in personas}
    resid = [means[(v, p)] - vm[v] - pm[p] + grand for v in VARIANTS for p in personas]
    df = (len(VARIANTS) - 1) * (len(personas) - 1)
    ms_int = sum(x * x for x in resid) / df
    s2vp = max(0.0, ms_int - s2e / R)
    s2p = max(0.0, st.variance(list(pm.values())) - ms_int / len(VARIANTS))
    print(f"A2 variance components (IQ points^2): repeat noise {s2e:.1f} (SD {math.sqrt(s2e):.1f}), "
          f"persona {s2p:.1f} (SD {math.sqrt(s2p):.1f}), variant x persona {s2vp:.1f} (SD {math.sqrt(s2vp):.1f}); "
          f"repeats per cell {R:.1f}")
    icc = s2p / (s2p + s2e) if s2p + s2e else float("nan")
    print(f"   repeat reliability of one rating of a fixed chat (persona variance share): {icc:.2f}")

    # A3. Power: personas needed to detect a probe shift of d points (paired, alpha .05 two-sided, 80% power).
    z = N.inv_cdf(0.975) + N.inv_cdf(0.80)
    var_unit = 2 * s2vp + 2 * s2e / R  # variance of one persona's (variant - base) difference
    print(f"A3 SD of one persona's shift estimate: {math.sqrt(var_unit):.1f} points")
    for d in (2, 3, 4, 6):
        need = math.ceil(z * z * var_unit / (d * d))
        print(f"   to detect a {d}-point shift: ~{need} personas (with {R:.0f} repeats each)")
    for reps in (1, 3, 10):
        v = 2 * s2vp + 2 * s2e / reps
        print(f"   repeats={reps}: personas for a 3-point shift ~{math.ceil(z * z * v / 9)}")

    # A4. Output spread versus what a calibrated estimator could show.
    third = [r["estimate"] for r in num if r["framing"] == F and r["variant"] in VARIANTS]
    s_out = st.stdev(third)
    print(f"A4 SD of all third-person estimates across variants: {s_out:.1f}; "
          f"mean {st.fmean(third):.1f}; mean on sound-reasoning base: {st.fmean(cell_vals(cell, 'base')):.1f}")


def cell_vals(cell, v):
    return [x for (vv, _), xs in cell.items() if vv == v for x in xs]


def part_b() -> None:
    print("\nB1 validity r -> error and information")
    print("   r    SEE   95% half-width   info (bits)   share of variance")
    for r in (0.3, 0.5, 0.6, 0.75, 0.81, 0.9, 0.97):
        see = SD_IQ * math.sqrt(1 - r * r)
        bits = -0.5 * math.log2(1 - r * r)
        print(f"  {r:.2f}  {see:5.1f}   +/-{1.96 * see:5.1f}         {bits:5.2f}         {r * r:.0%}")
    print("   (0.81 = ICAR16 vs WAIS-IV in one small study; 0.97 ~ reliability of a full WAIS composite)")

    print("\nB2 'IQ 130+' claims: P(true IQ > 130 | score > 130), scores on the IQ scale, base rate 2.3%")
    a = 2.0
    for r in (0.3, 0.5, 0.75, 0.9):
        joint = bvn_upper(a, a, r)
        ppv = joint / (1 - N.cdf(a))
        print(f"   r={r:.2f}: {ppv:.0%} of people scored above 130 truly are")
    print("   and 'IQ 120+' (top 9%):")
    a = 4 / 3
    for r in (0.3, 0.5, 0.75):
        joint = bvn_upper(a, a, r)
        print(f"   r={r:.2f}: {joint / (1 - N.cdf(a)):.0%}")

    print("\nB3 a -4 point group shift, same true ability: pass rates and four-fifths ratio")
    for score_sd, label in ((SD_IQ, "scores spread like IQ (SD 15)"), (7.5, "scores spread like Qwen's outputs (SD 7.5)")):
        d = 4 / score_sd
        print(f"   {label}:")
        for top in (0.5, 0.3, 0.1, 0.023):
            c = N.inv_cdf(1 - top)
            pb = 1 - N.cdf(c + d)
            print(f"     cutoff passing top {top:.1%}: group B passes {pb:.1%} -> ratio {pb / top:.2f}"
                  + ("  (fails 4/5 rule)" if pb / top < 0.8 else ""))

    print("\nB4 aggregating k chats (Spearman-Brown): r_k = r1 * sqrt(k / (1 + (k-1) rho1)); ceiling r1/sqrt(rho1)")
    for r1, rho1 in ((0.3, 0.5), (0.3, 0.3), (0.5, 0.6)):
        seq = ", ".join(f"k={k}: {r1 * math.sqrt(k / (1 + (k - 1) * rho1)):.2f}" for k in (1, 5, 20, 100))
        print(f"   r1={r1}, rho1={rho1}: {seq}; ceiling {r1 / math.sqrt(rho1):.2f}")

    print("\nB5 few-label validation: gold-label savings from prediction-powered inference (large unlabeled pool)")
    print("   variance factor vs gold-only ~ 1 - rho^2 (rho = corr(calibrated LLM score, test score))")
    for rho in (0.3, 0.5, 0.75):
        print(f"   rho={rho}: needs {1 - rho * rho:.0%} as many tested people for the same precision")

    print("\nB6 people needed to pin a validity correlation (Fisher z, 95% CI half-width)")
    for r, w in ((0.3, 0.1), (0.3, 0.05), (0.5, 0.05)):
        # half-width in r ~ 1.96 * (1 - r^2) / sqrt(n - 3)
        n = math.ceil((1.96 * (1 - r * r) / w) ** 2 + 3)
        print(f"   r={r}, +/-{w}: n ~ {n}")


if __name__ == "__main__":
    part_a()
    part_b()
