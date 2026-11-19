# Psychometric measurement theory for LLMs as raters of human traits, and for auditing their fairness (2023-2026)

Scope note: These notes cover rater-effects models, G-theory, DIF and invariance, LLM psychometrics and validity frameworks, and reliability ceilings. PPI, conformal, calibration, causal fairness, concept erasure, sycophancy and text-to-ability prediction are left to other researchers. "Background" marks pre-2023 foundations. Many 2026 items are arXiv preprints that have not been peer reviewed. Where I saw only a search snippet and did not open the paper, the bullet says "(snippet-level)".

Notation used for the audit throughout:
- c = content item (a reasoning passage or scenario whose reasoning is held fixed).
- v = surface variant: SAE baseline, AAE, non-native English, Chinese register, jargon, pasted abstract, framing, broken reasoning.
- m = LLM judge or model version.
- t = prompt template.
- r = repeated call (replicate).
- Y = the IQ estimate.

The user's current results, standardized to an IQ SD of 15:
| Variant (qwen3.7-plus) | Shift | In SD units |
|---|---|---|
| Non-native English | -4 | -0.27 SD |
| Jargon | +6 | +0.40 SD |
| Pasted physics abstract | +11 | +0.73 SD |
| Broken reasoning (the construct-relevant control) | -15 | -1.0 SD |

---

## 1. Many-facet Rasch measurement (MFRM), rater-effects models and hierarchical rater models applied to LLM judges

### Takeaway
Since 2024 a small but growing literature fits many-facet Rasch models to LLM essay scorers. It finds clear LLM severity differences, large shifts in severity across model versions, and mixed evidence on whether LLMs are harsher or more lenient than humans. No paper I found fits a hierarchical rater model (HRM) to LLM judges, although an HRM has been used to combine AES models and it reduced human-machine DIF. For this harness, the audit's surface variant should be a facet, and the judge × variant interaction is the "differential rater functioning" term. An HRM is the right model once several LLM calls rate the same chat, because those calls do not add independent information about the person.

### Cited Findings

**Background models.** These are standard formulations. The linked sources use or describe them; I wrote the formulas from the standard literature.
- **MFRM (Linacre), rating-scale form.**
  - Model: log[P(X_nijk) / P(X_nij(k-1))] = θ_n − δ_i − α_j − τ_k.
  - Terms: θ_n is person ability, δ_i is item or task difficulty, α_j is rater severity, and τ_k is the threshold of category k relative to k−1.
  - Extra facets, such as occasion or condition, enter as more subtracted terms. Rater × facet "bias/interaction" terms test differential rater functioning.
  - Source describing MFRM as the most commonly used IRT model with rater parameters, and its Bayesian extension with severity drift modeled as a Markov process over time: [Bayesian MFRM with Markov modeling for rater severity drift, PMC10615980](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10615980/).
- **Generalized many-facet models for neural automated essay scoring (AES).**
  - These add rater-specific discrimination and thresholds, and have been used to link essay tests with neural AES (Uto and colleagues, *Behavior Research Methods*, 2024) — [Linking essay-writing tests using many-facet models and neural AES, PMC11525454](https://pmc.ncbi.nlm.nih.gov/articles/PMC11525454/).
  - Extended MFRM forms "capable of identifying and accounting for a range of non-uniform rater behaviours" in AES systems — [Cambridge repository: Extended many-facet Rasch models for AES rater effects](https://www.repository.cam.ac.uk/items/db7bc448-f687-4f78-b7d1-e2b71f18a058) (date not checked).
- **Hierarchical rater model (HRM; Patz et al. 2002, background).**
  - Level 1 is a rater model linking the observed rating X_nir to a latent "ideal rating" ξ_ni. Level 2 is an IRT model linking ξ_ni to θ_n.
  - In the Patz et al. form, P(X = k | ξ) ∝ exp{−[k − (ξ + φ_r)]² / (2ψ_r²)}, where φ_r is rater bias (severity) and ψ_r is rater variability (inverse precision).
  - HRM-SDT (DeCarlo, Kim and Johnson 2011, *Journal of Educational Measurement*, background) uses a latent-class signal-detection rater model at level 1. That gives rater precision (discrimination d_r) and criteria c_rk, which capture effects "above and beyond simply severity or leniency" — [DeCarlo, Kim & Johnson 2011 (JEM PDF)](https://www.tc.columbia.edu/faculty/ld208/faculty-profile/files/JEM_11.pdf).

**2024-2026 applications to LLM raters.**
- **ChatGPT-4.0 on 136 ICNALE argumentative essays (MFRM, 2024).** ChatGPT-4.0's severity was comparable to human raters', and it was highly self-consistent — [ScienceDirect, *An application of MFRM to evaluate AES: a case of ChatGPT-4.0*](https://www.sciencedirect.com/science/article/abs/pii/S2772766124000399) (snippet-level).
- **ChatGPT and Claude on 117 Chinese EFL students' essays (MFRM).** The LLM raters were more severe than human raters. The direction of the severity gap therefore depends on the setup — [ResearchGate: ChatGPT and Claude in automated writing scoring, MFRM](https://www.researchgate.net/publication/396131180_Evaluating_the_performance_of_ChatGPT_and_Claude_in_automated_writing_scoring_Insights_from_the_Many-facet_Rasch_model) (snippet-level).
- **Jiao, Song & Lee (arXiv 2505.18486, May 2025).**
  - Compared 10 LLMs with human experts on two writing-task types: GPT-3.5, GPT-4, GPT-4o, o1, Claude 3.5 Sonnet, Gemini 1.5, Gemini 1.5 Pro, Gemini 2.0, DeepSeek V3 and DeepSeek R1.
  - Measures: QWK for accuracy, Cronbach's α across prompts for intra-rater consistency, and MFRM for rater effects.
  - GPT-4o, Gemini 1.5 Pro and Claude 3.5 Sonnet showed high accuracy, better reliability and "fewer rater effects."
  - [arXiv 2505.18486](https://www.arxiv.org/abs/2505.18486v1)
- **Sunkavalli (arXiv 2608.29517, Aug 2026, pre-registered, under review).** This is the most complete "LLM judges as raters" audit found.
  - Scale: 12 judges from 4 providers, 2,377 essays (ENEM/Essay-BR in Portuguese, and ASAP in English), 5 version contrasts.
  - Methods: MFRM severity, residual halo, G-/D-studies, cross-version shifts against permutation nulls, and differential functioning.
  - Severity:
    - Judge severity spans 219 points on ENEM's 0-1000 scale.
    - On ASAP, the spread across the judge panel is 15-33% of the score range, against a gap near 1% between trained humans.
    - All 5 version contrasts shift severity beyond the permutation null, by up to 133 points.
    - One judge was deprecated mid-study and was caught by "identity canaries."
  - Accuracy and reliability:
    - Judge-human correlations fall in a .47-.56 band.
    - Replicate calls give self-consistency (Φ ≥ .80 at k ≤ 2) but not human-level accuracy.
  - Halo: the author's own halo finding was overturned. There was no credible evidence that judge halo exceeds the range seen in trained humans.
  - Two pre-registered hypotheses were not supported: severity-adjusted leaderboard reversals, and "silent drift."
  - [arXiv 2608.29517](https://arxiv.org/abs/2608.29517v1)
- **Xiong, Huggins-Manley & Shin (AIME-Con 2026).** A facets model for severity and centrality of LLM vs human short-answer scoring found that different LLMs show distinct rater effects — [ACL Anthology 2026.aimecon-sessions.17](https://aclanthology.org/2026.aimecon-sessions.17.pdf) (snippet-level; I did not confirm that the PDF matches this description).
- **Fink, Gombert, Liu, Drachsler & Frey (2024), *Zeitschrift für Psychologie*, 232(3), 209-218.**
  - An HRM integrating predictions from several AES models matched the accuracy of the best single model.
  - It also "reduced the amount of differential item functioning" between human and automated scoring, giving higher measurement invariance than any individual AES model.
  - [Open Universiteit record](https://research.ou.nl/en/publications/a-hierarchical-rater-model-approach-for-integrating-automated-ess/)
- **arXiv 2507.03772 (LLM-as-judge autograders).** Notes that hierarchical extensions handle dependencies "enabling more robust inference and better-calibrated uncertainty" — [arXiv 2507.03772](https://arxiv.org/pdf/2507.03772v3) (snippet-level).

### Inferences
- **Facet model for the audit.** Make the LLM output rubric categories, or bin the IQ estimate, and fit:
  - log-odds = θ_c − α_m − λ_v − (αλ)_mv − τ_k.
  - Because c is crossed with v and the reasoning is held fixed, θ_c is the same across variants. λ_v is then a direct logit-scale estimate of construct-irrelevant leniency or severity for each surface form, e.g. λ_jargon < 0 means "more lenient".
  - (αλ)_mv is differential rater functioning: does qwen respond to jargon more than Gemini does?
  - FACETS-style bias/interaction t-statistics or a Bayesian MFRM (brms or Stan) give credible intervals.
- **Severity drift needs a version facet.** Sunkavalli's result that every version change shifted severity (up to 133/1000) means the harness should treat the model version or snapshot as a facet, or as a time-indexed severity as in the Markov-drift MFRM. The harness should also re-run a fixed anchor set (canaries) each time a model or version is re-run. Otherwise a "−4 for non-native English" may not replicate after a silent model update.
- **Central tendency** is the most likely IQ-specific rater effect, i.e. compression toward roughly 100-120. Diagnose it in any of these ways:
  - rater-specific thresholds (partial-credit MFRM: wide middle categories);
  - infit/outfit mean-squares well below 1 (muted ratings);
  - a slope below 1 when the LLM estimate is regressed on a criterion IQ.
  Compression matters for fairness because a fixed 4-point shift is a larger fraction of a compressed between-person SD. Report shifts standardized by the judge's own between-content SD as well as by 15.
- **Halo** becomes testable if the LLM gives analytic sub-ratings, e.g. reasoning validity, abstraction, vocabulary, knowledge. If jargon raises "reasoning validity" as much as "vocabulary", that is a halo or construct-contamination signature. Sunkavalli's reversal shows halo claims need a same-instrument human baseline.
- **Why an HRM fits the harness's repeated calls.** MFRM treats every rating as conditionally independent given θ. So with k repeated LLM calls on the same chat, its SE for the person shrinks like 1/√k without limit. That overstates precision: the calls re-read one fixed piece of evidence.
  - The HRM bounds information about θ_n by the number of distinct responses (chats or episodes), not by the number of ratings.
  - For a chat-based IQ measure, model "LLM calls → ideal rating of each reasoning episode → person θ". In HRM-SDT, the rater-precision parameter d_r becomes a per-model or per-prompt quality metric.

### Gaps
- No paper found that fits an HRM or HRM-SDT specifically to LLM judges. The closest are Fink et al. (2024, AES models, not LLMs) and Sunkavalli (2026, MFRM).
- No MFRM study found where the examinee-side facet is dialect or L1 with content held constant. That is exactly the harness's design, and it looks novel.
- The ChatGPT-4.0 MFRM paper and the ChatGPT/Claude EFL paper were seen only as snippets. Journal names, and whether halo or central tendency were tested, are unverified.
- The AIME-Con 2026 facets study was not opened.

---

## 2. Generalizability theory (G-theory) for LLM evaluations

### Takeaway
G-theory has been applied to LLM scoring since 2025 (AP Chinese writing; LLM judges; multi-provider text measures). Two recurring results:
1. Within-model replicate noise is small next to between-model and between-prompt variance. Self-consistency is high, but agreement across models or with humans is moderate.
2. Only about a third of variance in an LLM text score reflects the text itself (one finance study).

For an IQ-from-chat measure, the decisive coefficient is the absolute-decision Φ, not Eρ², because an IQ claim is norm-referenced on an absolute scale and model severity enters error. The audit's variant facet is what makes construct-irrelevant variance visible. Without it, that variance is absorbed into "true" person variance.

### Cited Findings

**Background formulas (Cronbach; Brennan 2001; standard).**
- One-facet p × r design:
  - Eρ² = σ²_p / (σ²_p + σ²_pr,e / n_r)
  - Φ = σ²_p / (σ²_p + (σ²_r + σ²_pr,e) / n_r)
- A D-study changes the n's to project reliability under other designs.
- The G and Φ coefficients were used this way for LLM vs human raters in Song, Lee & Jiao (below).

**Studies.**
- **Song, Lee & Jiao (arXiv 2507.19980, July 2025).**
  - Setting: AP Chinese Language and Culture free responses (story narration and email response), each scored by 2 trained human raters and 7 AI raters. Each essay got 1 holistic score and 3 analytic scores (task completion, delivery, language use).
  - Results:
    - Human raters were more reliable overall.
    - LLMs were reasonably consistent in some conditions, especially story narration.
    - Composite human + AI scores improved reliability, which supports hybrid scoring.
  - [arXiv 2507.19980](https://arxiv.org/abs/2507.19980) (abstract only; the variance components were not extracted).
- **Sunkavalli (arXiv 2608.29517, 2026).** Its G/D-studies show replicate self-consistency Φ ≥ .80 at k ≤ 2, while judge-human correlations are only .47-.56. Reliability across replicates is not accuracy — [arXiv 2608.29517](https://arxiv.org/abs/2608.29517v1).
- **Boustanifar & Mansouri (arXiv 2609.31013, Sept 2026), "Same Text, Different Numbers".**
  - Setting: 7 LLMs from different providers scored 13 constructs on S&P 500 earnings-call transcripts.
  - Cross-model rank correlations average 0.52.
  - Transcript-level differences shared across providers account for 34% of total score variation.
  - Model choice changes the size, sign and significance of downstream regression coefficients.
  - Averaging across providers stabilizes rankings for most constructs, but "score levels still depend on which models are in the ensemble."
  - [arXiv 2609.31013](https://arxiv.org/abs/2609.31013)
- **Zhu (arXiv 2609.29709, Aug-Sep 2026), "Three Ways Classical Test Theory Can Mislead About LLM Judges".**
  - Core point: "one judge under one prompt supplies no variance component of its own."
  - Evidence (Claude Haiku 4.5 judging 210 short answers against ten-element checklists):
    - KR-20 was 0.5223 on the judge's verdicts and 0.5231 on error-free gold.
    - Bank design alone moved KR-20 from 0.01 to 0.68 at the judge's 4.72% error rate.
    - Φ(λ) sat 0.22-0.38 below the judge's accuracy against gold.
  - Recommendation: claims about the judge need gold labels or a varied scorer facet, and any reliability ratio should be reported alongside the spread of the bank.
  - [arXiv 2609.29709](https://arxiv.org/abs/2609.29709)
- **Choi et al. (arXiv 2602.00521, ICML 2026).** Use the IRT graded response model to diagnose LLM-as-judge reliability in two dimensions: intrinsic consistency under prompt variations, and human alignment — [arXiv 2602.00521](https://arxiv.org/abs/2602.00521) (abstract only; no numbers extracted).
- **Other 2026 preprints (snippet-level, not opened):**
  - A G-study of LLM judges reports the judge main effect as the second-largest variance component, at 16.7% of total variance — [arXiv 2607.08535](https://arxiv.org/pdf/2607.08535).
  - A repeated-trial study reports ICC(2,1) = 0.58-0.77, with 44.7% of score variance from within-judge noise — [arXiv 2606.13685](https://arxiv.org/html/2606.13685v1).

### Inferences
- **G-study for the audit.** Treat the audit as a crossed c × v × m × t × r design. Variance components or fixed effects to estimate:
  - σ²_c: content level, the "signal".
  - β_v (fixed): construct-irrelevant variant main effects. These are the −4, +6 and +11.
  - σ²_cv: content-specific variant effects, i.e. non-uniform bias. Does jargon help weak reasoning more than strong reasoning?
  - σ²_m and σ²_t: judge severity and prompt-template level shifts.
  - σ²_vm and σ²_vt: does the dialect penalty depend on the model, or on the wording "ignore grammar"?
  - σ²_e: replicate noise.

  Fit with crossed random effects, e.g. lme4 or brms: Y ~ variant + (1|content) + (1|content:variant) + (1|model) + (1|template) + (1|model:variant) + ... The harness's "told to ignore grammar" manipulation is a template-facet level, so the effect size of the instruction is a β_t × β_v interaction.
- **G/D-study for a deployed chat-based IQ measure.** Persons p, chats nested in persons (c:p), models m, templates t, replicates r.
  - Relative coefficient:
    Eρ² = σ²_p / [σ²_p + σ²_c:p / n_c + σ²_pm / n_m + σ²_pt / n_t + σ²_cm:p / (n_c·n_m) + … + σ²_e / (n_c·n_m·n_t·n_r)]
  - Φ adds σ²_m / n_m + σ²_t / n_t (and interactions) to the denominator.
  - Model severity, which spanned 219/1000 points in Sunkavalli, only hurts Φ. Φ is the right index for an absolute claim like "IQ 128".
  - Increasing n_r (repeat calls) only shrinks the last term. The ceiling as n_r → ∞ is set by σ²_c:p / n_c, i.e. how many chats per person.
- **Construct-irrelevant variance hides inside person variance.** In observational chat data, dialect, L1 and jargon habits are stable person attributes. Their effect on the LLM score is therefore reliable and becomes part of σ²_p. That inflates Eρ² while lowering validity. Only a design that varies surface form within fixed content (the audit) moves this variance into an estimable facet. Report the audit's β_v next to any reliability coefficient.
- **The 34% figure, read through G-theory.** Taking the finance study's 34% as σ²_text / σ²_total for a single model and single call, Spearman-Brown-like averaging over 7 providers raises the rank stability of the text component. But the level (the main effects of the models) stays ensemble-dependent. For IQ, report the ensemble composition as part of the instrument definition.

### Gaps
- No full variance-component tables were extracted from Song et al. (2025), Sunkavalli (2026) or arXiv 2607.08535. The 16.7% and the ICC figures are snippet-level.
- No G-study found that includes a dialect or surface-form facet for LLM scoring of humans.

---

## 3. Measurement invariance and DIF, and how they map onto "same content, different dialect → different LLM score"

### Takeaway
Classical DIF and invariance methods test whether P(score | latent trait, group) depends on group. They need a matching criterion or anchor items because the trait is latent. The harness's matched-content design fixes the trait by construction, so each variant's effect is a paired, anchor-free estimate of uniform bias. That is the matched-guise logic of Hofmann et al. (2024, *Nature*).

Observational methods are still needed for real chat logs, where content is not matched:
- MNLFA with continuous moderators (degree of non-native features, jargon density, pasted-text fraction);
- regularized DIF to select anchors;
- alignment when there are many L1 groups.

2024-2026 LLM-scoring evidence shows L1-linked score offsets within human-assigned proficiency bands, and an HRM ensemble that reduced human-machine DIF.

### Cited Findings

**Background methods.** These are standard formulations. The linked sources describe or extend them.
- **MGCFA invariance levels (Meredith 1993; Vandenberg & Lance 2000).** For the indicator model x_jg = ν_jg + λ_jg·η + ε_jg:
  - configural: same pattern;
  - metric/weak: λ equal across groups;
  - scalar/strong: ν equal across groups;
  - strict: residual variances equal.
  Comparing latent means across groups requires at least partial scalar invariance.
- **IRT-DIF.** Uniform DIF is a group shift in difficulty b; non-uniform DIF is a group difference in discrimination a.
- **Mantel-Haenszel (Holland & Thayer 1988).**
  - Stratify on a matching score k: α_MH = Σ_k (A_k·D_k / N_k) / Σ_k (B_k·C_k / N_k).
  - ETS delta metric: MH D-DIF = −2.35·ln(α_MH).
  - Polytomous and continuous extensions: Mantel's test, and the standardized mean difference.
- **Logistic or ordinal regression DIF (Swaminathan & Rogers 1990; Zumbo 1999).** Model logit P(Y) = β0 + β1·M + β2·G + β3·(M × G). β2 is uniform DIF and β3 is non-uniform DIF. Effect sizes are ΔR² between nested models.
- **MNLFA (Bauer & Hussong 2009; Bauer 2017).**
  - Measurement parameters become functions of any set of covariates x, continuous or categorical:
    - ν_j(x) = ν_0j + ν_1j′x
    - λ_j(x) = λ_0j + λ_1j′x
    - factor mean α(x) = γ′x
    - factor variance ψ(x) = ψ_0·exp(β′x)
  - **Regularized MNLFA** (Bauer, Belzak & Cole 2020, *Psychological Methods*, 25(6), 673-690) puts a lasso penalty on the DIF parameters (ν_1j, λ_1j). This selects anchors and flags DIF together.
  - A 2024 *JEBS* paper (49(6), 976-1012) gives a penalized EM algorithm that is "faster, more flexible, and more statistically principled", with similar DIF recovery — [EconPapers record, JEBS 2024](https://econpapers.repec.org/RePEc:sae:jedbes:v:49:y:2024:i:6:p:976-1012).
  - A 2025 *Applied Psychological Measurement* paper addresses anchor detection in MNLFA for polytomous items — [PMC12643905](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12643905/).
- **Alignment optimization (Asparouhov & Muthén 2014, *Structural Equation Modeling*, background).** Start from the configural model. Choose group factor means and variances that minimize a total simplicity loss over pairwise group differences in λ and ν, using a component loss f(x) ≈ √(√(x² + ε)). This favors a few large non-invariances plus many near-zero ones, and suits many groups, e.g. many L1s. (Cited via the search above; I did not fetch it.)

**The LLM-specific bias design.**
- **Hofmann, Kalluri, Jurafsky & King (2024), *Nature* 633:147-154.** "Matched guise probing" gives models meaning-matched AAE vs SAE texts and asks for speaker traits.
  - Models assigned AAE users lower-prestige jobs, and were more likely to convict them and to sentence them to death.
  - Larger models were less overtly but more covertly prejudiced. Human-feedback training did not remove the covert bias.
  - [Stanford HAI summary](https://hai.stanford.edu/news/covert-racism-ai-how-language-models-are-reinforcing-outdated-stereotypes); [PMC11374696](https://pmc.ncbi.nlm.nih.gov/articles/PMC11374696/)

**DIF and fairness evidence in LLM and automated essay scoring.**
- **Gayed (arXiv 2607.14605, July 2026).**
  - Model: LoRA-adapted Gemma-3-27B-it, evaluated on all 12,100 TOEFL11 essays (11 L1s, 8 unseen prompts).
  - Accuracy: 77.79% band agreement, QWK 0.702, 99.98% adjacent-band agreement.
  - Bias: within every ETS proficiency band, essays from European-L1 writers scored consistently higher than essays from East-Asian-L1 writers. The author says this is not explained by the fine-tuning data.
  - Method note: the comparison is a stratified, MH-like conditioning on the human band. No formal DIF statistic or CI is reported.
  - [arXiv 2607.14605](https://arxiv.org/abs/2607.14605)
- **Zenodo reproducibility archive, "Scoring-induced differential item functioning in LLM ratings of English learner essays".** Contains the prompts, rubric, code, and frozen Qwen3-8B and Gemma-3-12B-IT scores for 6,482 ELLIPSE essays. Findings were not visible — [Zenodo 24112681](https://zenodo.org/records/24112681).
- **Fink et al. (2024).** An HRM ensemble of AES models reduced human-machine DIF, i.e. gave higher invariance than single models — [OU record](https://research.ou.nl/en/publications/a-hierarchical-rater-model-approach-for-integrating-automated-ess/).
- **2026 predictive-bias paper (*Assessing Writing*).** Notes that differential feature functioning (DFF) in AES "originates from" DIF, which was built for explanatory analysis rather than for predicting scores on new data. It urges caution and develops predictive-bias fairness measures instead — [ScienceDirect S1075293526000541](https://www.sciencedirect.com/science/article/pii/S1075293526000541).
- **Background DFF method.** Differential Feature Functioning in AES (book chapter) — [Emerald](https://www.emerald.com/books/edited-volume/19715/chapter-abstract/104692077/Differential-Feature-Functioning-in-Automated).
- **2023 statewide pre-LLM study.** Used DIF plus propensity-score matching to compare automated scoring of online essays with human scoring of paper essays for English learners. The human-scored paper format tended to favor ELs, and there was no significant EL vs non-EL difference in the online sample — [ScienceDirect S1075293523000272](https://www.sciencedirect.com/science/article/abs/pii/S1075293523000272).
- **BEA 2024 (ACL Anthology).** States the anchor problem: without a set of "unbiased" items, the source of group differences cannot be determined — [2024.bea-1.7](https://aclanthology.org/2024.bea-1.7.pdf).
- **LLM-inferred traits from text.**
  - **Peters & Matz** (GPT inference of Big Five from Facebook posts) found group differences in inferred scores. Correlations with self-reports did not differ significantly by gender. No formal multigroup invariance model — [PMC11211928](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11211928/).
  - **A chatbot-conversation personality study (arXiv 2405.13052).** Accuracy varied only slightly across gender, age, race, education and SES subgroups. This is an accuracy check, not an invariance test — [arXiv 2405.13052](https://www.arxiv.org/pdf/2405.13052) (snippet-level).
  - **A 2025 position paper (arXiv 2507.23009).** Argues measurement invariance via CFA is a necessary condition for comparing LLM and human personality measurements — [arXiv 2507.23009](https://arxiv.org/pdf/2507.23009).

### Inferences
- **Crosswalk from audit to DIF concepts.**

  | Audit element | Measurement concept |
  |---|---|
  | Same reasoning content c | The latent trait is fixed by design; this replaces the matching criterion and anchor items |
  | Variant v vs baseline | Focal vs reference group |
  | Mean paired shift β_v (e.g. −4 for non-native English) | Uniform DIF (an intercept / scalar non-invariance analog) |
  | Dependence of the shift on content level (σ²_cv, or a slope of d_cv on designed ability level) | Non-uniform DIF (a loading / discrimination analog) |
  | Judge × variant interaction | Differential rater functioning |
  | Broken-reasoning control | Construct-relevant sensitivity: what a real ability difference of the manipulated size does to the score |

- **A ratio statistic from the user's numbers.** Define R_v = |β_v| / |β_broken|, the construct-irrelevant shift as a fraction of a construct-relevant one. Using the user's qwen3.7-plus numbers:
  | Variant | R_v |
  |---|---|
  | Non-native English | ≈ 0.27 |
  | Jargon | ≈ 0.40 |
  | Pasted abstract | ≈ 0.73 |

  So pasting an abstract buys about three-quarters as much IQ as breaking the reasoning costs.
- **Testing non-uniform DIF without bias.** Do not regress the shift on the same noisy baseline score, because that creates a regression-to-the-mean artifact. Use the designed ability level of the content, or an independent replicate, as the moderator.
- **Content equivalence is the identifying assumption.** "Holding content constant" across dialect or translation is an assumption, as in cross-cultural test adaptation. If the AAE or non-native rewrite loses a hedge, a quantifier or a step, a true construct difference contaminates β_v. Verify equivalence with blind human judges or back-translation, and report it. The harness's equivalence check is the analog of translation-DIF review.
- **Deployment-time invariance on real chat logs.** With multiple LLM sub-ratings per chat as indicators:
  - fit an MNLFA with moderators such as an L1/dialect classifier probability, a jargon-density score, a pasted-text fraction and the chat language;
  - use the regularized version so anchors are chosen by data, not by assumption;
  - use alignment if the groups are many discrete L1s.

  The audit's controlled β_v estimates then serve as priors or validation targets for the observational DIF estimates.
- **Combining judges may reduce DIF.** Fink et al.'s HRM result suggests that a model-ensemble HRM may reduce variant-dependent bias as well as noise. This is testable in the harness by fitting variant effects on the ensemble score.
- **Applying ETS-style thresholds needs a standardization choice.** If ETS-style DIF or SMD flags are used, standardize β_v by the judge's between-content SD. Use the SD of 15 only if the LLM's estimates actually have that spread.

### Gaps
- No 2024-2026 paper found that applies formal MGCFA or MNLFA invariance testing to LLM-inferred cognitive ability or IQ from text.
- The Zenodo "scoring-induced DIF" manuscript's findings are unknown.
- I did not verify a head-to-head comparison of regularized MNLFA vs alignment published in 2024-2026.
- These were not verified this session and should be checked before citing: the ETS automated-scoring subgroup-flag rule (often cited as |SMD of machine − human| > 0.10 for subgroups, Williamson, Xi & Breyer 2012); the Jodoin-Gierl and Zumbo-Thomas ΔR² cutoffs; and tree-based DIF (Rasch trees).
- A search result said LLM scoring criteria vary more across proficiency groups than human scoring (Qwen, GPT, Gemini on non-native essays). I could not confirm which paper said this, so it is excluded.

---

## 4. "LLM psychometrics" developments 2024-2026: surveys, validity frameworks, IRT with LLMs

### Takeaway
Two framing pieces anchor the field:
- Wallach et al. (ICML 2025) recast GenAI evaluation as social-science measurement: background concept → systematized concept → instrument → measurements, with explicit validity lenses.
- Ye et al. (2025) survey LLM psychometrics, but explicitly exclude LLMs as tools for assessing humans, which is the harness's use case.

IRT with LLMs is active in three directions:
- LLMs as simulated respondents for item calibration (item parameters correlate above 0.8 with human calibrations, but single models have too narrow an ability spread);
- IRT/CAT for efficient LLM benchmarking (Fluid Benchmarking);
- IRT models of LLM judges (GRM, ICML 2026).

ETS authors argue GenAI scoring needs more validity evidence than feature-based NLP scoring.

### Cited Findings
- **Wallach et al., "Position: Evaluating Generative AI Systems Is a Social Science Measurement Challenge" (ICML 2025; PMLR v267; arXiv 2502.00561 and an earlier 2411.10939).**
  - Four-level framework: background concept, systematized concept, measurement instrument(s), and instance-level measurements.
  - Critique: typical ML practice jumps from background concept to instrument with little explicit systematization.
  - The framework offers "a set of lenses" for checking the validity of conceptual and operational work.
  - [PMLR](https://proceedings.mlr.press/v267/wallach25a.html); [arXiv 2411.10939](https://arxiv.org/pdf/2411.10939)
- **Ye, Jin, Xie, Zhang & Song, "Large Language Model Psychometrics: A Systematic Review of Evaluation, Validation, and Enhancement" (arXiv 2505.08245, May 2025, revised March 2026).**
  - Covers reliability across prompt variants, construct validity via factor analysis, measurement invariance and IRT (section 8.6). Cites 400+ references and has a companion "Awesome-LLM-Psychometrics" repository.
  - Scope excludes "using LLMs as tools to assess or profile human respondents."
  - [arXiv 2505.08245](https://arxiv.org/abs/2505.08245)
- **Casabianca, McCaffrey, Johnson, Alper & Zubenko (arXiv 2501.02334, Jan 2025; presented at the 2024 ITC meeting), "Validity Arguments for Constructed Response Scoring Using Generative AI Applications".**
  - Compares the validity evidence needed for human, feature-based NLP and GenAI scoring.
  - GenAI scoring needs more evidence because of lack of transparency and consistency concerns.
  - Suggests combining multiple AI scores ("contributory scoring") when human ratings are unavailable.
  - [arXiv 2501.02334](https://arxiv.org/abs/2501.02334)
- **Liu, Bhandari & Pardos (arXiv 2407.10899, 2024; reportedly in *BJET*), LLM respondents for item calibration.**
  - Six LLMs (GPT-3.5, GPT-4, Llama 2, Llama 3, Gemini-Pro, Command R+) answered College Algebra items. No single LLM matched the human ability distribution, because each has a narrow proficiency spread; an ensemble did better.
  - LLM-calibrated item parameters correlated above 0.8 with human calibrations, e.g. for GPT-3.5.
  - Resampling augmentation raised the Spearman correlation from 0.89 (human only) to 0.93 (augmented).
  - [arXiv 2407.10899](https://arxiv.org/pdf/2407.10899)
- **arXiv 2607.26317 (2026), caveat.** When the simulated examinee population lacks spread, item-difficulty estimates become unreliable, especially for easy items — [arXiv 2607.26317](https://arxiv.org/pdf/2607.26317) (snippet-level).
- **Hofmann et al., "Fluid Language Model Benchmarking" (arXiv 2509.11106, Sept 2025; Ai2/UW/CMU).**
  - Method: a 2PL IRT model fitted on 102 Open LLM Leaderboard models, with Fisher-information adaptive item selection, as in computerized adaptive testing.
  - On MMLU it gave higher validity and lower variance with about 50× fewer items. Mislabeled items in a 100-item evaluation fell from 0.75 to 0.01.
  - Limitation: IRT parameters need re-fitting as models outgrow the calibration sample, which compresses the top of the difficulty range.
  - [arXiv 2509.11106](https://arxiv.org/html/2509.11106v1); [Ai2 blog](https://allenai.org/blog/fluid-benchmarking)
- **Choi et al. (ICML 2026).** An IRT graded response model for LLM-as-judge reliability, covering intrinsic consistency under prompt variation and human alignment — [arXiv 2602.00521](https://arxiv.org/abs/2602.00521).
- **arXiv 2507.23009 (position, 2025).** Argues for AI-specific tests and invariance (CFA) before comparing LLM and human scores — [arXiv 2507.23009](https://arxiv.org/pdf/2507.23009).
- **Standards for Educational and Psychological Testing (AERA/APA/NCME 2014), background.** Validity is the degree to which evidence and theory support score interpretations for proposed uses. Fairness (freedom from construct-irrelevant variance across subgroups) is a validity issue — [testingstandards.net](https://www.testingstandards.net/).

### Inferences
- **Kane's interpretation/use argument applied to chat-IQ (background framework; Kane 2013, *JEM*).** Each inference maps to a method in these notes:

  | Kane inference | What it asks | Method |
  |---|---|---|
  | Scoring | Is the LLM rating of an episode accurate and free of construct-irrelevant variance? | MFRM/HRM rater effects; the audit's β_v; the broken-reasoning sensitivity check |
  | Generalization | Do a few chats generalize to the universe of the person's chats, models and prompts? | G-theory Φ; D-study for n_chats |
  | Extrapolation | Does the score relate to IQ-test performance? | Disattenuated validity against a reliable criterion |
  | Implication / decision | Are the consequences acceptable across dialect and L1 groups? | DIF and invariance; Messick's consequential aspect |

- **Messick's construct-irrelevant variance (CIV) vs construct underrepresentation.**
  - The jargon (+6) and pasted-abstract (+11) effects are CIV, which the Standards treat as a fairness and validity threat.
  - Chat logs that rarely contain hard reasoning risk construct underrepresentation. That argues for an IRT-style design where the content of chats is treated as items of varying difficulty.
- **Wallach's systematization step forces a definitional choice.** Is "IQ from chat" meant to be (a) the person's g, (b) their demonstrated reasoning in the chat, or (c) a prediction of a specific test score? The audit's pasted-abstract case is only "bias" under (a) or (b). Under a pure predictive definition (c), pasting technical text might legitimately correlate with IQ. That is the predictive-vs-explanatory tension the 2026 *Assessing Writing* paper raises about DFF.
- **IRT route to a validated chat measure (inference, not found in the literature).** Treat each substantive reasoning episode in a chat as an item response.
  - The LLM provides (1) a difficulty estimate for the problem attempted and (2) a graded quality rating.
  - Fit a GRM or an explanatory IRT model (difficulty predicted from LLM-extracted features), with an HRM layer for multiple LLM ratings.
  - The person's θ then has a proper SE, and test information shows when a person's chats are too easy to locate them at high θ.
  - LLM-respondent calibration (Liu et al.) and Fluid-style adaptive selection could seed difficulty parameters, subject to the population-spread caveat (2607.26317).
- **Version and provider are part of the instrument definition.** Following Casabianca et al. and Sunkavalli, the instrument is model version × prompt × aggregation rule. Any change triggers re-validation, including the harness's DIF audit.

### Gaps
- I did not extract Wallach et al.'s specific list of validity lenses. It reportedly includes face, content, convergent, discriminant, predictive, hypothesis and consequential validity, but this is unverified here.
- I did not extract Ye et al.'s section 8.6 IRT content.
- No 2024-2026 paper found that builds an IRT/CAT model for estimating human ability from naturalistic LLM chat logs. The episode-as-item design above is my proposal.
- No paper found that adapts a full Kane argument specifically to LLM raters of human cognitive traits. Casabianca et al. come closest, for constructed-response scoring.

---

## 5. Reliability ceilings: attenuation, Spearman-Brown, and noisy criteria

### Takeaway
Observed validity is capped by √(reliability of predictor × reliability of criterion). Short public-domain IQ forms (ICAR16 ω ≈ .77 in one sample) and brief EI ability tests (STEU-B α ≈ .63-.72; STEM-B α ≈ .75-.84) cap observable correlations at roughly .7-.9 even for a perfect chat-based predictor. Spearman-Brown says how many chats or ratings are needed. But G-theory and HRM logic show that averaging repeated LLM calls on the same chat cannot raise reliability beyond the chat-sampling ceiling.

### Cited Findings
- **Correction for attenuation (Spearman 1904, background).**
  - r_xy(observed) = r_true·√(ρ_xx·ρ_yy), so r_true = r_xy / √(ρ_xx·ρ_yy).
  - Maximum observable r = √(ρ_xx·ρ_yy).
  - [Wikipedia: Correction for attenuation](https://en.wikipedia.org/wiki/Correction_for_attenuation)
- **Spearman-Brown prophecy (background).**
  - ρ_k = k·ρ_1 / (1 + (k−1)·ρ_1).
  - Inverted: k = ρ*(1 − ρ_1) / [ρ_1(1 − ρ*)].
  - Assumes parallel (exchangeable) units.
  - [Wikipedia: Spearman-Brown prediction formula](https://en.wikipedia.org/wiki/Spearman%E2%80%93Brown_prediction_formula)
- **ICAR16.**
  - Swedish student sample (N = 428): α = .77, McDonald's ω = .77, with 28.3% variance explained by g — [Lund University student thesis](https://lup.lub.lu.se/student-papers/search/publication/9125503) (a student thesis; low source quality).
  - Young & Keith (2020) supported ICAR16 as a valid brief measure of nonverbal intelligence against the WAIS-IV in 97 students, noting larger replications are needed — [SAGE 10.1177/0734282920943455](https://journals.sagepub.com/doi/pdf/10.1177/0734282920943455).
- **STEU-B and STEM-B (brief EI ability tests), from Yan, Feng, Xu & Li (2019), *Frontiers in Psychology*:**
  | Test | α in prior study | α in Chinese sample (n = 904) |
  |---|---|---|
  | STEU-B | .63 (Allen et al. 2014) | .72 |
  | STEM-B | .84 (Allen et al. 2015) | .75 |

  No test-retest values were reported — [Frontiers 10.3389/fpsyg.2019.01156](https://www.frontiersin.org/articles/10.3389/fpsyg.2019.01156/full).
- **Reliability of LLM judges as raters (empirical inputs for these formulas).**
  - Replicate self-consistency Φ ≥ .80 at k ≤ 2, but judge-human r of .47-.56 — [Sunkavalli, arXiv 2608.29517](https://arxiv.org/abs/2608.29517v1).
  - Only 34% of LLM-score variance is shared across providers at the text level; mean cross-model rank r is .52 — [arXiv 2609.31013](https://arxiv.org/abs/2609.31013).
  - Human + AI composites improved G-coefficients — [arXiv 2507.19980](https://arxiv.org/abs/2507.19980).

### Inferences
These are worked examples using the formulas above. The inputs are illustrative unless sourced.
- **Criterion ceiling, IQ.** If the criterion is ICAR16 (ρ_yy ≈ .77) and the chat measure has ρ_xx = .80, the maximum observable r is √(.77 × .80) ≈ .785. A true correlation of .60 would appear as about .47.
  - Report both observed and disattenuated validities. Prefer a longer criterion battery, or a latent-variable criterion such as a g factor from several tests, so that the ceiling does not mask improvements.
- **Criterion ceiling, EI.** If the criterion is STEU-B (α ≈ .63), even a perfectly reliable predictor cannot show r above √.63 ≈ .79. With ρ_xx = .70 the ceiling is √(.63 × .70) ≈ .66, and a true r of .50 would appear as about .33.
  - Noisy EI criteria make "the LLM can't predict EI" conclusions weak.
  - Also check internal consistency in the user's own sample. STEU α was .42-.48 in some samples (snippet-level; see Gaps).
- **How many chats (Spearman-Brown).** If one chat's score has person-variance share ρ_1 = .30, reaching ρ* = .80 needs k = .8 × .7 / (.3 × .2) ≈ 9.3, i.e. about 10 independent chats. With ρ_1 = .50 it needs 4.
  - These assume chats are parallel. Heterogeneous difficulty violates this; the IRT treatment in section 4 handles it.
- **Repeated calls versus more chats.** Averaging n_r repeated LLM calls on one chat raises reliability only toward the ceiling σ²_p / (σ²_p + σ²_c:p + …). This is the HRM point from section 1, and it is consistent with Sunkavalli's Φ ≥ .80 at k ≤ 2 coexisting with low human agreement. Spend budget on more chats or more distinct models, not more calls.
- **Shrinking the absolute-error terms.** Averaging over models reduces σ²_pm / n_m (rank noise). The model main effects (σ²_m), which affect Φ, shrink only through calibration to a common scale, e.g. linking or equating each model's ratings with MFRM severity estimates. Averaging alone does not remove them, which is consistent with the finance paper's "levels depend on ensemble".
- **Validity ceiling for the bias audit itself.** Reliability of the audit's shift estimates depends on replicates and content items. SE(β_v) ≈ √[(σ²_cv + σ²_e/n_r) / n_c]. Increasing the number of matched content items n_c matters more than increasing replicates when σ²_cv is non-trivial.

### Gaps
- MSCEIT full-scale reliability (.91 from the test manual), the branch reliabilities, and STEU α values of .42-.48 in some samples appeared only in a search summary. I did not verify them against MacCann & Roberts (2008) or Austin (2010).
- Condon & Revelle's (2014) original ICAR16 reliability was not checked.
- No 2023-2026 paper found that computes disattenuated validity ceilings specifically for chat-based or text-based IQ estimation.
- The Spearman-Brown inputs (ρ_1 = .30 and .50) are illustrative, not empirical. A G-study on the user's own multi-chat data is needed to estimate σ²_p, σ²_c:p and the model and template components.
