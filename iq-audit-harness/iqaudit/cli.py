"""Command line: python -m iqaudit {list,preview,run,report}"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from .data import AUTHORED_VARIANTS, DATA_DIR, load_pastes, load_personas
from .probes import PROGRAMMATIC, VARIANT_KINDS, VARIANT_LABELS, build_condition
from .prompts import FRAMINGS, build_prompt

ROOT = Path(__file__).resolve().parent.parent
_CJK = re.compile(r"[一-鿿]")


def _size(msgs: tuple[str, ...], zh: bool) -> int:
    text = " ".join(msgs)
    return len(_CJK.findall(text)) if zh else len(text.split())


def cmd_list(args) -> int:
    personas = load_personas(args.data)
    pastes = load_pastes(args.data)
    print("Variants")
    for v, kind in VARIANT_KINDS.items():
        src = "programmatic" if v in PROGRAMMATIC else "authored"
        print(f"  {v:<12} {kind:<11} {src:<13} {VARIANT_LABELS[v]}")
    print("\nFramings")
    for f, spec in FRAMINGS.items():
        print(f"  {f:<16} {spec['label']}")
    print("\nPersonas")
    warnings = 0
    for p in personas.values():
        print(f"  {p.id}: {p.title}  (paste: {p.paste})")
        base = p.variants["base"]
        base_n = len(base.messages)
        base_words = _size(base.messages, False)
        for name in AUTHORED_VARIANTS:
            v = p.variants[name]
            zh = name.startswith("zh_")
            size = _size(v.messages, zh)
            unit = "chars" if zh else "words"
            notes = []
            if len(v.messages) != base_n:
                notes.append(f"{len(v.messages)} messages vs {base_n} in base")
            if not zh and name != "verbose" and not 0.7 <= size / base_words <= 1.4:
                notes.append(f"length {size / base_words:.2f}x base")
            warnings += bool(notes)
            flag = ("  ! " + "; ".join(notes)) if notes else ""
            print(f"    {name:<12} {len(v.messages)} msgs {size:>4} {unit:<5}  review: {v.review}{flag}")
        if p.paste and p.paste not in pastes:
            print(f"    ! paste {p.paste!r} not found in pastes.toml")
            warnings += 1
    print(f"\n{len(personas)} personas, {warnings} warnings.")
    return 0


def cmd_preview(args) -> int:
    personas = load_personas(args.data)
    pastes = load_pastes(args.data)
    persona = None if args.variant == "empty" else personas[args.persona]
    cond = build_condition(persona, args.variant, pastes)
    print(build_prompt(cond, args.framing))
    return 0


def _load_keys(cfg: dict) -> None:
    from .providers.base import load_user_env

    names = {"ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"}
    names |= {m.get("api_key_env", "OPENAI_API_KEY") for m in cfg["models"] if m.get("provider") == "openai_compat"}
    load_user_env(sorted(names))


def cmd_run(args) -> int:
    from .analyze import write_report
    from .runner import load_config, run

    cfg = load_config(args.config)
    _load_keys(cfg)
    out = Path(args.out) if args.out else ROOT / "runs" / cfg["run"]["name"]
    models = args.models.split(",") if args.models else None
    run(cfg, out, yes=args.yes, dry_run=args.dry_run, only_models=models, data_dir=args.data)
    if not args.dry_run and (out / "results.jsonl").exists():
        write_report(out)
    return 0


def cmd_models(args) -> int:
    """List the model ids each OpenAI-compatible endpoint in a config offers, to fill in `model = ...`."""
    import os

    from .runner import load_config

    cfg = load_config(args.config)
    _load_keys(cfg)
    entries = [m for m in cfg["models"] if m.get("provider") == "openai_compat"]
    if not entries:
        print("No openai_compat models in this config.")
        return 0
    try:
        import openai
    except ImportError:
        print("The `openai` package is not installed: pip install openai")
        return 1
    for m in entries:
        name = m.get("name", m.get("model"))
        env = m.get("api_key_env", "OPENAI_API_KEY")
        print(f"{name}  ({m.get('base_url', 'https://api.openai.com/v1')})  configured model: {m.get('model')}")
        key = os.environ.get(env)
        if not key:
            print(f"  {env} is not set\n")
            continue
        try:
            client = openai.OpenAI(api_key=key, base_url=m.get("base_url"), max_retries=1)
            ids = sorted({x.id.removeprefix("models/") for x in client.models.list()})
        except Exception as e:
            print(f"  could not list models: {type(e).__name__}: {' '.join(str(e).split())[:200]}\n")
            continue
        if args.filter:
            ids = [i for i in ids if args.filter.lower() in i.lower()]
        mark = {str(m.get("model"))}
        for i in ids:
            print(f"  {'*' if i in mark else ' '} {i}")
        if m.get("model") not in ids and m.get("model") != "REPLACE_ME":
            print(f"  ! configured model {m.get('model')!r} is not in this list")
        print()
    return 0


def cmd_rationales(args) -> int:
    from .rationales import write_rationales

    framing = None if args.framing == "all" else args.framing
    out = write_rationales(Path(args.run_dir), args.model, framing)
    print(f"Rationale coding: {out}")
    return 0


def cmd_report(args) -> int:
    from .analyze import write_report

    write_report(Path(args.run_dir))
    return 0


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser(prog="iqaudit", description="Audit what moves an LLM's IQ estimate from chat logs.")
    ap.add_argument("--data", type=Path, default=DATA_DIR, help="data folder (personas/, pastes.toml)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list", help="list variants, framings and personas, with authoring checks")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("preview", help="print the exact prompt for one condition")
    p.add_argument("--persona", default="phone_plans")
    p.add_argument("--variant", default="base", choices=sorted(VARIANT_KINDS))
    p.add_argument("--framing", default="third_person", choices=sorted(FRAMINGS))
    p.set_defaults(func=cmd_preview)

    p = sub.add_parser("run", help="run a config, then write the report")
    p.add_argument("config", type=Path)
    p.add_argument("--out", help="output folder (default runs/<run.name>)")
    p.add_argument("--models", help="comma-separated model names from the config to run")
    p.add_argument("--yes", action="store_true", help="skip the cost confirmation for paid models")
    p.add_argument("--dry-run", action="store_true", help="show the plan and token estimate, send nothing")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("models", help="list model ids offered by each OpenAI-compatible endpoint in a config")
    p.add_argument("config", type=Path)
    p.add_argument("--filter", help="only ids containing this text, e.g. flash or qwen")
    p.set_defaults(func=cmd_models)

    p = sub.add_parser("rationales", help="code which reasons a model cites in its explanations")
    p.add_argument("run_dir")
    p.add_argument("--model", required=True, help="model name as it appears in the run")
    p.add_argument("--framing", default="third_person", help="framing to code, or 'all'")
    p.set_defaults(func=cmd_rationales)

    p = sub.add_parser("report", help="rebuild report.md and CSVs from a run folder")
    p.add_argument("run_dir")
    p.set_defaults(func=cmd_report)

    args = ap.parse_args(argv)
    return args.func(args)
