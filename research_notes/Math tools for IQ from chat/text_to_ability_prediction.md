# Text-to-Ability Prediction: Methods, Math and Limits (2023-2026 focus)

Scope note: this file covers predicting cognitive ability (and, for comparison, other stable traits) from text, especially many short messages. PPI/conformal methods, IRT/DIF, causal/fairness/concept erasure and sycophancy are covered elsewhere. Items marked "background" are pre-2023 foundations. Wikipedia links marked "(standard reference, not fetched)" point to textbook formulas that were not re-read in this session. Every formula in the "Inferences" blocks is my own derivation from the cited formulas, and the arithmetic is shown so it can be checked.

## 1. Embedding-based supervised prediction, and how accuracy scales with labeled N and with words per person

### Takeaway
The best verified result is still Wolfram (2025). A single ~250-word, on-prompt essay at age 11, turned into OpenAI ada-002 embeddings and fed to an untuned SuperLearner, gave holdout R^2 = .57 for general cognitive ability (N about 10.5k essays). Verbal, reading and math scores were predicted at R^2 .55-.59, but non-verbal ability only at .37. Text volume shows fast diminishing returns: in Facebook personality data, about 20 posts (about 340 words) already captured much of the signal, and accuracy plateaued well before 200 posts. I found no 2023-2026 learning curve over the number of labeled people for ability prediction.

### Cited Findings
**Wolfram (2025), Communications Psychology 3:95 ("LLMs predict cognition and education close to or better than genomics or expert assessment")** — [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC12229686/), [DOI](https://doi.org/10.1038/s44271-025-00274-x)
- **Data.** National Child Development Study (1958 British birth cohort). 10,511 essays written at age 11 on the theme "Imagine you are 25". Essays were 1 to 1,239 words long, with roughly 250 words requested.
- **Features.** text-embedding-ada-002 (1,536 dimensions). Also linguistic features: TAALED (lexical diversity), TAALES (lexical sophistication), SEANCE (sentiment), 31 readability metrics, and LanguageTool grammar/typo ratios. Methods says 534 linguistic metrics and Results says 566, which is an internal inconsistency.
- **Learner.** SuperLearner over xgboost, ranger, nnet, radial SVM, linear regression and the training mean, with LASSO pre-screening. All learners used default settings with no tuning. The linear model and random forest got the highest weights.
- **Validation.** Nested cross-validation with 10 outer and 5 inner folds, MSE loss.
- **Holdout R^2 from essays:**
  - general cognitive ability (age 11): .57
  - verbal (11): .55
  - non-verbal (11): .37
  - reading (11): .59; reading (16): .58
  - math (11): .55; math (16): .55
- **Teacher assessment (TA) comparison:** g .62, verbal .57, non-verbal .45, math (16) .62. Polygenic scores (PGS) for g: .15. The combined text + TA + PGS ensemble reached .70 for g.
- **Educational attainment (age 33):** essays .26, TA .29, PGS .19, all three combined .38. Parental education alone gave .12. A Fragile-Families-style sociological baseline gave .18-.19.
- **Non-cognitive outcomes from essays:** externalizing .08, internalizing .03, scholastic motivation .08.
- **Which features mattered:**
  - Embeddings alone did almost as well as the full feature set.
  - GPT-3.5/GPT-4-family embeddings beat RoBERTa.
  - The full model beat essay length alone by a factor the paper calls "often exceeding 5–10 times".
  - Root type-token ratio was selected in 96.6% of models.
- **Not reported.** No learning curve over training N, no analysis of text length, no SES-adjusted model, and no split into fluid vs crystallized ability. The author discloses employment at a genomics company.

**Peters & Matz (2024), PNAS Nexus (zero-shot LLM, Facebook)** — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11211928/)
- **Data.** N = 1,000 users, each with at least 200 status updates; the 200 most recent were used. Updates averaged 17.10 words (SD 15.03), so roughly 3,400 words per user.
- **Correlation with self-reported Big Five.** GPT-4 average r = .31 (range .26-.33); GPT-3.5 average r = .27. Supervised models on the same data source reached an average r = .37 (range .26-.41, citing Park et al.).
- **Text-volume curve** (20 updates up to 200, in chunks of 20). Most correlations were near their maximum well before 200 updates, and a substantial share of variance was captured with about 20 updates. Conscientiousness leveled off earliest.
- **Demographic error.** Absolute residuals differed by gender and age (for example, larger for men on C, A and N). Within-group correlations did not differ significantly. In other words, there was bias in level or calibration, not in rank-ordering.

**Peters, Cerf & Matz (2024), arXiv 2405.13052 (GPT-4 chatbot conversations)** — [arXiv](https://arxiv.org/abs/2405.13052)
- Mean r with self-reported Big Five by chatbot condition:
  - personality-eliciting chatbot: .443 (range .245-.640)
  - naturalistic chatbot: .218 (.066-.373)
  - default "helpful assistant" (ChatGPT-like): .117 (-.004 to .209)
- Scores came from three extra GPT-4 calls over the transcript, averaged.
- Users rated the eliciting conversations as equally natural.

**Fan et al. (2023), Journal of Applied Psychology 108(8):1277-1299** — [NYU listing](https://ifp.nyu.edu/?p=1679075), [Auburn summary](https://ocm.auburn.edu/experts/2023/02/151108-fan-ai-personality-ea.php), [summary](https://academicnewsletter.sufe.edu.cn/info/368997)
- N = 1,444 undergraduates had a 20-30 minute conversation with a Juji chatbot, and machine learning on the free-text answers produced Big Five scores.
- The scores had "acceptable" reliability, a factor structure comparable to questionnaire scores, some incremental validity, and cross-sample generalizability.
- Exact correlations were not retrieved.

**Wright et al. (2026), Nature Human Behaviour 10(3):541-555 (zero-shot scoring by 7 LLMs)** — [DOI page](https://www.nature.com/articles/s41562-025-02389-x), [U. Minnesota record](https://experts.umn.edu/en/publications/assessing-personality-using-zero-shot-generative-ai-scoring-of-br/)
- Texts were streams of thought and daily video-diary transcripts.
- Averaging the scores across models gave the strongest agreement with self-report, "comparable to or exceeding" self-other agreement, EMA and bespoke machine-learning benchmarks.
- The headline r is reported inconsistently in secondary sources: an average convergent r = 0.48 in a search snippet of the [PMC version](https://pmc.ncbi.nlm.nih.gov/articles/PMC12974486/), versus r = .415 for the stream-of-thought ensemble cited by [arXiv 2604.06071](https://arxiv.org/html/2604.06071v1). Neither was verified against the full text.

**Background: Ganesan et al. (2021), NAACL, "The Role of Sample Size and Dimensionality"** — [arXiv](https://arxiv.org/abs/2105.03484)
- In human-level tasks, N is often smaller than the 768+ embedding dimensions.
- Fine-tuning large models on limited data is hard. Pre-trained dimension reduction (PCA) fixes much of this.
- RoBERTa was best. PCA handled users who write longer texts better than other reduction methods. Most tasks matched best performance with 1/12 of the embedding dimensions.

**Background: Eichstaedt et al. (2021), Psychological Methods 26(4)** — [JHU record](https://pure.johnshopkins.edu/en/publications/closed-and-open-vocabulary-approaches-to-text-analysis-a-review-q/)
- 65,896 Facebook users. The paper explicitly studies the effects of sample size, words per user and number of topics. Its numbers could not be retrieved because the PDF was larger than 10 MB.

**Background: older stylometric IQ estimation** (vocabulary ratios, small samples, weak criteria) — [Hendrix & Yampolskiy, CEUR 2017](https://ceur-ws.org/Vol-1964/CS1.pdf)
- No LLM-based zero-shot IQ-from-writing validation against standardized tests turned up in search.

**Social media text to verbal intelligence**
- [Sci. Reports 2024, VK users, N = 1,358](https://www.nature.com/articles/s41598-024-56080-8): BERT-based models for verbal intelligence, Big Five and logical thinking. Average word length in posts was the most important feature for verbal intelligence. Metrics were not retrieved because of a paywall redirect.
- ["Mining Minds" (ACM 2024)](https://dl.acm.org/doi/fullHtml/10.1145/3651671.3651750): 93 stylometric features. Metrics were not retrieved (HTTP 403).

### Inferences
- **What the Wolfram number means.** Holdout R^2 = .57 corresponds to r ≈ .755. That came from about 250 words of prompted, same-task, handwritten-era school writing with N ≈ 10k labeled children.
  - That setting is close to a standardized test item: same prompt, same age, same context.
  - Chat logs violate all three conditions. Expect lower validity unless the prompt or context is standardized, for example asking every user the same writing or explanation tasks inside the chat.
- **Elicitation design matters more than model size for conversations.** On personality, default ChatGPT-style logs gave r ≈ .12 while an eliciting chatbot gave r ≈ .44 (Peters, Cerf & Matz). That is consistent with the near-chance zero-shot results on real ChatGPT histories (Cögendez et al. 2026, per the brief).
- **Practical recipe from these sources:**
  1. Frozen LLM embeddings, reduced (PCA to around 64-128 dimensions when N is in the hundreds to low thousands).
  2. Ridge or elastic net plus a tree ensemble, stacked (SuperLearner), with nested cross-validation.
  3. Add cheap lexical diversity features (root TTR = types/sqrt(tokens)) and an error-rate feature.
- **Scaling with labeled N.** I found no published 2023-2026 learning curve for ability. A standard rule is that out-of-sample R^2 for ridge on p effective dimensions falls short of the population R^2 by roughly a factor of p/N. That is why reducing dimensions helps when N is small (consistent with Ganesan 2021). This is heuristic and not from a cited 2023-2026 source.

### Gaps
- No 2023-2026 paper found that reports an ability-prediction learning curve over the number of labeled persons, or over words per person.
- Wolfram reports no text-length analysis beyond the length-only baseline.
- Exact r values were not retrieved for Fan et al. (2023), Wright et al. (2026), the Sci. Reports VK study or the ACM "Mining Minds" study.
- Fine-tuned encoders compared with frozen embeddings plus ridge for ability prediction: no 2023-2026 head-to-head found. Wolfram found GPT embeddings beat RoBERTa, but did not fine-tune.
- [Survey of LLMs for perception and measurement of human psychology (arXiv 2606.20603)](https://arxiv.org/pdf/2606.20603) and [LLM personality inference from real-world interviews (arXiv 2509.13244)](https://arxiv.org/html/2509.13244v1) were surfaced but not read.

## 2. Multi-instance and hierarchical aggregation over many messages, and the reliability gain from aggregation

### Takeaway
Three aggregation families are documented: mean pooling, attention-based multiple-instance learning (MIL) with message-level attention, and hierarchical "human language models". Message-level attention beat word-level attention for personality. A Gaussian random-effects model makes the Bayesian shrinkage factor exactly equal to the Spearman-Brown reliability of the per-person mean. The key limit is that aggregation removes only message-specific noise. Validity converges to r_1/sqrt(ρ_1) (defined below), not to 1.

### Cited Findings
- **Background: message-level attention** — [Lynn, Balasubramanian & Schwartz (2020, ACL)](https://aclanthology.org/2020.acl-main.472/), [paper summary](https://paperswithcode.com/paper/hierarchical-modeling-for-user-personality). A hierarchical model (word attention, then message attention, then a user vector) learned how much each post matters for a user's Big Five. Message-level attention beat word-level attention.
- **Background: Transformer-MD** — [AAAI 2021](https://ojs.aaai.org/index.php/AAAI/article/view/17673/17480). Order-agnostic multi-document encoding: each post can attend to the user's other posts through Transformer-XL memory, and trait-specific attention lets each trait use different posts.
- **Human language modeling (HaRT)**
  - [Soni et al. 2022, ACL Findings](https://arxiv.org/abs/2205.05128): pre-trained on about 100k social media users, conditioned on a user state that evolves over that user's sequence of documents. Met or beat the state of the art on user-level age and openness.
  - [2024 follow-up (arXiv 2401.12492)](https://arxiv.org/abs/2401.12492): pre-training with both individual and group context improved user-level age and personality regression from multiple documents.
  - A 2025 NAACL evaluation reportedly found HuLM (HaRT-variant) hidden states best for user-level trait prediction. This is [third-party summary only](https://liner.com/review/evaluation-llmsbased-hidden-states-as-author-representations-for-psychological-humancentered), unverified.
- **Aggregation in zero-shot LLM pipelines**
  - Peters & Matz scored chunks of 20 posts and averaged three runs; accuracy rose with chunks but plateaued — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11211928/).
  - Wright et al. found the average across 7 LLMs beat any single LLM — [Nature Hum. Behav.](https://www.nature.com/articles/s41562-025-02389-x).
- **Background: attention-based MIL** — [Ilse, Tomczak & Welling (2018), ICML](https://arxiv.org/abs/1802.04712). The person-level vector is z_i = Σ_j a_ij h_ij, with a_ij = softmax_j(wᵀ tanh(V h_ij)), optionally gated. The permutation-invariant pooling suits unordered message bags.
- **Spearman-Brown** — [Wikipedia (standard reference, not fetched)](https://en.wikipedia.org/wiki/Spearman%E2%80%93Brown_prediction_formula). If one unit has reliability ρ_1, the mean of k parallel units has reliability ρ_k = kρ_1 / (1 + (k−1)ρ_1).
- **Empirical-Bayes shrinkage** — [Wikipedia (standard reference, not fetched)](https://en.wikipedia.org/wiki/Empirical_Bayes_method). Model: y_ij = θ_i + ε_ij, θ_i ~ N(μ, τ²), ε_ij ~ N(0, σ²). The posterior mean is θ̂_i = μ + B_i(ȳ_i − μ), with B_i = τ² / (τ² + σ²/n_i).

### Inferences
- **Shrinkage equals Spearman-Brown.** Set ρ_1 = τ²/(τ²+σ²), the share of message-level score variance that is stable person variance. Then
  - B_i = n_iτ² / (n_iτ² + σ²) = n_iρ_1 / (1 + (n_i−1)ρ_1).
  - The optimal shrinkage toward the population mean is exactly the Spearman-Brown reliability of that person's mean (Kelley's true-score formula).
  - Practical consequence: users with few messages should get estimates near 100 and wide intervals; heavy users get less shrinkage.
- **Validity ceiling under aggregation.** Let r_1 be the correlation of a single message-level prediction with IQ. For k parallel messages, the composite's validity is r_k = r_1·sqrt(k / (1 + (k−1)ρ_1)). As k → ∞, r_k → r_1/sqrt(ρ_1), which is the correlation of the stable person-level text component θ_i with IQ.
  - Worked example: r_1 = .15 and ρ_1 = .10 gives r_10 = .15·sqrt(10/1.9) ≈ .34, r_50 ≈ .15·sqrt(50/5.9) ≈ .44, and a limit of .15/sqrt(.10) ≈ .47.
  - More chat cannot push validity past the stable trait-relevant component. This matches the plateau Peters & Matz saw before 200 posts.
  - Spearman-Brown assumes parallel units. Chat messages differ in topic, length and register, so in practice gains are smaller.
- **Proposed model for chat logs.** Score each session or message, then fit crossed random effects: y_ijt = θ_i + γ_t(topic/task) + δ(register, length) + ε_ijt.
  - Report θ̂_i with its posterior SD.
  - Weight by length: σ²_ij ∝ 1/words_ij.
  - Attention-MIL can learn which messages are diagnostic, for example explanations and arguments as opposed to "thanks!". It needs many labeled persons, because the bag label is person-level only.
- **Equivalent in prompt-based scoring.** Average several runs, several chunks and several LLMs. This is the same variance reduction, and Wright et al. found the model ensemble best.

### Gaps
- I found no 2023-2026 paper that applies attention-MIL or Bayesian hierarchical shrinkage specifically to cognitive-ability prediction from many messages.
- No published estimate of the message-level reliability ρ_1 of ability-relevant text signal in chat.
- The test-retest reliability of language-based trait scores over time (for example Park et al. 2015, background) was not retrieved in this session.

## 3. Information-theoretic and surprisal measures (perplexity, entropy, compression, lexical sophistication) and their links to ability or education

### Takeaway
2024-2026 evidence links LLM surprisal or perplexity of a person's writing to L2 proficiency (more proficient writers produce lower surprisal) across Swedish, English, Chinese and Japanese learner corpora. I found no 2023-2026 study linking writer-level perplexity to measured IQ. The relationship is non-monotonic and heavily confounded. Errors and disfluency raise perplexity. A limited, formulaic vocabulary (typical of L2 writers) lowers it, which is why GPT detectors flag non-native essays as AI-written. The most robust "sophistication" features in Wolfram were lexical diversity (root TTR) and readability or errors, not surprisal.

### Cited Findings
- **Surprisal and the reader's IQ (comprehension side)** — [Haller et al. 2024, ACL Findings](https://aclanthology.org/2024.findings-acl.469/). Individual cognitive measures improved how well LM surprisal and entropy predicted reading times. GPT-2 surprisal's predictive power degraded for readers with higher verbal intelligence. This concerns readers, not writers.
- **Swedish L2 essays** — [Muñoz Sánchez, Dobnik & Volodina (BEA 2024)](https://preview.aclanthology.org/setup/2024.bea-1.34). GPT-SW3 perplexity tends to be lower at higher CEFR levels. Normalized (error-corrected) essays have lower perplexity than the originals. Some perplexity spikes come from factors unrelated to learner language.
- **English degree expressions** — [Cambridge 2024](https://resolve.cambridge.org/core/services/aop-cambridge-core/content/view/4C0C2D2C078C2D93D0213D387885D82C/S2977042424000566a.pdf/second-language-learning-of-degree-expressions-a-computational-approach.pdf). Higher surprisal goes with lower proficiency, and surprisal predicted proficiency better than classic NLP measures.
- **Chinese learners' English writing** — [Cong et al.](https://cla.purdue.edu/academic/slc/news/documents/yans-article.pdf). "LLM-Surprisal" is framed as a measure of the interplay between lexical diversity and syntactic complexity. It separates L2 from L1 writing and indexes developmental stages.
- **Chinese L2 writing** — [CMCL 2025](https://preview.aclanthology.org/moar-dois/2025.cmcl-1.22.pdf). Tests whether LLM surprisal separates proficiency levels and notes that the quality of surprisal estimates depends on the model.
- **L2 Japanese essays** — [AIME-Con 2026](https://aclanthology.org/2026.aimecon-main.24/). Surprisal separates proficiency levels, and surprisal plus feature indices gave the best classification.
- **GPT detectors and non-native writers** — [Liang et al. 2023, Patterns (arXiv)](https://arxiv.org/html/2304.02819v3).
  - Of 91 TOEFL essays by Chinese students, all seven detectors flagged 18 (19.78%) as AI, and at least one detector flagged 89 (97.80%).
  - The unanimously flagged essays had significantly lower perplexity (p = 9.74E-05).
  - Prompting ChatGPT to enrich word choice reduced false positives.
  - The average false positive rate is quoted as about 61% in secondary sources; this was not verified in the primary text.
- **Lexical diversity in Wolfram** — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12229686/). Root TTR was selected in 96.6% of models, and a further lexical diversity measure was also among the most consistently selected features. Embeddings alone were nearly as good as embeddings plus all hand-built linguistic features.
- **Average word length in VK posts** — [Sci. Reports 2024](https://www.nature.com/articles/s41598-024-56080-8). It was the top explanatory feature for predicted verbal intelligence.
- **Emotional intelligence and online text (2023)** — [PMC10130158](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10130158/). Characteristics of user-generated text predicted EI; high-EI people used more positive and less negative affect language. Effect sizes were not retrieved.

### Inferences
- **Information density formulas.** Mean surprisal per token is S̄ = −(1/T) Σ_t log p_LM(w_t | w_<t), and perplexity is PPL = exp(S̄).
- **Two opposing mechanisms bias S̄ as an ability proxy:**
  - (a) Errors, typos and disfluency raise S̄ (low ability raises perplexity).
  - (b) Rare words, long-range structure and novel content raise S̄ (high ability also raises perplexity), while limited formulaic vocabulary lowers it (L2 and low-ability writers lower perplexity).
  - Net: raw perplexity is not monotone in ability.
- **Fixes for that bias:**
  - Compute surprisal on error-corrected text (normalize first; the Swedish result shows normalization changes perplexity).
  - Separate error rate from lexical rarity.
  - Condition on topic and register by computing surprisal relative to a topic-matched reference, for example a z-score against other users answering the same prompt.
- **Compression complexity.** Compression ratio (bytes after gzip or an LM-based coder, divided by raw bytes) is a crude upper bound on per-character entropy rate. With an LM coder it is essentially S̄ in bits. It inherits the same confounds and also depends heavily on length, so compare only at fixed length windows. I found no 2023-2026 study linking writer compression complexity to IQ.
- **Signals likely to be most valid for chat.** Length-normalized lexical diversity (root TTR, MTLD) on standardized prompts; rare-word use measured against topic-matched baselines; and error rates on unedited typing. Chat interfaces with autocorrect, or users pasting LLM-written text, contaminate all three.

### Gaps
- No 2023-2026 study found that correlates writer-level LLM perplexity, entropy rate or compression complexity with measured IQ, or with years of education in native speakers.
- No study found that uses LLM-estimated word difficulty or age-of-acquisition norms as person-level ability predictors with validity against tests.
- Effect sizes for the L2 surprisal-proficiency studies were not retrieved; the direction is consistent across all of them.

## 4. Domain shift and confounding: separating ability from education, SES and L1, and evidence that text predictions mostly track crystallized/verbal ability

### Takeaway
The direct evidence points to text predictions tracking verbal, crystallized and school-achievement constructs. In Wolfram's study, essays predicted verbal (.55), reading (.59) and math (.55) about as well as teachers did, but non-verbal ability much less well (.37). L1 status strongly shifts surface statistics such as perplexity. I found no 2023-2026 work applying invariant risk minimization, domain adaptation or residualization specifically to text-based ability prediction. Methods exist; validated applications do not.

### Cited Findings
- **Construct profile of essay predictions** — [Wolfram 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12229686/). Holdout R^2: reading .59, verbal .55, math .55, g .57, non-verbal .37. Teacher ratings show the same ordering (verbal .57, non-verbal .45).
  - The paper does not separate fluid from crystallized ability and does not isolate writing skill.
  - It does not adjust for SES. Parental education alone predicted attainment at R^2 .12, and essays at .26.
- **Calibration bias by demographic group** — [Peters & Matz 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11211928/). Mean absolute error differed by gender and age, while within-group correlations did not differ. The bias was in level or calibration, not in rank-ordering.
- **Small subgroup differences in chat** — [Peters, Cerf & Matz 2024](https://arxiv.org/abs/2405.13052). Preliminary analyses suggest only marginal accuracy differences across socio-demographic subgroups.
- **L1 confound** — [Liang et al. 2023](https://arxiv.org/html/2304.02819v3). Non-native writing has systematically lower perplexity, which caused near-universal misclassification by perplexity-based detectors.
- **L2 proficiency shifts surprisal** — [BEA 2024](https://preview.aclanthology.org/setup/2024.bea-1.34), [Cong et al.](https://cla.purdue.edu/academic/slc/news/documents/yans-article.pdf). An ability model trained on native speakers will read L2 proficiency as "ability".
- **Background: invariant risk minimization** — [Arjovsky et al. 2019](https://arxiv.org/abs/1907.02893). Learn a representation Φ such that the same predictor w is optimal in every training environment e: min Σ_e R^e(w∘Φ) + λ‖∇_w R^e(w·Φ)|_{w=1}‖². The environments here could be L1 groups, education strata or platforms.
- **User-factor adaptation.** The 2024 HaRT follow-up shows that conditioning on group-level context (demographic or group features) changes user-level prediction — [arXiv 2401.12492](https://arxiv.org/abs/2401.12492).

### Inferences
- **Residualizing education.** Fitting ŷ_res = ŷ − E[ŷ | education, SES, L1] and validating ŷ_res against IQ_res = IQ − E[IQ | same covariates] gives a partial validity: the ability signal beyond what the covariates explain.
  - This is the right number to report if the claim is "the text measures ability, not schooling".
  - It removes real ability variance too, because education is partly caused by ability, so the partial validity is a lower bound on construct validity, not the true value.
- **Report the decomposition.** R^2(text) and R^2(covariates) on their own; ΔR^2 of text over covariates; and validity within strata such as L1 or education band.
  - The Peters & Matz pattern (equal within-group r, different mean error) suggests the main risk is group-level miscalibration. Fix it with group-wise recalibration (intercept and slope) and check it with residual-by-group plots.
- **Explicit L1 environments.** For L1-heterogeneous chat users, treat L1 as an explicit environment: fit or recalibrate per language group, or use invariance or adversarial penalties.
  - Measure ability within a language: a non-native user's English chat reflects English proficiency more than g.
  - Prefer the user's L1 when possible.
- **Predicting non-verbal ability.** Given Wolfram's construct profile, a chat-based estimate should be labeled a verbal/crystallized or "school-achievement-like" indicator unless validated against non-verbal tests. Its predicted non-verbal R^2 should be expected to be roughly 30-40% lower: on Wolfram's numbers .37 vs .55-.59 for verbal and reading.

### Gaps
- No 2023-2026 study found that applies IRM, adversarial domain adaptation or formal residualization to text-to-IQ prediction and reports partial validity.
- No study found that directly decomposes text-predicted IQ into education, SES and L1 components in adults.
- Fluid-vs-crystallized split for chat or social-media text: no direct test found beyond Wolfram's verbal vs non-verbal contrast.

## 5. Theoretical limits: mutual information bounds, regression to the mean and calibration, and the ceiling from an unreliable criterion

### Takeaway
Three limits stack.
1. **Information:** R^2 ≤ 1 − exp(−2·I(IQ; text)) when IQ is Gaussian, and no post-processing can add information.
2. **Criterion reliability:** the observed correlation r ≤ sqrt(rel_pred × rel_test).
3. **Calibration:** an MSE-optimal predictor has prediction SD = r·15. People with true IQ of 130 get mean predictions of about 100 + r²·30, and individual 95% intervals are about ±1.96·15·sqrt(1−R^2), which is about ±19 IQ points even at Wolfram-level R^2 = .57.

### Cited Findings
- **Gaussian mutual information** — [Wikipedia: Mutual information](https://en.wikipedia.org/wiki/Mutual_information) (fetched). For a bivariate normal, I = −½ log(1 − ρ²), equivalently ρ² = 1 − exp(−2I) with I in nats.
- **Data processing inequality** — [Wikipedia (standard reference, not fetched)](https://en.wikipedia.org/wiki/Data_processing_inequality). For any processing f, I(Y; f(T)) ≤ I(Y; T).
- **Estimation counterpart of Fano's inequality** — [Wikipedia: Differential entropy (standard reference, not fetched)](https://en.wikipedia.org/wiki/Differential_entropy). E[(Y − Ŷ(T))²] ≥ (1/(2πe))·exp(2h(Y|T)).
- **Correction for attenuation** — [Wikipedia (standard reference, not fetched)](https://en.wikipedia.org/wiki/Correction_for_attenuation). r_observed = r_true·sqrt(rel_x·rel_y), so r_observed ≤ sqrt(rel_x·rel_y).
- **Regression toward the mean** — [Wikipedia (standard reference, not fetched)](https://en.wikipedia.org/wiki/Regression_toward_the_mean).
- **Empirical anchor for the reliability ceiling** — [Wolfram 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12229686/). The text + teacher + PGS ensemble reached R^2 = .70 for g, which the paper says "approaches the test-retest reliability of benchmark intelligence tests". The paper does not report the test-retest reliability of its own criterion tests.

### Inferences
- **A general bound, not just a Gaussian identity.** Combine the Fano-type inequality with h(Y|T) = h(Y) − I(Y;T). If IQ is normed Gaussian with variance σ², then h(Y) = ½ log(2πeσ²). For any predictor from any text representation, MSE ≥ σ²·exp(−2I), so R^2_max ≤ 1 − exp(−2·I(IQ; T)).
- **Information content of reported results** (I = −½ ln(1−R^2)):

| Result | R^2 | Information |
|---|---|---|
| Wolfram, essays → g | .57 | 0.42 nats ≈ 0.61 bits |
| Wolfram, combined ensemble | .70 | 0.60 nats ≈ 0.87 bits |
| Wolfram, non-verbal | .37 | 0.23 nats ≈ 0.33 bits |
| Peters & Matz (r = .31) | .096 | 0.05 nats ≈ 0.07 bits |

  A chat log with r ≈ .3 carries less than one tenth of a bit about the trait.
- **Ceiling from the criterion.** If the IQ test used for training and validation has reliability .90, observed R^2 ≤ .90 even with perfect text information. A short online test with reliability .70 caps observed R^2 at .70.
  - Validating against a noisy criterion understates true validity. You can disattenuate for reporting, but not for individual predictions.
  - Training on a noisy criterion adds label noise, which raises the N needed.
  - If rel_pred is the Spearman-Brown reliability of the aggregated chat score (Section 2), then r_observed ≤ sqrt(rel_pred·rel_test). Both terms are needed.
- **Calibration and regression to the mean.** Assume a joint Gaussian, an MSE-trained predictor ŷ = E[IQ | T] and SD 15.
  - Calibration in the large holds: E[IQ | ŷ] = ŷ.
  - SD(ŷ) = 15r, so at R^2 .57 the SD is ≈ 11.3.
  - Conditional on true IQ, E[ŷ | IQ] = 100 + r²(IQ − 100). A true 130 is predicted on average at 100 + .57·30 ≈ 117, and a true 70 at ≈ 83.
  - Standard error of estimate = 15·sqrt(1 − R^2):

| Validity | SEE (IQ points) | 95% interval |
|---|---|---|
| R^2 .57 | 9.84 | ±19.3 |
| R^2 .70 | 8.2 | ±16.1 |
| r = .31 | 14.3 | about ±28, nearly as wide as the population ±29.4 |

- **Rescaling makes it worse.** Rescaling predictions to SD 15 (common in "IQ estimate" products) un-shrinks them. MSE becomes 2σ²(1 − r) instead of σ²(1 − r²): RMSE 10.6 vs 9.9 at r = .75, and 17.7 vs 14.3 at r = .31. Rescaling always loses accuracy and exaggerates extreme estimates.
- **Per-person intervals.** With the hierarchical model in Section 2, each user's interval should also widen as their message count falls, because their shrinkage factor B_i is smaller.

### Gaps
- The bound R^2 ≤ 1 − exp(−2I) relies on IQ being Gaussian; it is exact only with a Gaussian residual. I did not find a 2023-2026 paper applying it empirically to text-trait prediction, for example by estimating I with neural MI estimators.
- The inequality sources (data processing inequality, the Fano counterpart) are textbook results whose Wikipedia pages were not re-fetched in this session; verify them against Cover & Thomas before formal publication.
- Test-retest reliabilities of the NCDS age-11 tests were not found.

## 6. 2024-2026 LLM-based prediction of cognitive ability or cognitive status from conversation, dialogue or speech transcripts

### Takeaway
Direct LLM-from-dialogue prediction of IQ in healthy adults appears unpublished; I found none. The closest evidence comes from two places:
- Chatbot personality inference, where elicitation design dominates accuracy (r .44 eliciting vs .12 default assistant).
- Clinical speech, where 2024 challenge systems detected MCI at about 78% balanced accuracy and predicted MMSE with RMSE of about 2.7-5.3 points, and acoustic features sometimes beat transcript-language features.

Clinical results target impairment (a large, low-variance-within-group deficit), not normal-range IQ differences, so they do not transfer directly.

### Cited Findings
- **Chat personality** — [Peters, Cerf & Matz 2024](https://arxiv.org/abs/2405.13052). GPT-4 chatbot inference of Big Five from conversation transcripts: eliciting r = .443, naturalistic .218, default assistant .117.
- **Chat personality, older platform** — [Fan et al. 2023 JAP](https://ifp.nyu.edu/?p=1679075). A 20-30 minute Juji chatbot conversation (N = 1,444) gave machine-inferred Big Five scores with acceptable reliability and generalizability.
- **TAUKADIAL challenge (Interspeech 2024)** — [Hoang et al. 2024](https://www.isca-archive.org/interspeech_2024/hoang24_interspeech.pdf). A bilingual English/Chinese system reported 78.2% average balanced accuracy for MCI detection and an averaged MMSE RMSE of 2.705. The acoustic model outperformed the language-based model. Numbers are from the search snippet.
- **Multilingual LLM + speech** — [ResearchGate](https://www.researchgate.net/publication/387331231_Multilingual_Prediction_of_Cognitive_Impairment_with_Large_Language_Models_and_Speech_Analysis). Fully automatic acoustic + linguistic features gave 78.87% AD classification accuracy and an MMSE RMSE of 5.28 (search snippet; not verified in full text).
- **DementiaBank study** — [Communications Medicine 2025](https://www.nature.com/articles/s43856-025-01263-1). N = 291 with external validation N = 22, covering ADRD detection and MMSE prediction. MCI is harder because its language changes are subtler. Metrics were not retrieved because of a paywall redirect.
- **Framingham progression** — [Amini et al. 2024, Alzheimer's & Dementia](https://alz-journals.onlinelibrary.wiley.com/doi/10.1002/alz.13886). Predicted MCI-to-AD progression within 6 years from speech with language models. Metrics were not retrieved (HTTP 403).
- **Background: GPT-3 embeddings** — [Agbavor & Liang 2022, PLOS Digital Health, Drexel summary](https://drexel.edu/news/archive/2022/december/gpt-3-alzheimers-disease). GPT-3 embeddings of ADReSSo transcripts outperformed acoustic-feature models for AD detection. The press release says about 20% more accurate MMSE prediction; the RMSE was not retrieved.
- **Audio LLMs** — [CogBench 2025 (arXiv 2508.03360)](https://arxiv.org/pdf/2508.03360). Audio LLMs (Qwen2-Audio, Ultravox and others) were benchmarked on multilingual speech-based cognitive impairment assessment. Exact task metrics were not verified.

### Inferences
- **What carries over to chat logs:**
  - (a) Elicitation tasks beat passive logs. Clinical speech uses standardized tasks such as picture description for the same reason Wolfram's essays work: same prompt, comparable output.
  - (b) Non-lexical channels (acoustics in speech; in chat, timing, editing behavior and typo dynamics) can carry signal that transcripts lack.
  - (c) Clinical accuracy reflects detecting deficits. Normal-range IQ discrimination is harder, and its R^2 is bounded as in Section 5.
- **A defensible design** for "chat → ability" therefore embeds a few standardized prompts in the chat (explain a concept, summarize a passage, define words, solve a verbal reasoning item). Score them with embeddings plus supervised calibration against a reliable test (N in the thousands), and aggregate across sessions with hierarchical shrinkage. Naturalistic assistant logs alone are likely to give low validity (personality analog: r ≈ .12).

### Gaps
- No 2024-2026 study found that predicts measured IQ or verbal IQ (as opposed to dementia status, MMSE or personality) from conversational or dialogue transcripts with an LLM.
- Exact metrics not verified: Amini et al. 2024 (AUC), Communications Medicine 2025 (MMSE RMSE), the multilingual LLM study (full text) and Agbavor & Liang (RMSE).
- Whether user-AI chat (as opposed to human-human conversation) contains enough user-produced text per session for stable estimates is untested; the Cögendez et al. 2026 near-chance result (from the brief, not re-verified here) suggests it often does not.
