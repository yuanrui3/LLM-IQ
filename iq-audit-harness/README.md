# iqaudit: what moves an LLM's IQ guess?

People paste their chats into chatbots and ask "what's my IQ?". Nobody has checked those numbers against real test scores, so this harness asks a cheaper question first:

> **If the content of a chat log stays the same, what still moves the model's IQ number?**

It feeds a model the same synthetic chats in different guises (dialect, non-native English, Chinese, WeChat slang, padding and jargon, pasted text, AI polish, export format), asks the question in different ways (neutral, the viral first-person prompt, a flattering anchor, a "forensic WAIS-IV" role prompt, in Chinese), and measures how far the estimate moves. A broken-reasoning version of every chat is the yardstick: a rater worth trusting should react more to broken reasoning than to any surface change.

No real person's chats or scores are involved. Everything is synthetic.

## Results so far (2026-11-14)

Free-tier run on 4 synthetic personas, with the contested probes extended to 12 personas on Qwen (2026-11-19). Intervals are small-sample t-intervals over personas. With 12 personas the non-native English (-3.9 [-5.5, -2.4]) and African American English (-3.7 [-5.3, -2.2]) penalties are established for Qwen; effects measured on the original 4 only (paste, the instruction test, framings) remain provisional. Full tables: [`runs/free/report.md`](runs/free/report.md); the reasons behind them: [`runs/free/findings-qwen-reasons.md`](runs/free/findings-qwen-reasons.md).

- **qwen3.7-plus** tracks reasoning first: broken reasoning lowers its IQ guess by 15 points, while surface changes move it far less (PSI 0.19). But every surface effect points the way the research predicted: jargon padding +6, a pasted physics abstract about +11 (credited as the person's own expertise), non-native English -4, African American English -4, phone-style typos -3, formal Chinese about 0. It refused every empty log and pushed back on the flattering prompt instead of inflating.
- **Telling Qwen to ignore surface features** removed the paste bonus, halved the jargon bonus and sharpened the reasoning signal (-23), but left the non-native English penalty unchanged (-4). Qwen stopped mentioning the grammar, yet still scored it lower.
- **gemini-3.5-flash** is running at about 20 free requests a day through a daily scheduled task; its first answers point the same way (base guess about 5 points higher than Qwen's).
- **Text review:** formal and WeChat Chinese reviewed by a native Chinese speaker (5 formal lines rewritten); non-native English checked overall (meaning intact, minor grammar slips); African American English unverified.

## Quick start

Python 3.11 or newer. The offline demo needs nothing else:

```bash
python -m iqaudit list
```

```bash
python -m iqaudit run configs/demo.toml
```

The report lands in `runs/demo/report.md`. The demo runs two offline raters: a mock with known planted biases and a surface-feature baseline that only counts word shapes. Together they show what a biased profile and a presentation-only profile look like.

To audit a real model, install the SDK and check the plan before anything is sent:

```bash
pip install anthropic
```

```bash
python -m iqaudit run configs/pilot.toml --dry-run
```

```bash
python -m iqaudit run configs/pilot.toml
```

Claude credentials come from `ANTHROPIC_API_KEY` or an `ant auth login` profile. The run asks for confirmation before paid calls (skip with `--yes`). It resumes if interrupted: finished calls are skipped and errored ones retried. `configs/full.toml` adds OpenAI, DeepSeek, Qwen, Gemini and Grok through their OpenAI-compatible endpoints (`pip install openai`, set the key variable, a current model id, and `enabled = true`).

### Free tiers: Gemini and Qwen

`configs/free.toml` audits Gemini and Qwen through their OpenAI-compatible endpoints at no cost, if their free-tier settings are right (the comments at the top of the file explain each one):

- **Gemini:** key from Google AI Studio, in a Cloud project *without* billing. Free limits are low (some models ~20 requests a day), so the config paces calls (`rpm`) and can cap calls per run (`max_calls_per_run`).
- **Qwen:** Alibaba Cloud Model Studio, Singapore region, which currently has the new-user free quota (~1M tokens per model, 90 days). Turn on **"Free quota only"** for the model; it is off by default, and without it you are billed once the quota runs out.

```bash
pip install openai
```

```bash
python -m iqaudit models configs/free.toml --filter flash
```

```bash
python -m iqaudit run configs/free.toml
```

`models` lists the model ids each key can use, so you can fix `model = ...` before spending any quota. When a daily or free quota runs out, the run stops that model and says so. Run the same command again after the limit resets; finished calls are skipped, and the calls are ordered so every pass covers each condition once before repeating any.

### Why the numbers moved

```bash
python -m iqaudit rationales runs/free --model qwen
```

Tags every explanation a model wrote (reasoning, vocabulary, language form, pasted material, education, caveats) and writes `rationales-<model>.md` with per-variant rates and the sentence behind each tag, plus a per-reply CSV. Keyword coding is rough, so read the example sentences. `runs/free/findings-qwen-reasons.md` is a worked example.

Run the tests:

```bash
python -m unittest discover -s tests -t .
```

## What gets measured

| Term | Meaning | What a trustworthy rater shows |
|---|---|---|
| Control effect | `base` minus `flawed`: same style, broken reasoning | Clearly positive |
| Probe shift | surface variant minus `base`, same content | About 0 |
| Ratio | \|probe shift\| / control effect | Well below 1 |
| PSI | Mean ratio over the third-person probes | Well below 1 |
| Framing shift | Same chats, different question, vs neutral third person | About 0 |
| Empty log | No messages at all | Declines every time |

Shifts are paired by persona. 95% intervals come from resampling personas and then repeats, so with four personas they are rough. A low PSI shows the model isn't fooled by *these* surface changes; it says nothing about whether its numbers are accurate. Accuracy needs real test scores (see the research report's validation-study section).

## Probes

| Variant | Kind | How it's made |
|---|---|---|
| `base` | reference | Hand-written, standard English, sound reasoning |
| `flawed` | control | Same style as `base`, reasoning errors |
| `aae` | surface | Hand-written African American English guise |
| `l2` | surface | Hand-written non-native English (Chinese-L1 patterns) |
| `zh_formal`, `zh_casual` | surface | Hand-written Chinese: formal written, and WeChat casual |
| `verbose` | surface | Same points, padded with filler and jargon |
| `ai_polished` | surface | Same points, rewritten as polished AI prose |
| `pasted` | surface | `base` plus one pasted technical block (abstract, contract clause, code) |
| `phone_style` | surface | `base` lowercased, no apostrophes, one swapped-letter typo per message |
| `format_json` | surface | `base` rendered as a JSON chat export with timestamps |
| `empty` | empty | No messages |

Framings: `third_person` (reference), `self_viral`, `self_flattering`, `forensic`, `self_viral_zh`. `python -m iqaudit preview --persona trip_dates --variant zh_casual --framing self_viral_zh` prints the exact prompt for any combination.

## Layout

```
configs/        demo (offline), pilot (one Claude model), free (Gemini + Qwen free tiers), full (cross-vendor)
data/personas/  one TOML per persona, 8 hand-written variants each
data/pastes.toml  pasted blocks (original text, not copied from anywhere)
iqaudit/        probes.py, prompts.py, parse.py, runner.py, analyze.py, providers/
runs/<name>/    results.jsonl, prompts.jsonl, run_meta.json, report.md, cells.csv, effects.csv
tests/          parser tests, runner tests (ordering, caps, pacing, quota detection), end-to-end planted-bias recovery
tools/          save-key.ps1 (save an API key from the clipboard without showing it),
                review-page/ (native-speaker review page: template + build script)
```

Other workflow details:

- **Keys** live in your Windows user environment (`tools/save-key.ps1 GEMINI_API_KEY` after copying a key). `iqaudit` reads them even in terminals opened before they were saved. They never go into files.
- **Changed texts are redone automatically:** if a persona's text changes, the next run redoes only the answers whose prompt changed; old answers stay in `results.jsonl` as history.
- **Cells can be limited to some models** with `models = [...]` on a `[[cells]]` block (used for the Qwen-only fix test in `configs/free.toml`).
- **Review page:** `python tools/review-page/build.py` rebuilds it from the persona files; reviewers' answers are stored with the published page, one document per reviewer.

## Before trusting the numbers

- **Native-speaker review.** The `aae`, `l2`, `zh_formal` and `zh_casual` variants are marked `needs-native-review`. Someone who speaks each variety should check that every one reads as natural and carries the same reasoning as `base`. Change `review` to `reviewed` when done. Until then, treat those shifts as provisional: a caricatured guise would exaggerate the bias.
- **More personas.** Four is enough to see large effects, not small ones. Add a TOML file in `data/personas/` with all eight variants; `python -m iqaudit list` flags missing variants and length mismatches.
- **API ≠ app.** The API has no memory, no app system prompt and no account history. The consumer apps can behave differently (the "fresh account" anecdotes came from the apps).
- **Declines matter.** Means use numeric replies only. A model that refuses more often on some variants changes the picture as much as one that shifts its numbers.

## Design choices

- Claude is called through the official `anthropic` SDK; other vendors through the `openai` SDK's OpenAI-compatible endpoint, in a separate module.
- No temperature is sent to any model by default, so repeats measure each model's default sampling. Claude's current API versions reject temperature anyway.
- Refusal fallbacks are not enabled for Claude. A fallback answers with a different model, which would mix two models in one row. Safety refusals are recorded as their own outcome.
- Every prompt ends with the same machine-readable line (`ESTIMATE: 123 | RANGE: 115-130` or `ESTIMATE: NONE`). The parser falls back to "IQ of about 120", ranges, Chinese phrasing and percentiles. Anything else is counted as `unparsed` rather than guessed.
- Never put other people's real chats in `data/`. The harness is built so it never needs them.
