# Inference, calibration and uncertainty when LLM judgments stand in for measurements (few gold labels)

Scope: statistical inference, calibration and uncertainty only (psychometrics/IRT/DIF, fairness/causal and text-to-ability modelling are covered elsewhere). Setting throughout: N people have chat logs rated by an LLM (score f(X), cheap, biased); a small random subset of n people also have a real test score Y (ICAR/WAIS). "Background" marks pre-2023 foundations. Items marked [prior knowledge, not re-fetched] are well-known papers whose details were not re-checked in this session; everything else was checked against an abstract page or search result on 2026-11-18.

## Q1. Prediction-powered inference (PPI) and its successors: estimators, guarantees, and how much they cut the gold-label sample size

### Takeaway
PPI-family estimators give confidence intervals that stay valid however biased the LLM is, because a small random gold-labelled sample estimates and removes the bias. The savings depend on the LLM–label correlation ρ: with power tuning and many unlabelled people, the labelled sample is "worth" about n/(1−ρ²) labels. That is only about 1.2–1.3x at ρ≈0.4–0.5, about 2x at ρ≈0.7, and the gain can turn into a loss in small samples. PPI estimates population quantities such as mean ability, group gaps and regression slopes. It does not estimate any one person's IQ.

### Cited Findings
**Original PPI (Angelopoulos, Bates, Fannjiang, Jordan, Zrnic; Science 2023)** [prior knowledge, not re-fetched] — [arXiv 2301.09633](https://arxiv.org/abs/2301.09633)
- Mean estimator ("rectified" estimator): θ̂_PP = (1/N)Σ_j f(X̃_j) − (1/n)Σ_i (f(X_i) − Y_i). The second term (the "rectifier") estimates the LLM's bias on the labelled set. CI: θ̂_PP ± z_{1−α/2}·sqrt(σ̂²_f/N + σ̂²_{f−Y}/n). Guarantee: asymptotically P(θ* ∈ C) ≥ 1−α for any predictor f. The CI is narrower than the classical one only if Var(f−Y) < Var(Y), so with λ=1 f has to be on the same scale as Y. The same idea extends to convex M-estimation (quantiles, OLS/logistic/GLM coefficients) by rectifying the loss gradient. — [arXiv 2301.09633](https://arxiv.org/abs/2301.09633)
- The labelled and unlabelled data must come from the same distribution (i.i.d.). The paper and the `ppi_py` package also handle certain covariate-shift and label-shift settings. — [ppi_py README](https://github.com/aangelopoulos/ppi_py)

**PPI++ / power tuning (Angelopoulos, Duchi, Zrnic, 2023)**
- PPI++ adds a weight λ on the prediction terms. For the mean: θ̂_λ = (1/n)ΣY_i + λ[(1/N)Σf(X̃_j) − (1/n)Σf(X_i)]. λ=1 recovers PPI and λ=0 recovers classical inference. The variance-minimising plug-in ("power tuning") is λ̂ = Ĉov(Y,f) / ((1+n/N)·V̂ar(f)). The authors report that power tuning is essentially never worse than either classical inference or PPI, and often clearly better. — [arXiv 2311.01453](https://arxiv.org/abs/2311.01453)
- Asymptotically, the power-tuned estimator is at least as precise as the labels-only estimator (the asymptotic "free lunch"). — [Cluster-Robust PPI, arXiv 2610.09601](https://arxiv.org/abs/2610.09601); [arXiv 2311.01453](https://arxiv.org/abs/2311.01453)

**Finite-sample caveat: "No Free Lunch" (Mani, Xu, Lipton, Oberst; arXiv May 2025, revised June 2026)**
- An exact finite-sample analysis of PPI++ for the mean shows that PPI++ can have provably larger error than the gold-only estimator. It beats gold-only if and only if corr(pseudo-label, gold label) exceeds a threshold that depends on n. In the Gaussian case the threshold is ρ ≥ 1/sqrt(n−2): about 0.33 at n=11, 0.15 at n=50 and 0.10 at n=100. The paper also gives exact variance expressions for sample-split PPI++. — [arXiv 2505.20178](https://arxiv.org/abs/2505.20178)

**Cross-prediction-powered inference (Zrnic & Candès, PNAS 2024)** [prior knowledge, not re-fetched]
- Cross-PPI lets you train or recalibrate the predictor on the same few gold labels used for inference. The labelled set is split into K folds; f^(k) is trained without fold k; the estimator is θ̂ = (1/K)Σ_k (1/N)Σ_j f^(k)(X̃_j) − (1/n)Σ_k Σ_{i∈fold k} (f^(k)(X_i) − Y_i). The CI accounts for the dependence across folds. — [arXiv 2309.16598](https://arxiv.org/abs/2309.16598); cross-PPI is implemented in `cross_ppi.py` — [ppi_py](https://github.com/aangelopoulos/ppi_py)

**Recalibrated PPI ("Predictions as Surrogates", Ji, Lei, Zrnic; arXiv Jan 2025)**
- The paper formally links PPI to the classical surrogate-outcome model from biostatistics and economics. It proposes recalibrated PPI, which learns the optimal imputed loss from the predictions, typically by cross-fitting a flexible model. The authors state it always improves on the labelled-only estimator even when the imputed loss is estimated imperfectly, and report large gains in effective sample size over earlier PPI variants in three AI applications. — [arXiv 2501.09731](https://arxiv.org/abs/2501.09731)

**Stratified PPI (Fisch et al., NeurIPS 2024)**
- StratPPI runs PPI within strata and chooses how to allocate labels across them. Its CIs are valid without assumptions on the autorater or the data. It gives substantially tighter CIs than unstratified PPI when the autorater's accuracy differs across segments of the data. — [arXiv 2406.04291](https://arxiv.org/abs/2406.04291); [NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/c9fcd02e6445c7dfbad6986abee53d0d-Abstract.html)

**Active statistical inference (Zrnic & Candès, ICML 2024)** [prior knowledge, not re-fetched]
- Each unit is labelled with a known probability π(X_i), and the estimator is θ̂ = (1/N)Σ_i [f(X_i) + (Y_i − f(X_i))·ξ_i/π(X_i)] with ξ_i ~ Bernoulli(π(X_i)). This is an inverse-probability-weighted rectifier. The variance-optimal π(x) is proportional to sqrt(E[(Y−f)²|X=x]), so labels go where the model is most uncertain, subject to the label budget. — [arXiv 2403.03208](https://arxiv.org/abs/2403.03208)

**Confidence-driven inference (Gligorić, Zrnic, Lee, Candès, Jurafsky; NAACL 2025)**
- Builds on active inference. Human labels are steered to items where the LLM's verbalised confidence is low, and a power-tuning parameter guarantees the result is no worse than human-only. The authors report cutting the human annotations needed by more than 25% on politeness, stance and bias tasks. — [arXiv 2408.15204](https://arxiv.org/abs/2408.15204); [NAACL 2025](https://preview.aclanthology.org/setup/2025.naacl-long.179)

**Cluster-Robust PPI++ (Broska & Howes; arXiv 7 Oct 2026)**
- Standard PPI assumes independent observations. When units are dependent within clusters, especially partially labelled clusters, PPI intervals undercover: in a TV-news application, standard PPI++ intervals covered below 60%. Cluster-Robust PPI++ gives closed-form, cluster-robust standard errors that are asymptotically valid under arbitrary within-cluster dependence, with no bootstrap. It also derives a cluster-aware power-tuning rule and shows how precision depends on the labelling design. — [arXiv 2610.09601](https://arxiv.org/abs/2610.09601)

**Mixed Subjects Design (Broska, Howes, van Loon; Sociological Methods & Research 54(3), 2025)**
- The paper treats LLM outputs as "potentially informative observations" alongside a human gold standard. It extends PPI and adds a power analysis for choosing between costly human subjects and cheap predictions. The R package `mixedsubjects` implements the estimators. — [IDEAS/RePEc](https://ideas.repec.org/a/sae/somere/v54y2025i3p1074-1109.html); [CRAN vignette](https://stat.ethz.ch/CRAN/web/packages/mixedsubjects/vignettes/introduction.html)
- In later commentary the authors note that effective-sample-size gains were only up to about 15%, even with far more LLM-simulated data than human data. — [Statistical Modeling blog, Dec 2025](https://statmodeling.stat.columbia.edu/2025/12/19/validating-language-models-as-study-participants-how-its-being-done-why-it-fails-and-what-works-instead/)

**Distribution shift (2025–2026)**
- Zou, Witten & Williamson (arXiv Feb 2026, listed as "Generalized Prediction-Powered Inference") give PPI estimators for three covariate-shift targets, illustrated with TPR, FPR and AUC. They note that earlier PPI estimators had no general, theoretically justified strategy for covariate shift. Only the search snippet was read. — [arXiv 2602.10332](https://arxiv.org/abs/2602.10332)
- Testa, Xu, Lei & Roeder (arXiv May 2025, revised Mar 2026) give a semiparametric semi-supervised framework for inference under distribution shift and decaying overlap, covering means, quantiles and causal effects. — [arXiv 2505.06452](https://arxiv.org/abs/2505.06452)

**Software**
- `ppi_py` implements PPI, PPI++, cross-PPI, the prediction-powered bootstrap, PPI with imputed covariates and nonuniform sampling, and the mixed-subjects design. It has a notebook for choosing labelled and unlabelled sizes under a budget, and functions named like `ppi_mean_ci` and `ppi_mean_pval` (pattern `ppi_[ESTIMAND]_ci`). — [ppi_py](https://github.com/aangelopoulos/ppi_py)

### Inferences
- **Effective sample size as a function of ρ (derived here from the PPI++ λ formula above).** With optimal λ, Var(θ̂_λ*) = (σ²_Y/n)·[1 − ρ²·N/(n+N)], where ρ = corr(f(X), Y). So n_eff = n / (1 − ρ²·N/(n+N)), which tends to n/(1−ρ²) when N ≫ n. Equivalently, the gold labels needed for a given CI width shrink by a factor (1−ρ²). Gains at N≫n:

  | ρ | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 | 0.9 |
  |---|---|---|---|---|---|---|---|
  | n_eff/n | 1.10 | 1.19 | 1.33 | 1.56 | 1.96 | 2.78 | 5.26 |

  For vanilla PPI (λ=1) the variance is σ²_{Y−f}/n + σ²_f/N, which can be worse than classical if the LLM score is on the wrong scale. LLM "IQ guesses" are typically compressed toward the mean, so power tuning or recalibration is mandatory.
- **ρ here is the correlation with the observed test score, not with latent ability.** Test unreliability lowers it. Classical attenuation (background) gives ρ_obs = ρ_true·sqrt(rel_Y)·sqrt(rel_f), so an unreliable short test, or a single noisy LLM rating, directly cuts PPI's gains. Averaging several LLM ratings or prompts per person raises rel_f.
- **Applying this to "LLM rates chats → estimate ability; few have test scores."**
  - (a) Population mean or quantiles of ability among users. Use PPI++ or cross-PPI on the labelled people plus all rated users.
  - (b) Group gaps, e.g. native vs non-native writers. Fit OLS of Y on a group indicator with the PPI++ rectified gradient. Comparing this PPI estimate of the true gap with the raw LLM-score gap measures how much of the LLM gap is bias. This connects the audit harness to ground truth.
  - (c) Stratified PPI by dialect or L1 group, chat length and topic is natural, because the audit harness already suggests the LLM's error differs by stratum.
  - (d) If test-takers are recruited after their chats are rated, active or confidence-driven sampling can invite people whose ratings are most uncertain (high inter-model or inter-prompt disagreement) more often. This only works if the inclusion probabilities π are recorded and are bounded away from 0.
  - (e) If the unit of analysis is the chat rather than the person, or people are nested in sites or panels, use Cluster-Robust PPI++. Otherwise aggregate to one score per person first.
- **The validity coefficient corr(LLM score, test score) itself gains nothing from PPI.** It involves f and Y jointly, so only the n labelled people inform it. Report it with an ordinary CI, such as a Fisher-z interval or bootstrap.
- **The key assumption that can fail is that the labelled people are a random subsample of the rated people** (or are sampled with known probabilities). Volunteers who agree to take ICAR are self-selected, so the shift needs to be modelled with the 2025–26 covariate-shift methods above or by design.

### Gaps
- No PPI paper was found that targets a correlation or reliability coefficient as the estimand. The general M-estimation and PPI++ machinery could in principle be applied (e.g., to the regression slope of Y on a covariate), but no verified source does this for correlations.
- Not read in full this session: "Prediction-Powered Semi-Supervised Learning with Online Power Tuning" ([arXiv 2510.22586](https://arxiv.org/abs/2510.22586)); "From Narratives to Numbers", an applied PPI with language-model predictions on verbal-autopsy free text ([arXiv 2404.02438](https://arxiv.org/abs/2404.02438)); multi-source PPI (arXiv 2606.21232) and transportable inference (arXiv 2603.02474), which were seen only as references; and Bayesian PPI. Their content is unverified.
- The exact finite-sample formulas in "No Free Lunch" beyond the 1/sqrt(n−2) Gaussian threshold were not extracted.

## Q2. Conformal prediction for regression and LLM outputs: producing an "IQ range with 90% coverage"

### Takeaway
Split conformal, conformalized quantile regression (CQR) and their group-conditional variants turn any chat-based score into per-person intervals with finite-sample, distribution-free marginal coverage. The only assumption is exchangeability between the calibration people and new people, and no model of the LLM's errors is needed. With a few dozen to a few hundred gold-labelled people the coverage guarantee holds, but the intervals will be wide and their realised coverage noisy. Per-group coverage (native vs non-native) requires a separate calibration budget for each group. Very recent work (EMNLP 2025) applies conformal methods directly to LLM-judge ratings.

### Cited Findings
**Foundations (background)** [prior knowledge, not re-fetched]
- Split conformal regression (Lei et al., JASA 2018). Fit a predictor m on one split, compute calibration residuals R_i = |Y_i − m(X_i)| on n_cal held-out people, and set q̂ = the ⌈(n_cal+1)(1−α)⌉-th smallest R_i. The interval is C(x) = [m(x) − q̂, m(x) + q̂]. Guarantee: 1−α ≤ P(Y_new ∈ C(X_new)) ≤ 1−α + 1/(n_cal+1) (upper bound if there are no ties), marginal over the calibration and test draws. — [arXiv 1604.04173](https://arxiv.org/abs/1604.04173); [Angelopoulos & Bates, gentle intro](https://arxiv.org/abs/2107.07511)
- Conditional on a fixed calibration set, coverage is random, distributed Beta(n_cal+1−l, l) with l = ⌊(n_cal+1)α⌋. This is the basis for choosing n_cal. — [Angelopoulos & Bates](https://arxiv.org/abs/2107.07511)
- CQR (Romano, Patterson, Candès, NeurIPS 2019). Fit lower and upper quantile regressors q̂_lo and q̂_hi. The score is E_i = max(q̂_lo(X_i) − Y_i, Y_i − q̂_hi(X_i)), and the interval is [q̂_lo(x) − Q, q̂_hi(x) + Q], with Q the conformal quantile of E. Same marginal guarantee, but the width adapts to x. — [arXiv 1905.03222](https://arxiv.org/abs/1905.03222)
- Weighted conformal under covariate shift (Tibshirani, Barber, Candès, Ramdas, NeurIPS 2019). Weight each calibration point by the likelihood ratio w(x) = dP_test/dP_cal(x) and take the weighted quantile. Coverage holds under the target distribution when w is known (approximately when estimated). — [arXiv 1904.06019](https://arxiv.org/abs/1904.06019)
- Barber, Candès, Ramdas, Tibshirani (Annals of Statistics 2023) bound the coverage loss when exchangeability fails, in terms of total-variation distances between swapped data. — [arXiv 2202.13415](https://arxiv.org/abs/2202.13415)

**Group-conditional coverage**
- Mondrian conformal gives exact finite-sample coverage within each group of a non-overlapping partition by calibrating separately per group. Gibbs, Cherian & Candès ("Conformal Prediction with Conditional Guarantees", JRSS-B 87, 2025) extend this to overlapping groups and to any finite-dimensional class of covariate shifts, with exact finite-sample coverage over every shift in the class. Exact conditional coverage over infinite-dimensional classes is impossible, so they quantify the gap there. The method works on top of black-box split-conformal pipelines and is implemented in MAPIE. — [arXiv 2305.12616](https://arxiv.org/abs/2305.12616); [MAPIE docs](https://mapie.readthedocs.io/en/latest/content/conformal-prediction/conditional-guarantees/)

**Conformal for LLM-as-judge ratings (2025)**
- Sheng et al., "Analyzing Uncertainty of LLM-as-a-Judge: Interval Evaluations with Conformal Prediction" (EMNLP 2025; arXiv Sept 2025):
  - The method extracts the judge's logits over the rating tokens, uses them as features for conformal regression or ordinal conformal, and calibrates offline.
  - It compares 9 conformal methods, 7 regression-type and 2 ordinal.
  - It proposes an ordinal boundary adjustment for discrete scales, with provably non-decreasing coverage.
  - The interval midpoint matched or slightly beat raw LLM scores on correlation with humans, with significantly lower MSE and MAE.
  - Re-prompting the judge with its own interval did not reliably help.
  - Performance was weaker on reasoning tasks, often because the calibration sets were smaller.
  - [arXiv 2509.18658](https://arxiv.org/abs/2509.18658); [ACL Anthology](https://preview.aclanthology.org/setup/2025.emnlp-main.569)
- "Trust or Escalate" (Jung, Brahman, Choi, ICLR 2025): selective LLM judging that abstains or escalates when unsure, calibrated on a human-labelled set so that agreement with humans on non-abstained items is ≥ 1−α with high probability. Its confidence comes from simulated annotators. [prior knowledge, not re-fetched] — [arXiv 2407.18370](https://arxiv.org/abs/2407.18370)

**Noisy gold labels in calibration (2025)**
- Standard conformal prediction calibrated on noisy labels gives large sets when there are many classes. Noise-Aware CP (Penso, Goldberger, Fetaya, COPA 2025) estimates the noise-free threshold under a known noise model and proves finite-sample coverage for uniform noise. Classification only. — [arXiv 2501.12749](https://arxiv.org/abs/2501.12749)
- For partial-label learning, coverage still holds with noisy calibration data, within [1−α, 1−α+1/(n+1)+ε] (Gong, Bisht, Xu, AAAI 2025). — [mlanthology](https://mlanthology.org/aaai/2025/gong2025aaai-conformal)

### Inferences
- **Recipe for "IQ range with 90% coverage" (α = 0.1).**
  1. Build a score from the chats. This could be a cross-fitted calibration map from the LLM's rating(s), optionally plus LLM-logit features à la Sheng et al., to the IQ scale.
  2. Hold out n_cal gold-labelled people, one row per person.
  3. Compute CQR scores, or absolute residuals if widths need not vary.
  4. Report [q̂_lo(x) − Q, q̂_hi(x) + Q].

  The guarantee is marginal: 90% of future people drawn like the calibration people get an interval containing their observed test score.
- **Minimum and practical n_cal (computed here from the Beta formula).** ⌈(n+1)(0.9)⌉ ≤ n requires n_cal ≥ 9, or the interval is infinite. Realised coverage for a given calibration set is Beta(n+1−l, l):
  - n_cal=50 (l=5): Beta(46,5), mean 0.90, SD 0.041.
  - n_cal=200 (l=20): Beta(181,20), mean 0.90, SD 0.021.

  So "90%" from 50 people can realistically be 82–96%.
- **Width is governed by ρ (Gaussian back-of-envelope, illustrative only).** If residual SD = σ_Y·sqrt(1−ρ²) with σ_Y = 15 IQ points, the 90% half-width is about 1.645·15·sqrt(1−ρ²): ±23.5 at ρ=0.3, ±21.4 at ρ=0.5, ±17.6 at ρ=0.7. The unconditional population interval (ρ=0) is ±24.7. Honest chat-based IQ ranges will therefore be wide (~35–50 points) unless the chat signal is strong. That should be displayed, not hidden.
- **Subgroup coverage (native vs non-native, dialect groups).** Marginal coverage can hide 80% coverage in one group and 95% in another. Use Mondrian calibration (needs ≥9, realistically ≥50–100 gold people per group) or Gibbs–Cherian–Candès for overlapping groups such as L1 × chat length. Equal coverage with unequal width is the expected outcome if the LLM is less informative for one group. Width gaps are a measurable fairness and audit statistic that complements the harness's shift measurements.
- **Exchangeability failures specific to this project.**
  - (i) Calibration people (paid ICAR takers) differ from deployment users. Use weighted conformal with an estimated propensity of being in the calibration set.
  - (ii) Multiple chats per person. Calibrate at the person level, or the guarantee is about chats, not people.
  - (iii) LLM version drift. Re-calibrate per model version, since conformal validity is tied to the fixed scoring function.
- **Observed vs true score.** Conformal intervals cover the observed test score, including test measurement error, not latent ability. They are therefore conservative for latent ability but cannot be shrunk to latent-ability intervals without a measurement model, which belongs to the psychometrics stream.
- **Abstention.** A Trust-or-Escalate-style rule ("report a range only when the chat evidence is sufficient; else abstain") can be calibrated the same way, e.g. guaranteeing that coverage or accuracy among non-abstained people stays ≥ 1−α.

### Gaps
- No verified 2024–2026 paper applies conformal prediction to LLM-inferred psychological traits or cognitive ability specifically.
- No verified conformal regression method was found for noisy continuous calibration labels (test-score error). The 2025 noisy-label work found was classification-only.

## Q3. Correcting LLM-as-judge bias with few human labels, and measurement-error models for LLM-generated variables

### Takeaway
The social-science and econometrics literature from 2023 to 2026 agrees that LLM outputs should be treated as error-prone measurements, never as data. With a small random validation sample, design-based (DSL), PPI-type or explicit bias-correction estimators restore valid inference. Naive use is biased even at 80–90% LLM accuracy. Savings are capped by the judge's informativeness: for evaluation tasks, a judge no better than the thing it judges cannot more than halve the labels needed.

### Cited Findings
**Design-based supervised learning, DSL (Egami, Hinck, Stewart, Wei; NeurIPS 2023)**
- Using LLM surrogate labels directly in downstream analyses gives substantial bias and invalid CIs, even when the surrogates are 80–90% accurate. DSL combines surrogates with a smaller set of gold labels in a doubly-robust (debiased-ML) procedure. Validity comes from design: the researcher controls and records the probability that each document is sent for gold labelling. Inference stays valid even when surrogates are arbitrarily biased, with RMSE comparable to prediction-only alternatives. — [arXiv 2306.04746](https://arxiv.org/abs/2306.04746); [NeurIPS 2023](https://proceedings.neurips.cc/paper_files/paper/2023/hash/d862f7f5445255090de13b825b880d59-Abstract.html)
- DSL pseudo-outcome (form as in the paper; [prior knowledge, not re-fetched]): Ỹ_i = ĝ(Q_i, X_i) + (R_i/π_i)·(Y_i − ĝ(Q_i, X_i)). Here Q_i is the LLM output(s), X_i the covariates, ĝ a cross-fitted prediction of Y, R_i the gold-label indicator and π_i the known labelling probability. Ỹ_i is then plugged into the downstream moment equation (linear or logistic regression, etc.). — [arXiv 2306.04746](https://arxiv.org/abs/2306.04746)

**Generated regressors (Battaglia, Christensen, Hansen, Sacher; arXiv 2024, v5 April 2025; Cowles/CEPR discussion paper)**
- Treating AI/ML-generated variables as data in downstream regressions biases estimates and invalidates inference. The main problem is bias, not wrong standard errors. Remedies: an explicit bias correction with bias-corrected CIs, or joint estimation of the regression and the latent variable. — [arXiv 2402.15585](https://arxiv.org/abs/2402.15585)

**Applied econometric framework for LLMs (Ludwig, Mullainathan, Rambachan; NBER w33344; Annual Review of Economics 2026)**
- For prediction uses, valid conclusions need "no training leakage" between the LLM's training data and the researcher's sample. For estimation uses, where the LLM measures a concept, a human-labelled validation sample is required. Without one, prompt and model choices swing estimates in magnitude, sign and significance. With one, imperfect LLM outputs act as "amplifiers" of the validation sample and tighten standard errors. — [arXiv 2412.07031](https://arxiv.org/abs/2412.07031); [NBER w33344](https://nber.org/system/files/working_papers/w33344/w33344.pdf)

**Limits of LLM-as-judge debiasing (Dorner, Nastl, Hardt; ICLR 2025 oral)**
- When the judge is no more accurate than the model being evaluated, no debiasing method can reduce the required ground-truth labels by more than half. In MMLU and MT-Bench experiments, savings beyond 2x were rare. They appeared mainly when a state-of-the-art judge evaluated much weaker models. The commonly reported judge–human agreement rate does not meaningfully bound judge bias or the achievable savings. Judge bias can reorder model rankings even at 79–84% judge accuracy. — [arXiv 2410.13341](https://arxiv.org/abs/2410.13341); [ICLR 2025](https://www.iclr.cc/virtual/2025/oral/31864)

**PPI applied to model evaluation** [prior knowledge, not re-fetched]
- "AutoEval Done Right" (Boyeau, Angelopoulos, Yosef, Malik, Jordan, 2024) applies PPI/PPI++ to estimate model metrics from a few human labels plus many synthetic or judge labels. — [arXiv 2403.07008](https://arxiv.org/abs/2403.07008)
- Prediction-powered ranking (Chatzi et al., NeurIPS 2024) builds rank sets of LLMs with coverage guarantees from pairwise human and LLM comparisons. — [arXiv 2402.17826](https://arxiv.org/abs/2402.17826)
- Stratified PPI and confidence-driven inference (Q1) are the label-efficient judge-evaluation estimators with verified 2024–2025 publication. — [arXiv 2406.04291](https://arxiv.org/abs/2406.04291); [arXiv 2408.15204](https://arxiv.org/abs/2408.15204)

### Inferences
- **Which tool for which downstream use of "LLM-IQ".**
  - (1) LLM-IQ as an outcome, e.g. the mean or a group difference: PPI++/DSL with Y = test score.
  - (2) LLM-IQ as a regressor, e.g. predicting a life outcome from chat-inferred ability: generated-regressor bias, which is attenuation under classical error. Correct with Battaglia et al.'s bias correction, DSL, or classical regression calibration (background). Regression calibration replaces W = LLM-IQ by Ê[X_true | W, Z], estimated in the validation sample; under classical error with no covariates it gives β_RC = β_naive / λ_RC, with λ_RC = Cov(X, W)/Var(W). SIMEX (background) adds simulated extra noise and extrapolates back to zero noise, but it needs the error variance and a classical additive error structure. LLM errors that depend on dialect or jargon (exactly what the audit harness detects) violate that, so DSL, PPI or Battaglia-style corrections, which allow arbitrary error structure given a random validation sample, are safer.
- **Design implication.** Decide the gold-label sampling scheme before collecting ICAR/WAIS scores, and log the inclusion probabilities. DSL and active/stratified PPI then give valid CIs regardless of how biased the LLM is for non-native or dialect writers. Oversampling groups where the audit harness shows large surface-feature sensitivity is allowed and efficient, provided π is known.
- **Expectation management (Dorner et al. plus the ρ table in Q1).** If the chat-based rater correlates only moderately with test scores, the gold-label savings will be modest (≈1.1–1.5x). The main value of the LLM ratings will be breadth (estimates for everyone), not a big cut in the number of tested people. The mixed-subjects authors' ~15% observed gain is a realistic anchor.
- **Leakage (Ludwig et al.).** If public datasets of essays paired with IQ or personality scores could be in the LLM's training data, validate on fresh, privately collected chats.

### Gaps
- No verified paper estimates the size of LLM-judge bias corrections for continuous psychological constructs, as opposed to binary or ordinal evaluation labels.
- The exact form of the later (2024) general-framework version of DSL and its R package (`dsl`) were not re-verified this session.
- No 2023–2026 paper was found applying SIMEX specifically to LLM-generated variables.

## Q4. Work applying these inference and calibration methods to psychological or personality traits inferred by LLMs

### Takeaway
I found no paper that applies PPI, DSL or conformal prediction to LLM-inferred personality, IQ or EQ. The trait-inference studies found report correlations or accuracies only, with no valid downstream-inference or per-person uncertainty layer. The closest methodological precedent is the Mixed Subjects Design, which uses PPI for LLM-simulated survey or experiment responses in social science. This is an open niche the project can fill.

### Cited Findings
- **Cögendez, Zimmermann, Zufferey (arXiv Mar 2026, rev. May 2026), "Can LLMs Infer Conversational Agent Users' Personality Traits from Chat History?"** The data are real ChatGPT logs from N=668 participants (62,090 chats). The models are fine-tuned RoBERTa-base ternary trait classifiers. Accuracy beat chance in several cases, with the largest gain (+44% over baseline) for extraversion on relationship and self-reflection chats. The abstract mentions no calibration, conformal prediction, PPI or uncertainty quantification. This is the closest data analogue to the user's "IQ from chat logs" design. — [arXiv 2604.19785](https://arxiv.org/abs/2604.19785)
- **Other LLM trait-inference studies found.** LLMs inferring psychological dispositions from social-media text (Peters & Matz, PNAS Nexus 2024) and generative AI scoring personality from open-ended narratives (Nature Human Behaviour 2025) report convergent validity with self-reports. The search snippets showed no PPI or conformal layer. — [PNAS Nexus](https://academic.oup.com/pnasnexus/article/3/6/pgae231/7692212); [Nature Human Behaviour](https://www.nature.com/articles/s41562-025-02397-x)
- **Mixed Subjects Design.** It uses PPI with power analysis to combine LLM predictions of human responses with real human subjects in social-science studies, with `mixedsubjects` R software. — [IDEAS/RePEc](https://ideas.repec.org/a/sae/somere/v54y2025i3p1074-1109.html); [CRAN vignette](https://stat.ethz.ch/CRAN/web/packages/mixedsubjects/vignettes/introduction.html)

### Inferences
- **A defensible validation-study analysis plan** (assembled from Q1–Q3 tools, not from any single cited paper):
  1. Randomly or stratified-randomly select people for ICAR/WAIS with logged π.
  2. Report the validity coefficient on the gold set alone, with a CI.
  3. Report population and group parameters (mean ability, native vs non-native gap) with PPI++/DSL CIs, next to the naive LLM-only numbers, to show the bias.
  4. Report per-person ranges with CQR plus Mondrian or conditional conformal, with per-group coverage and width tables.
  5. Use cluster-robust errors if the analysis is at chat level.
  6. Re-calibrate whenever the LLM or prompt changes.
- The audit harness's surface-feature shifts (dialect, non-native English, jargon, pasted text) are natural strata for stratified PPI and natural groups for Mondrian conformal. Inflated or deflated LLM scores for a group show up as group-specific rectifiers (bias) and as coverage or width gaps.

### Gaps
- No verified study applies PPI, DSL or conformal methods to LLM-inferred cognitive ability (IQ) or emotional intelligence (EQ).
- The ground-truth instrument and sample details of Cögendez et al. could not be confirmed from the abstract page.
- Typical LLM–IQ-test correlations needed to plug into the ρ tables are out of scope here (text-to-ability stream). Without them, the savings and width numbers above are illustrative only.
