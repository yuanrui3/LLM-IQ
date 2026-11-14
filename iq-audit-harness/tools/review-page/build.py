"""Rebuild the native-speaker review page from the persona files.

    python tools/review-page/build.py  ->  tools/review-page/iqaudit-review.html
Published at https://claude.ai/artifact/ACMaa9DLL6eqPkEQABusdG (answers are stored in its `reviews` collection,
one document per reviewer). Republish the built file to the same URL after changing personas.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent))
from iqaudit.data import load_personas  # noqa: E402

VARIANTS = ("zh_formal", "zh_casual", "l2")  # AAE dropped from review 2026-11-14: no reviewer who speaks it
data = [
    {"id": p.id, "title": p.title, "base": list(p.variants["base"].messages),
     "variants": {k: list(p.variants[k].messages) for k in VARIANTS}}
    for p in load_personas().values()
]
blob = json.dumps(data, ensure_ascii=False).replace("</", r"<\/")  # keep "</script>" out of the JSON
html = (HERE / "template.html").read_text(encoding="utf-8").replace("/*__DATA__*/", blob)
out = HERE / "iqaudit-review.html"
out.write_text(html, encoding="utf-8")
print(f"wrote {out} ({len(html):,} chars, {len(data)} personas)")
