# The mathematics of IQ from chat

*Analysis of 2026-11-18. Numbers marked "our data" come from the free-tier audit run (qwen3.7-plus, neutral third-person question, 4 synthetic personas, 3 repeats per cell) and are reproduced by `iq-audit-harness/tools/math_analysis.py`. Everything else is closed-form math under stated assumptions.*

**Bottom line.** Even the best published text-based predictor (r ≈ .75) carries about 0.6 bits of information about a person's IQ and leaves a ±19-point 95% interval. Zero-shot LLM raters are likely far below that. On top of that limit, our data show three structural problems:

- **Coarse outputs.** Qwen answers mostly in round numbers, and repeated runs on the same chat vary by about ±6 points.
- **Offset, not calibrated.** Its scores sit well above 100 for ordinary chats, and they swing about 1 SD on a single piece of evidence. A calibrated estimator would shrink toward 100.
- **Small biases that matter.** Its 4-point penalty for non-native English looks small, but at any realistic selection cutoff it fails the four-fifths adverse-impact rule.

The math also explains why "ignore the grammar" did not remove that penalty, and it points to a cheap fix to test: rewrite into standard grammar first, then score.

## 1. A measurement model for an LLM rater

Let θ be a person's true ability on the IQ scale (population mean 100, SD 15). The person writes chat text T, and an LLM asked question F returns a score S. A useful working model is

> S = μ_F + β·q(T) + Σ_z δ_z·1[z(T) = z] + w·c(T) + ε

- q(T) is the reasoning quality actually expressed in the text.
- z(T) are surface features: dialect, first language, register, typing.
- c(T) are explicit cues the rater may count: vocabulary, pasted material.
- μ_F is a framing offset.
- ε is run-to-run noise.

Each audit variant is an intervention, do(z), that holds q fixed. So each measured shift is a controlled direct effect:

> δ_z = E[S | do(z), q] − E[S | do(base), q]

The broken-reasoning control measures β·Δq. The presentation sensitivity index is

> PSI = mean_z |δ_z| / (β·Δq)

In psychometric terms, each δ_z is a **uniform DIF** effect: the same reasoning gets a different score depending on group-linked form.

For S to be a valid measure of θ, three things must hold. The audit tests only the first:

1. **Invariance:** δ_z ≈ 0 and w ≈ 0.
2. **Relevance:** q(T) carries information about θ, not just about education or topic.
3. **Calibration:** E[θ | S] = S.

Conditions 2 and 3 need people with real test scores. There is also a pathway invariance cannot catch: education and first language change *what* people write about and how carefully, which alters q(T) itself. In the path diagram, θ → q(T) → S is legitimate and education → z(T) → S is what the audit measures, but education → q(T) → S passes every invariance test and is still not ability.

## 2. Our data: noise and resolution

| Quantity (Qwen, third person) | Value |
|---|---|
| Numeric estimates | 342, only **29 distinct values**, **63% multiples of 5** |
| Run-to-run noise (same chat, same prompt) | SD **3.0** points |
| Content differences between personas | SD 4.6 points |
| Variant × persona interaction | SD 1.8 points |
| Share of single-rating variance that is content, not noise | 0.70 |

**Resolution.** The outputs are heaped on round numbers. Rounding to the nearest 5 alone adds about 5/√12 ≈ 1.4 points of noise.

**Run-to-run noise.** Together with sampling variation, one rating of one fixed chat has a run-to-run 95% band of about ±6 points. That is before asking whether the number means anything about the person.

## 3. How big an audit has to be

One persona's estimated shift for a probe (variant minus base, averaged over 3 repeats) has SD **3.5 points**. Its variance is 2·σ²_interaction + 2·σ²_noise / R. The persona count needed for 80% power at α = .05 follows from n = (1.96 + 0.84)²·var / δ².

| Shift to detect | Personas needed (3 repeats) |
|---|---|
| 2 points | ~25 |
| 3 points | ~11 |
| 4 points | ~7 |
| 6 points | ~3 |

**Current power.** With 4 personas the audit reliably detects about 5–6 point shifts. **Correction:** the harness marks the −4 effects as significant, but its bootstrap resamples only four personas and so gives intervals that are too narrow. A small-sample t-interval over the four persona shifts does not exclude zero:

| Probe | Per-persona shifts | 95% t-interval |
|---|---|---|
| Non-native English | +1.3, −5.7, −5.7, −5.3 | −9.3 to +1.7 |
| Non-native, with "ignore surface" | | −9.3 to +0.7 |
| African American English | | −7.7 to 0.0 |
| Phone typos | | −4.6 to −1.3 (holds) |

These should be read as strong leads until there are more personas.

**Update, 12 personas (2026-11-19).** Eight new personas were run on the contested cells (2 repeats). The t-intervals now exclude zero:

| Probe | 12 personas | Original 4 / new 8 |
|---|---|---|
| Non-native English | −3.9 [−5.5, −2.4] | −3.8 / −4.0 |
| African American English | −3.7 [−5.3, −2.2] | −3.8 / −3.7 |

Going from 4 to 12 personas shrank the non-native interval from 11 points wide to 3. That is the effect of adding personas that §3 predicted. The new personas replicate the old estimate almost exactly.

**Personas, not repeats.** Going from 3 to 10 repeats cuts the personas needed for a 3-point shift only from ~11 to ~7. The interaction term sets a floor that only more personas can lower.

**Recommendation:** about 12 personas. That resolves 3-point shifts.

## 4. What calibrated output would look like, and why Qwen's isn't

Assume θ and the information in a chat are jointly normal, and the chat signal has validity r. The best estimate is the conditional mean

> E[θ | signal] = 100 + r·15·z_signal

This has two consequences you can check without any test scores.

**The mean must be 100.** Averaged over a representative population, a calibrated estimator's outputs equal the population mean. Qwen gave **114.5** on our sound-reasoning chats, which show ordinary, careful everyday reasoning. Gemini 3.5 Flash gave about 119. Synthetic personas are not a population sample, so this doesn't prove the offset. But ordinary competence is roughly average by definition, and the viral 130–145 estimates fit the same upward offset.

**The spread must shrink with validity.** Calibrated outputs have SD r·15 across the whole population, which is 7.5 at r = .5. Qwen's outputs across our handful of variants already have SD **7.5**, and one broken-reasoning chat moves them by 15 points (1 SD).

In Bayesian terms, the posterior mean moves by the evidence's reliability λ times the evidence's deviation. A few lines of everyday chat cannot plausibly have λ near 1. Moving a full SD on one flawed message means the rater reports something like a point estimate from the likelihood alone, with no prior and no shrinkage. That is exactly the shape of the "130–145" answers.

**Fix:** shrink toward 100 by the estimated validity, and report the interval rather than the point.

Calibrated predictions look strange to users. At the best published accuracy (R² = .57), they spread with an SD of about 11 rather than 15, and a person whose true IQ is 130 is predicted about 117 on average. Stretching predictions back to SD 15 to look more "IQ-like" makes them less accurate and exaggerates the extremes.

## 5. What a chat-based number is worth

For jointly normal variables, the information a score carries about IQ is I = −½·log₂(1 − r²) bits.

| Validity r | Standard error (IQ pts) | 95% interval | Information about IQ | Variance explained |
|---|---|---|---|---|
| .30 (zero-shot, optimistic) | 14.3 | ±28 | 0.07 bits | 9% |
| .50 | 13.0 | ±25 | 0.21 bits | 25% |
| .75 (best essay model, Wolfram 2025) | 9.9 | ±19 | 0.60 bits | 56% |
| .81 (ICAR-16 vs WAIS-IV, one small study) | 8.8 | ±17 | 0.77 bits | 66% |
| .97 (≈ full WAIS composite reliability) | 3.6 | ±7 | 2.04 bits | 94% |

Even the best published text model tells you less than one bit about IQ, which is less than a coin flip's worth of information. A 16-item test does slightly better than that, and a full battery carries about 2 bits.

**"You're 130+".** Suppose the score sits on the IQ scale with correlation r to true IQ. Then the share of people scored above 130 who really are above 130 (2.3% of people) is:

| r | Scored 130+ who are truly 130+ | Scored 120+ who are truly 120+ |
|---|---|---|
| .30 | 9% | 20% |
| .50 | 18% | 31% |
| .75 | 37% | 50% |
| .90 | 59% | n/a |

At realistic validity, most "130+" verdicts are wrong. The rarer the claim, the worse it gets.

## 6. When a 4-point bias becomes a big deal

The non-native English and dialect penalties have point estimates of about −4 points, which is 0.27 IQ SD. With four personas they were not statistically established; with twelve they are, for Qwen on these texts (§3). Suppose two groups have the same true ability, one group's scores sit 4 points lower, and a cutoff selects people. Then the pass-rate ratio (the four-fifths rule used in US hiring-discrimination practice) is:

| Cutoff passes | Ratio if scores spread like IQ (SD 15) | Ratio if scores spread like Qwen's (SD 7.5) |
|---|---|---|
| top 50% | 0.79 | 0.59 |
| top 30% | 0.71 | 0.48 |
| top 10% | 0.61 | 0.35 |
| top 2.3% | 0.52 | 0.25 |

Every cutoff fails the 0.8 threshold. Two things make it worse than the raw number suggests:

- **Selection magnifies tail differences.** The tighter the cutoff, the larger the gap in pass rates.
- **The rater's own spread is narrower than IQ's.** Against Qwen's output spread, a 4-point shift is half a standard deviation.

This is why the earlier research said never to use such a rater for hiring or admissions. It is now a calculation rather than a principle.

## 7. Why "ignore the grammar" fixed paste and jargon but not non-native English

The fix test changed behavior unevenly:

| Probe | Shift before instruction | Shift with instruction |
|---|---|---|
| Pasted text | +5.8 | +0.7 |
| Jargon | +6.0 | +3.1 |
| Non-native English | −3.8 | −4.3 |

Meanwhile, the share of non-native explanations that mentioned language fell from 100% to 0%.

A mediation reading explains the pattern. Split the rater into what it consciously *weighs* and what it *perceives*:

> S = a + b·q̂ + w·c(T),  where q̂ = q − γ·z

- **Weighed cues.** Paste and vocabulary enter through w·c(T), cues the model names and counts. An instruction about what to weigh can set w to about 0, and it did.
- **Perceived reasoning.** Non-native grammar seems to lower q̂, the model's own perception of how clear and rigorous the reasoning is. That effect travels through the legitimate mediator. "Don't let grammar affect your score" cannot remove it, because the model no longer thinks grammar is affecting the score; it thinks the reasoning is weaker. Hence the silence in the explanations alongside an unchanged number. This is the covert-bias pattern.

This reading is a hypothesis. With 12 personas the penalty itself is now established (§3). Its survival under the instruction, though, has only been tested on the original 4.

**A testable fix: canonicalize, then score.** If the bias runs through how the form is perceived, remove the form before scoring:

1. Rewrite each message into standard grammar with an LLM pass that preserves meaning.
2. Score the rewrite.

Our data make this promising for Qwen, because the `ai_polished` probe shows **no polish bonus (+0.0)**. Standardizing the language should therefore remove the non-native, dialect and typo penalties without adding a bonus of its own.

Two checks are needed:

- **The rewrite must not repair reasoning.** The broken-reasoning control must stay broken after canonicalizing, so its −15 to −23 effect should survive.
- **Not every model may be indifferent to polish.** Re-check the polish probe on each model.

**Cost:** about 24–48 Qwen calls.

**A design caveat that applies to the whole audit.** The dialect, non-native and polished variants were written by an LLM (the harness author). Rewriting can leave artifacts of its own. Recent work on rewrite-based effect estimates (RATE, ICML 2025) compares a rewrite-of-a-rewrite against a single rewrite, so both arms carry the same artifacts. Applying that control here would tell whether any part of a shift comes from "LLM-written" style rather than from dialect.

## 8. More chats don't rescue it

Averaging k chats from the same person raises validity by Spearman–Brown, but only up to a ceiling:

> r_k = r₁·√(k / (1 + (k−1)·ρ₁)),  ceiling r₁ / √ρ₁

Here r₁ is one chat's validity and ρ₁ is how well two chats from the same person agree.

| r₁ | ρ₁ | k = 1 | 5 | 20 | 100 | Ceiling |
|---|---|---|---|---|---|---|
| .30 | .50 | .30 | .39 | .41 | .42 | .42 |
| .30 | .30 | .30 | .45 | .52 | .54 | .55 |
| .50 | .60 | .50 | .61 | .64 | .64 | .65 |

A person's chats share topics, register, mood and task mix, so ρ₁ is substantial. That shared part reflects the person's life as much as their ability, and it caps what more data can buy.

Worse, the biases in §6 are themselves stable traits. A non-native writer is non-native in every chat, and a jargon user pads every message. Their penalty or bonus therefore counts as *reliable person variance*: averaging more chats raises the score's reliability while lowering its validity. No reliability statistic can detect this. Only a design that holds content fixed and varies form, like the audit, can separate the two. This fits the ETH finding that zero-shot personality inference from real ChatGPT histories stayed near chance, while users with many more chats were classified only modestly better.

## 9. Validating with few test scores

| Target | People with test scores needed |
|---|---|
| r ≈ .30, ±.10 | ~322 |
| r ≈ .30, ±.05 | ~1,276 |
| r ≈ .50, ±.05 | ~868 |

**What prediction-powered inference can save.** Prediction-powered inference combines a small tested sample with a large pool of LLM-scored chats. It cuts the tested sample by roughly a factor of 1 − ρ², where ρ is the correlation between the calibrated LLM score and the test score. That means 91% as many people at ρ = .3, 75% at ρ = .5 and 44% at ρ = .75. A weak rater saves little; the cost of a validation study sits in the tested people.

Three caveats from the 2025–26 PPI literature:

- **Small samples can lose.** With few tested people, power-tuned PPI can be worse than using the tests alone. In the Gaussian case it only helps when ρ ≥ 1/√(n − 2).
- **Many chats per person break the standard intervals.** One person contributes many chats, so ordinary PPI intervals are too narrow; a cluster-robust version is needed.
- **The validity coefficient gets no help.** PPI targets population quantities such as means, group gaps and slopes. The validity coefficient r itself can only be estimated from the tested people.

## 10. What the math says to do next

1. **Grow the audit to about 12 personas** so 3-point shifts are resolvable (§3).
2. **Test canonicalize-then-score** on the non-native, dialect and typo probes, with the reasoning control as a guard (§7).
3. **Add broken-reasoning versions of the surface variants** (for example flawed + non-native). This tests *non-uniform* DIF: does the penalty depend on reasoning quality? The current design can only see uniform DIF (§1).
4. **Report calibrated output in any user-facing tool:** shrink toward 100 by the validated r, show the interval from §5, and never a single "130+".
5. **Budget a real validation study** at the sizes in §9, using prediction-powered inference only as a modest saving.

The same algebra applies to EQ, with one extra penalty. Ability-EI tests are themselves noisy (item-total correlations around .18), so the criterion's unreliability lowers the achievable correlation further: r_observed ≤ r_true·√(reliability of the test).
