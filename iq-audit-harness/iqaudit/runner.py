"""Expand a config into jobs, call each rater, and append results to runs/<name>/results.jsonl.

Re-running the same config resumes: finished rows are skipped and rows that errored are retried.
"""
from __future__ import annotations

import json
import re
import sys
import threading
import time
import tomllib
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from . import __version__
from .data import DATA_DIR, data_fingerprint, load_pastes, load_personas
from .parse import parse_estimate
from .probes import Condition, build_condition
from .prompts import FRAMINGS, build_prompt, prompt_sha, render_transcript
from .providers import OFFLINE_PROVIDERS, FatalProviderError, ProviderOverloaded, Request, make_provider


@dataclass(frozen=True)
class Job:
    model: str
    cond: Condition
    framing: str
    repeat: int

    @property
    def key(self) -> str:
        return f"{self.model}|{self.cond.persona}|{self.cond.variant}|{self.framing}|{self.repeat}"


def load_config(path: Path) -> dict:
    with Path(path).open("rb") as f:
        cfg = tomllib.load(f)
    cfg.setdefault("run", {})
    cfg["run"].setdefault("name", Path(path).stem)
    cfg["run"].setdefault("repeats", 3)
    if not cfg.get("cells"):
        raise ValueError("config has no [[cells]]")
    if not cfg.get("models"):
        raise ValueError("config has no [[models]]")
    return cfg


def _persona_ids(wanted, personas: dict, where: str) -> list[str]:
    ids = sorted(personas) if wanted in (None, "all") else list(wanted)
    for pid in ids:
        if pid not in personas:
            raise KeyError(f"{where}: persona {pid!r} not found; available: {sorted(personas)}")
    return ids


def plan_conditions(cfg: dict, data_dir: Path = DATA_DIR) -> tuple[list[tuple[Condition, str, list]], list[str]]:
    """Unique (condition, framing) pairs, each with the rules that ask for it.

    A [[cells]] block may also carry:
      models   = [...]  only these model names run it
      personas = [...]  these personas instead of [run] personas
      repeats  = N      this many repeats instead of the model's or run's default
    Each rule is (allowed model names or None for all, repeats or None for the default).
    """
    personas = load_personas(data_dir)
    pastes = load_pastes(data_dir)
    run_ids = _persona_ids(cfg["run"].get("personas", "all"), personas, "[run]")

    planned: dict[tuple[str, str, str], list] = {}
    used: set[str] = set()
    for n, cell in enumerate(cfg["cells"], 1):
        allowed = set(cell["models"]) if cell.get("models") else None
        reps = int(cell["repeats"]) if cell.get("repeats") else None
        ids = _persona_ids(cell["personas"], personas, f"cell {n}") if cell.get("personas") else run_ids
        for framing in cell["framings"]:
            if framing not in FRAMINGS:
                raise KeyError(f"unknown framing {framing!r}; known: {sorted(FRAMINGS)}")
            for variant in cell["variants"]:
                targets = [None] if variant == "empty" else [personas[p] for p in ids]
                for persona in targets:
                    cond = build_condition(persona, variant, pastes)
                    if persona is not None:
                        used.add(persona.id)
                    k = (cond.persona, cond.variant, framing)
                    planned.setdefault(k, [cond, framing, []])[2].append((allowed, reps))
    return [tuple(v) for v in planned.values()], sorted(used) or run_ids


def plan_jobs(cfg: dict, data_dir: Path = DATA_DIR) -> tuple[list[Job], list[str]]:
    conditions, persona_ids = plan_conditions(cfg, data_dir)
    jobs = []
    for m in active_models(cfg):
        repeats = int(m.get("repeats", cfg["run"]["repeats"]))
        empty_repeats = int(m.get("empty_repeats", cfg["run"].get("empty_repeats", repeats * len(persona_ids))))
        mine: list[tuple[Condition, str, int]] = []
        for cond, framing, rules in conditions:
            ns = [r if r is not None else (empty_repeats if cond.variant == "empty" else repeats)
                  for allowed, r in rules if allowed is None or m["name"] in allowed]
            if ns:
                mine.append((cond, framing, max(ns)))
        # Repeat-major order: a run cut short (daily limits) has covered every condition once
        # before any condition gets a second sample.
        for r in range(max((n for _, _, n in mine), default=0)):
            for cond, framing, n in mine:
                if r < n:
                    jobs.append(Job(m["name"], cond, framing, r))
    return jobs, persona_ids


@dataclass
class Budget:
    """A spending cap for one model, priced from each reply's reported token usage.

    Config keys on a [[models]] entry: budget_usd, budget_since (ISO date; answers before it are not
    counted), price_in_per_m and price_out_per_m (list price in USD per million tokens). Earlier answers in
    the results file count toward the cap, so the limit holds across runs. Stops with a margin so that
    calls already in flight can't push spending past the cap.
    """
    limit: float
    since: str
    price_in: float
    price_out: float
    assumed_reasoning: int = 0   # hidden thinking tokens to assume for old answers that didn't record them
    spent: float = 0.0
    margin: float = 0.05

    @classmethod
    def from_config(cls, mcfg: dict, results: Path, model: str) -> "Budget | None":
        if not mcfg.get("budget_usd"):
            return None
        b = cls(float(mcfg["budget_usd"]), str(mcfg.get("budget_since", "")),
                float(mcfg.get("price_in_per_m", 0)), float(mcfg.get("price_out_per_m", 0)),
                int(mcfg.get("assumed_reasoning_tokens", 0)))
        if b.price_in <= 0 and b.price_out <= 0:
            raise ValueError(f"model {model!r} has budget_usd but no price_in_per_m / price_out_per_m")
        if results.exists():
            with results.open(encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        r = json.loads(line)
                        if r.get("model") == model and not r.get("error") and r.get("ts", "") >= b.since:
                            extra = r.get("extra") or {}
                            hidden = extra.get("reasoning_tokens", b.assumed_reasoning)
                            b.add(r.get("input_tokens"), r.get("output_tokens"), hidden)
        return b

    def add(self, tokens_in: int | None, tokens_out: int | None, reasoning: int | None = 0) -> None:
        """Output price applies to visible and hidden (thinking) output tokens alike."""
        out = (tokens_out or 0) + (reasoning or 0)
        self.spent += ((tokens_in or 0) * self.price_in + out * self.price_out) / 1e6

    def exhausted(self) -> bool:
        return self.spent >= self.limit - self.margin


class RateLimiter:
    """Space request starts at least 60/rpm seconds apart, across all worker threads."""

    def __init__(self, rpm: float | None):
        self.interval = 60.0 / rpm if rpm else 0.0
        self.lock = threading.Lock()
        self.next_at = 0.0

    def wait(self) -> None:
        if not self.interval:
            return
        with self.lock:
            start = max(time.monotonic(), self.next_at)
            self.next_at = start + self.interval
        delay = start - time.monotonic()
        if delay > 0:
            time.sleep(delay)


def active_models(cfg: dict) -> list[dict]:
    models = [m for m in cfg["models"] if m.get("enabled", True)]
    for m in models:
        m.setdefault("name", m.get("model", m.get("provider")))
        if m.get("model") == "REPLACE_ME":
            raise ValueError(f"model {m['name']!r} still has model = \"REPLACE_ME\"; set a real model id or enabled = false")
    names = [m["name"] for m in models]
    if len(names) != len(set(names)):
        raise ValueError(f"duplicate model names: {names}")
    return models


# Visible output per reply, for the dry-run estimate. Raters explain themselves at length:
# qwen3.7-plus averaged ~1,870 output tokens per reply on 2026-11-13.
OUTPUT_TOKENS_GUESS = 1800

_CJK = re.compile(r"[　-鿿＀-￯]")


def _rough_tokens(text: str) -> int:
    cjk = len(_CJK.findall(text))
    return cjk + (len(text) - cjk) // 4


def _read_existing(results: Path) -> tuple[dict[str, str], set[str]]:
    """Latest successful row per key -> its prompt sha; keys whose rows all errored."""
    done: dict[str, str] = {}
    failed: set[str] = set()
    if results.exists():
        with results.open(encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    row = json.loads(line)
                    if row.get("error"):
                        failed.add(row["key"])
                    else:
                        done[row["key"]] = row.get("prompt_sha") or ""
    return done, failed - set(done)


def _read_prompt_shas(path: Path) -> set[str]:
    if not path.exists():
        return set()
    with path.open(encoding="utf-8") as f:
        return {json.loads(line)["sha"] for line in f if line.strip()}


def run(cfg: dict, out_dir: Path, yes: bool = False, dry_run: bool = False,
        only_models: list[str] | None = None, data_dir: Path = DATA_DIR, quiet: bool = False) -> Path:
    def say(*a):
        if not quiet:
            print(*a, flush=True)

    jobs, persona_ids = plan_jobs(cfg, data_dir)
    models = {m["name"]: m for m in active_models(cfg)}
    if only_models:
        unknown = set(only_models) - set(models)
        if unknown:
            raise KeyError(f"--models names not in config: {sorted(unknown)}")
        models = {k: v for k, v in models.items() if k in only_models}
        jobs = [j for j in jobs if j.model in models]

    out_dir = Path(out_dir)
    results_path = out_dir / "results.jsonl"
    prompts_path = out_dir / "prompts.jsonl"
    done, _ = _read_existing(results_path)

    def job_sha(j: Job) -> str:
        return prompt_sha(models[j.model].get("system"), build_prompt(j.cond, j.framing))

    def is_done(j: Job) -> bool:
        # A finished call counts only if its prompt is unchanged: editing a persona's text
        # makes the old answers stale, and they are redone (old rows stay in the file as history).
        return j.key in done and done[j.key] == job_sha(j)

    stale = sum(j.key in done and not is_done(j) for j in jobs)
    todo = [j for j in jobs if not is_done(j)]
    todo_by_model: dict[str, list[Job]] = {}
    for name, m in models.items():
        mj = [j for j in todo if j.model == name]
        cap = m.get("max_calls_per_run")
        todo_by_model[name] = mj[: int(cap)] if cap else mj

    # Plan summary and rough token estimate.
    say(f"Run '{cfg['run']['name']}' -> {out_dir}")
    say(f"  personas: {', '.join(persona_ids)}")
    paid = False
    for name, m in models.items():
        mj = todo_by_model[name]
        remaining = sum(j.model == name for j in todo)
        system = m.get("system")
        in_tok = sum(_rough_tokens(build_prompt(j.cond, j.framing)) + _rough_tokens(system or "") for j in mj)
        offline = m["provider"] in OFFLINE_PROVIDERS
        paid |= bool(mj) and not offline
        capped = f" (capped; {remaining} remain)" if len(mj) < remaining else ""
        say(f"  {name:<28} {m['provider']:<14} {len(mj):>5} calls this run{capped}"
            + ("" if offline else f"  ~{in_tok:,} input tokens, output ~{OUTPUT_TOKENS_GUESS * len(mj):,} tokens plus any thinking"))
    say(f"  already done: {len(jobs) - len(todo)} of {len(jobs)}"
        + (f" ({stale} earlier answers will be redone because their prompt text changed)" if stale else ""))
    if dry_run:
        say("Dry run: nothing sent.")
        return out_dir
    if paid and not yes:
        try:
            answer = input("These calls use your API accounts (billed, or counted against free-tier quota). "
                           "Proceed? [y/N] ").strip().lower()
        except EOFError:
            answer = ""
        if answer not in ("y", "yes"):
            say("Aborted; nothing sent.")
            return out_dir

    out_dir.mkdir(parents=True, exist_ok=True)
    meta_path = out_dir / "run_meta.json"
    meta = {
        "harness_version": __version__,
        "config": cfg,
        "personas": persona_ids,
        "data_fingerprint": data_fingerprint(data_dir),
        "started": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
    }
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    lock = threading.Lock()
    known_shas = _read_prompt_shas(prompts_path)

    def write_row(row: dict, prompt_rec: dict | None) -> None:
        with lock:
            with results_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            if prompt_rec and prompt_rec["sha"] not in known_shas:
                known_shas.add(prompt_rec["sha"])
                with prompts_path.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(prompt_rec, ensure_ascii=False) + "\n")

    for name, mcfg in models.items():
        mj = todo_by_model[name]
        if not mj:
            continue
        try:
            provider = make_provider(mcfg)
        except FatalProviderError as e:
            say(f"  ! skipping {name}: {e}")
            continue
        stop = threading.Event()
        fatal: list[str] = []
        limiter = RateLimiter(mcfg.get("rpm"))
        overload_limit = int(mcfg.get("stop_after_overloads", 0))
        overloads = [0]  # consecutive "service busy" errors, shared by this model's workers
        budget = Budget.from_config(mcfg, results_path, name)
        if budget:
            say(f"  {name}: budget ${budget.limit:.2f} since {budget.since}, ${budget.spent:.2f} spent so far")

        def do(job: Job) -> None:
            if stop.is_set():
                return
            if budget and budget.exhausted():
                with lock:
                    if not stop.is_set():
                        stop.set()
                        fatal.append(f"spending budget reached (${budget.spent:.2f} of ${budget.limit:.2f} "
                                     f"since {budget.since}); raise budget_usd to continue")
                return
            limiter.wait()
            if stop.is_set():
                return
            user = build_prompt(job.cond, job.framing)
            transcript = render_transcript(job.cond, FRAMINGS[job.framing]["lang"])
            sha = prompt_sha(provider.system, user)
            req = Request(user=user, transcript=transcript, meta={
                "persona": job.cond.persona, "variant": job.cond.variant, "framing": job.framing,
                "repeat": job.repeat, "n_messages": len(job.cond.messages),
            })
            row = {
                "key": job.key, "model": name, "persona": job.cond.persona, "variant": job.cond.variant,
                "kind": job.cond.kind, "lang": job.cond.lang, "framing": job.framing, "repeat": job.repeat,
                "prompt_sha": sha, "error": None,
            }
            t0 = time.perf_counter()
            try:
                resp = provider.complete(req)
            except FatalProviderError as e:
                stop.set()
                fatal.append(str(e))
                return
            except Exception as e:  # transient: rate limits after retries, network, 5xx
                row.update(error=f"{type(e).__name__}: {e}", latency_s=round(time.perf_counter() - t0, 2),
                           ts=datetime.now(timezone.utc).isoformat(timespec="seconds"))
                write_row(row, None)
                if isinstance(e, ProviderOverloaded) and overload_limit:
                    with lock:
                        overloads[0] += 1
                        if overloads[0] >= overload_limit and not stop.is_set():
                            stop.set()
                            fatal.append(f"service busy {overloads[0]} times in a row; stopped to save quota, "
                                         "run again later to continue")
                return
            with lock:
                overloads[0] = 0
                if budget:
                    budget.add(resp.input_tokens, resp.output_tokens, (resp.extra or {}).get("reasoning_tokens", 0))
            parsed = parse_estimate(resp.text)
            row.update(
                estimate=parsed.estimate, low=parsed.low, high=parsed.high, declined=parsed.declined,
                parse_method=parsed.method, stop_reason=resp.stop_reason, served_model=resp.served_model,
                input_tokens=resp.input_tokens, output_tokens=resp.output_tokens,
                latency_s=round(time.perf_counter() - t0, 2), extra=resp.extra or None,
                response_text=resp.text, ts=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            )
            write_row(row, {"sha": sha, "system": provider.system, "user": user,
                            "persona": job.cond.persona, "variant": job.cond.variant, "framing": job.framing})

        workers = max(1, int(mcfg.get("concurrency", 4)))
        pace = f", at most {mcfg['rpm']} per minute" if mcfg.get("rpm") else ""
        say(f"  running {name}: {len(mj)} calls, {workers} at a time{pace}")
        finished = 0
        step = max(1, len(mj) // 10)
        with ThreadPoolExecutor(max_workers=workers) as pool:
            for fut in as_completed([pool.submit(do, j) for j in mj]):
                fut.result()
                finished += 1
                if not quiet and not stop.is_set() and (finished % step == 0 or finished == len(mj)):
                    print(f"    {name}: {finished}/{len(mj)}", flush=True)
        if fatal:
            say(f"  ! stopped {name}: {fatal[0]}")
        if budget:
            say(f"  {name}: ${budget.spent:.2f} of ${budget.limit:.2f} budget spent since {budget.since} (list prices)")

    done, still_failed = _read_existing(results_path)
    failed_here = {j.key for j in jobs} & still_failed
    if failed_here:
        say(f"  {len(failed_here)} calls ended in errors; run the same command again to retry them.")
    left = sum(not is_done(j) and j.key not in still_failed for j in jobs)
    if left:
        say(f"  {left} planned calls not done yet; run the same command again (e.g. after a daily limit resets) to continue.")
    return out_dir
