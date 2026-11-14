"""Code the raters' written explanations: which reasons does a model cite for its IQ number?

Each reply is split into sentences and tagged with keyword categories (English and Chinese).
This is deliberately simple and transparent: every tag can be traced to the sentence that
triggered it (see the example quotes and the per-reply CSV). Keyword coding over- and
under-counts; read the examples before trusting a percentage.

Output, per model: rationales-<model>.md (tables + example sentences) and rationales-<model>.csv.
"""
from __future__ import annotations

import csv
import re
import statistics
from collections import defaultdict
from pathlib import Path

from .analyze import load_rows
from .probes import VARIANT_KINDS, VARIANT_LABELS
from .prompts import REFERENCE_FRAMING

CATEGORIES: dict[str, tuple[str, str]] = {
    # name: (description, regex)
    "reasoning": (
        "Cites the reasoning itself: logic, calculations, method, variables, constraints",
        r"\breason|\blogic|systematic|calculat|arithmetic|\bmath|hypothes|variable|methodolog|causal|constraint"
        r"|critical thinking|analytical|推理|逻辑|计算|分析|系统",
    ),
    "reasoning_errors": (
        "Points out mistakes in the reasoning",
        r"\berrors?\b|mistake|incorrect|\bflaw|fallac|miscalcul|post hoc|\bwrong\b|overlook|错误|谬误|算错|漏洞",
    ),
    "vocabulary": (
        "Credits vocabulary, sophistication, articulateness or jargon",
        r"vocabular|sophisticat|articulate|eloquen|jargon|terminolog|lexic|well-written|polished|word choice"
        r"|precise language|词汇|措辞|用词|术语",
    ),
    "language_form": (
        "Comments on grammar, spelling, dialect, non-native English, slang or informality",
        r"grammar|grammatical|typo|spelling|punctuation|capitaliz|non-native|native speaker|second language|\besl\b"
        r"|proficien|language barrier|dialect|\baave\b|african american|vernacular|slang|colloquial|informal"
        r"|abbreviat|语法|错别字|口语|方言|非母语|网络用语|缩写",
    ),
    "pasted_material": (
        "Mentions the pasted block (abstract, contract clause, code)",
        r"pasted|copied|don'?t lose it|sav(ed|es|ing) (it|this|the (text|clause|abstract|code|snippet|legal))"
        r"|majorana|nanowire|conductance|andreev|indemnif|licensee|legal (text|clause|language)|contract clause"
        r"|moving.average|code snippet|python|physics abstract",
    ),
    "education": (
        "Infers education, degree, profession or field",
        r"educat|college|degree|graduate|universit|professional background|engineer|scientist|学历|教育|大学",
    ),
    "caveat": (
        "Says IQ can't really be measured from chat, or hedges heavily",
        r"cannot (be )?(reliably |accurately )?(measure|estimat|determin|assess)|can't (reliably |accurately )?(measure|estimat|determin|assess)"
        r"|not a (reliable|valid)|limited (sample|data|evidence)|speculative|standardized test|formal (iq )?test"
        r"|无法|仅供参考|不能准确|标准化测试",
    ),
}
_COMPILED = {k: re.compile(rx, re.IGNORECASE) for k, (_, rx) in CATEGORIES.items()}
_NEGATION = re.compile(
    r"\bnot\b|n't\b|regardless|independent of|unrelated|irrespective|shouldn't|should not|不代表|无关|不影响|并不", re.IGNORECASE)
_SENT_SPLIT = re.compile(r"(?<=[.!?。！？])\s+|\n+")


def sentences(text: str) -> list[str]:
    return [s.strip(" -*#>\t") for s in _SENT_SPLIT.split(text or "") if len(s.strip()) > 3]


def code_reply(text: str) -> dict:
    """Tags plus the first sentence that triggered each tag, and whether form talk is disclaimed."""
    tags: dict[str, str] = {}
    form_disclaimed = ""
    for s in sentences(text):
        for name, rx in _COMPILED.items():
            if name not in tags and rx.search(s):
                tags[name] = s
        if not form_disclaimed and _COMPILED["language_form"].search(s) and _NEGATION.search(s):
            form_disclaimed = s
    return {"tags": tags, "form_disclaimed": form_disclaimed}


def _pct(n: int, d: int) -> str:
    return f"{100 * n / d:.0f}%" if d else "n/a"


def _clip(s: str, n: int = 220) -> str:
    s = " ".join(s.split())
    return s if len(s) <= n else s[: n - 3] + "..."


def write_rationales(run_dir: Path, model: str, framing: str | None = REFERENCE_FRAMING) -> Path:
    run_dir = Path(run_dir)
    rows = [r for r in load_rows(run_dir) if r["model"] == model and not r.get("error") and r.get("response_text")]
    if framing:
        rows = [r for r in rows if r["framing"] == framing]
    if not rows:
        raise SystemExit(f"no replies for model {model!r}" + (f" under framing {framing!r}" if framing else ""))

    coded = []
    for r in rows:
        c = code_reply(r["response_text"])
        coded.append((r, c))

    by_variant: dict[str, list[tuple[dict, dict]]] = defaultdict(list)
    for r, c in coded:
        by_variant[r["variant"]].append((r, c))
    order = [v for v in VARIANT_KINDS if v in by_variant]
    cats = list(CATEGORIES)

    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", model)
    with (run_dir / f"rationales-{safe}.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["key", "variant", "framing", "persona", "estimate", "declined", *cats, "form_disclaimed"])
        for r, c in coded:
            w.writerow([r["key"], r["variant"], r["framing"], r["persona"], r.get("estimate"), r.get("declined"),
                        *[int(k in c["tags"]) for k in cats], int(bool(c["form_disclaimed"]))])

    L = [f"# Why {model} gave its numbers", ""]
    L.append(f"Replies coded: {len(coded)}" + (f" (framing: {framing})" if framing else " (all framings)") + ". "
             "Each cell is the share of replies with at least one sentence in that category. Keyword coding is rough: "
             "check the example sentences below before relying on a percentage.")
    L.append("")
    L.append("| Category | What it catches |")
    L.append("|---|---|")
    for k, (desc, _) in CATEGORIES.items():
        L.append(f"| `{k}` | {desc} |")
    L.append("")
    L.append("## How often each reason is cited, by variant")
    L.append("")
    L.append("| Variant | n | Mean IQ | " + " | ".join(f"`{k}`" for k in cats) + " | form disclaimed |")
    L.append("|---|---|---|" + "---|" * len(cats) + "---|")
    for v in order:
        items = by_variant[v]
        n = len(items)
        ests = [r["estimate"] for r, _ in items if r.get("estimate") is not None]
        cells = [_pct(sum(k in c["tags"] for _, c in items), n) for k in cats]
        disc = _pct(sum(bool(c["form_disclaimed"]) for _, c in items), n)
        L.append(f"| `{v}` | {n} | {statistics.fmean(ests):.1f} | " + " | ".join(cells) + f" | {disc} |"
                 if ests else f"| `{v}` | {n} | n/a | " + " | ".join(cells) + f" | {disc} |")
    L.append("")

    # Does citing language form go with a lower number, within the same variant?
    L.append("## Within a variant: estimate when language form is mentioned vs not")
    L.append("")
    L.append("| Variant | Mentions form: n, mean | No mention: n, mean | Difference |")
    L.append("|---|---|---|---|")
    for v in order:
        a = [r["estimate"] for r, c in by_variant[v] if r.get("estimate") is not None and "language_form" in c["tags"]]
        b = [r["estimate"] for r, c in by_variant[v] if r.get("estimate") is not None and "language_form" not in c["tags"]]
        if a and b:
            L.append(f"| `{v}` | {len(a)}, {statistics.fmean(a):.1f} | {len(b)}, {statistics.fmean(b):.1f} | "
                     f"{statistics.fmean(a) - statistics.fmean(b):+.1f} |")
    L.append("")

    L.append("## Example sentences")
    L.append("")
    for v in order:
        L.append(f"### `{v}`: {VARIANT_LABELS.get(v, v)}")
        L.append("")
        shown = 0
        for k in ("language_form", "vocabulary", "pasted_material", "education", "reasoning_errors"):
            for r, c in by_variant[v]:
                if k in c["tags"]:
                    L.append(f"- `{k}` ({r['persona']}, IQ {r.get('estimate') or 'declined'}): \"{_clip(c['tags'][k])}\"")
                    shown += 1
                    break
        for r, c in by_variant[v]:
            if c["form_disclaimed"]:
                L.append(f"- form disclaimed ({r['persona']}): \"{_clip(c['form_disclaimed'])}\"")
                break
        if not shown:
            L.append("- (no form, vocabulary, paste, education or error sentences)")
        L.append("")

    out = run_dir / f"rationales-{safe}.md"
    out.write_text("\n".join(L), encoding="utf-8")
    return out
