# Predicting IQ / general cognitive ability (g) from natural-language text: empirical accuracy

Scope note: this file covers IQ and cognitive ability only. EQ, privacy/attribute-inference from LLM chats, and ethics/commercial tools are covered elsewhere. Where a correlation is converted from R², the conversion (r = sqrt(R²)) is mine and is marked as such. "Measured IQ" means scores from a validated cognitive test. Proxies (SAT/GRE, education, self-report) are labelled as proxies.

Research-process caveat: several key primary sources (PNAS, JPSP, JAP, PMC, ACM, ResearchGate) blocked automated fetching during this session. Figures I could not read in a primary or near-primary source are listed under Gaps as unverified, not as findings.

---

## Q1. Which studies have correlated language features or text-based ML models with measured intelligence, and how big are the correlations?

### Takeaway
The strongest validated result is Wolfram (2025, *Communications Psychology*). From roughly 250-word essays written at age 11 by about 10,500 children in the British 1958 NCDS birth cohort, an ML model using LLM embeddings plus linguistic features predicted a measured general-cognitive-ability factor with holdout R² ≈ 0.57, which I convert to r ≈ 0.75. That is about the accuracy of teacher assessments (R² 0.62). Most other "IQ-from-text" work is small, uses proxy ground truth, or appears in low-tier venues. Evidence on adult free text (social media, chat) against real IQ tests is thin.

### Cited Findings
**Wolfram (2025): best-validated text-to-cognition study**
- Wolfram, T. (2025), "Large language models predict cognition and education close to or better than genomics or expert assessment," *Communications Psychology* 3:95 (published 3 July 2025). — [Nature/Comms Psych](https://www.nature.com/articles/s44271-025-00274-x); [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC12229686/)
- Data: National Child Development Study (NCDS), a British cohort of 17,415 children born in one week of 1958.
  - At age 11 the children wrote an essay titled "Imagine you are 25," with about 250 words requested.
  - 10,511 essays were transcribed, ranging from 1 to 1,239 words.
  - Cognitive outcomes were reading, verbal, mathematical, and non-verbal ability, plus a general cognitive ability factor at age 11; some outcomes were also measured at age 16.
  - Educational attainment was recorded at age 33. — [Europe PMC full text of Wolfram 2025](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12229686/fullTextXML)
- Methods: [same source]
  - Features were text-embedding-ada-002 embeddings (1,536 dimensions, described as GPT-3.5), compared against GPT-4 and RoBERTa embeddings.
  - The paper also used about 534 lexical diversity, sophistication, and sentiment metrics (TAALED/TAALES/SEANCE), 31 readability metrics, and grammar/typo error ratios.
  - The model was a SuperLearner ensemble (xgboost, random forest, nnet, SVM, linear), evaluated with nested cross-validation (5 inner, 10 outer folds).
  - GPT-3.5 and GPT-4 embeddings performed similarly, and both beat RoBERTa.
- Holdout R² from essays alone (NLP), compared with teacher assessment (TA) and polygenic scores (PGS): [same source]
  - General cognitive ability, age 11: NLP 0.57 (my conversion: r ≈ 0.75), TA 0.62, PGS 0.15.
  - Reading, age 11: NLP 0.59, TA 0.57.
  - Reading, age 16: NLP 0.58.
  - Verbal, age 11: NLP 0.55.
  - Maths, age 11: NLP 0.55. Maths, age 16: NLP 0.55, TA 0.62.
  - Non-verbal ability, age 11: NLP 0.37 (r ≈ 0.61), TA 0.45, PGS 0.11.
  - Educational attainment, age 33: NLP 0.26, TA 0.29, PGS 0.19.
- An ensemble combining text, teacher assessment, and genetics reached mean R² ≈ 0.70 for general cognitive ability. The author compares this to the test-retest reliability of gold-standard IQ tests. — [same source](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12229686/fullTextXML)
- A search-engine summary of the abstract gives text-based accuracy as "0.56 based on a shorter text (~250 words)." The paper's table gives 0.57; this is a minor discrepancy, possibly abstract rounding. — [Nature listing](https://www.nature.com/articles/s44271-025-00274-x)
- Embeddings carried most of the signal: adding the hand-crafted linguistic features to the embeddings gave only marginal gains. The full text model outperformed essay length alone "by a factor often exceeding 5–10." — [Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12229686/fullTextXML)
- Limitations stated by the author: [same source]
  - The study uses a single 1958 British cohort, so results may not generalize to today's pupils or other countries.
  - Non-response and missingness may bias results.
  - There was no preregistration.
  - Newer LLMs were not tested.
  - The author works for a pre-launch genomics company.

**Kosinski, Stillwell & Graepel (2013): digital footprint (Likes), not language**
- The study had 58,466 US volunteers from the myPersonality Facebook app.
  - Intelligence was measured with Raven's Standard Progressive Matrices in n = 1,350 participants.
  - Numeric traits were predicted with linear regression on SVD-reduced Likes. — [PMC3625324 (via search result summary)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3625324)
- Among the best predictors of high intelligence were Likes for "thunderstorms," "The Colbert Report," "science," and "curly fries." — [Cambridge news release](https://www.cam.ac.uk/research/news/digital-records-could-expose-intimate-details-and-personality-traits-of-millions); [PotatoPro summary](https://potatopro.com/news/2013/liking-curly-fries-indicates-you-are-smart)
- The exact r for intelligence could not be fetched (see Gaps).

**Social-media text plus LIWC (myPersonality)**
- "Mining Minds: Predicting IQ Scores Using Social Media Textual Analytics" (ACM, 2024) used myPersonality data.
  - It selected the top 25 LIWC features correlated with IQ.
  - It reports good accuracy for average IQ ranges but "challenges at the extremes." — [ACM DL](https://dl.acm.org/doi/fullHtml/10.1145/3651671.3651750)
  - The full text was blocked (HTTP 403), so the exact r, MAE, and N were not obtained.

**Stylometry "IQ estimation" (low-quality and proxy ground truth)**
- A University of Louisville thesis and related papers on automatic IQ estimation via stylometry report:
  - mean r = 0.718, RMSE = 8.695 IQ points with a multi-kernel SVR;
  - r = 0.684 with a single kernel;
  - a GRE-based experiment in which errors grew at the extremes of the IQ range.
  - Ground truth appears to be GRE-derived or estimated IQ, not a validated IQ test, so treat it as a proxy. — [Louisville ThinkIR thesis](https://ir.library.louisville.edu/cgi/viewcontent.cgi?article=4132&context=etd); [ResearchGate: Automatic IQ Estimation Using Stylometric Methods](https://www.researchgate.net/publication/332652614_Automatic_IQ_Estimation_Using_Stylometric_Methods)
- An ACM 2023 paper, "Automatic IQ Estimation from Written text using Stylometry Methods," reportedly evaluated its method on only four text samples (75% accuracy). That is far too small to be informative. — [ACM DL](https://dl.acm.org/doi/fullHtml/10.1145/3603765.3603769)
- Hendrix & Yampolskiy, "Automated IQ Estimation from Writing Samples" (MAICS 2017, CEUR Vol-1964), is a preliminary stylometry study. Its numbers could not be extracted from the PDF. — [CEUR-WS PDF](https://ceur-ws.org/Vol-1964/CS1.pdf)

**Spoken interview language (job-interview context)**
- Hickman, Tay & Woo (2025), "Are Automated Video Interviews Smart Enough? Behavioral Modes, Reliability, Validity, and Bias of Machine Learning Cognitive Ability Assessments," *Journal of Applied Psychology*, pp. 314–335, DOI 10.1037/apl0001236. — [abstract via aggregator](https://academicnewsletter.sufe.edu.cn/info/368792); [Synapse listing](https://synapsesocial.com/papers/W4402862933)
  - Verbal behavior (what interviewees said) best predicted cognitive ability.
  - Paraverbal (voice) and nonverbal (face) behavior gave no incremental validity.
  - Models were built for general mental ability, verbal ability, and zero-acquaintance-rated intellect, across two mock-interview samples. These models captured similar behavioral manifestations.
  - The exact validity coefficients were not retrievable.
- Hickman's Purdue dissertation, "Algorithmic Ability Prediction in Video Interviews," is a precursor. — [Purdue](https://hammer.purdue.edu/articles/thesis/Algorithmic_Ability_Prediction_in_Video_Interviews/14687172)

**Essays to SAT (a proxy for g)**
- Alvero et al. (2021, *Science Advances*), as summarized in Wolfram 2025:
  - College-application essays explained up to 49% of variance in SAT composite scores and 16% in household income.
  - Applicants wrote about 1,400 words each. — [Wolfram 2025 full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12229686/fullTextXML)
  - SAT is a proxy, though a heavily g-loaded one.

### Inferences
- The best validated estimate is r ≈ 0.75 (my conversion of R² 0.57) between a model's text prediction and measured g. That holds under favorable conditions:
  - a standardized prompt;
  - all writers the same age (11);
  - similar instruction context;
  - about 250 words of handwritten, effortful, schoolchild prose, which carries strong literacy and reading-skill signal;
  - training labels for thousands of people.
- Expect it to drop for adult chat logs, which are informal, short-turn, topic-heterogeneous, and possibly autocorrected or AI-assisted, and where people differ widely in education and age.
- Non-verbal (fluid) ability was predicted notably worse (R² 0.37) than verbal and reading (about 0.55–0.59). Text mainly captures crystallized and verbal ability. A text-based "IQ" estimate is therefore closer to a verbal-IQ or education-weighted estimate than to fluid g.
- Several studies independently report regression to the mean: models do well near average and poorly at the tails (Mining Minds; the Louisville stylometry work). For an IQ-estimation product, this means compressed predictions and poor discrimination exactly where users are most interested (very high or very low IQ).
- The literature has a split. Rigorous cohort work uses validated tests but child essays. Adult and online work mostly uses proxies or tiny samples.

### Gaps
- **Kosinski et al. (2013) exact intelligence accuracy.** From my recollection (unverified this session; the PNAS and PMC full text was blocked), Likes predicted Raven's-measured intelligence at r ≈ 0.39, and openness at r ≈ 0.43. Verify against PNAS DOI 10.1073/pnas.1218772110, Figure 3.
- **myPersonality status updates vs Raven's IQ.** I found no peer-reviewed paper reporting language-based (status-update) prediction of myPersonality IQ with a clear r. The ACM 2024 "Mining Minds" paper is the closest, and its numbers could not be retrieved. The myPersonality dataset was withdrawn in 2018, which limits replication.
- **Park, Schwartz, et al. (WWBP) language-based assessments.** These cover the Big Five, age, and gender. I found no WWBP paper validating language-based IQ against a test.
- **Pennebaker et al. (2014), "When small words foretell academic success."** The Categorical-Dynamic Index from admissions essays predicted GPA. This was not fetched this session, so no figures are given.
- **Hickman, Tay & Woo (2025).** Exact convergent validities (r with GMA and verbal tests) and subgroup-bias figures were not retrieved; the paywalled JAP article is needed.
- **Twitter/Reddit work.** I did not retrieve studies predicting education, occupation, or SES from Twitter or Reddit (e.g., Lampos et al.; Preoţiuc-Pietro et al.). They use proxies anyway.

---

## Q2. What does verbal-ability and vocabulary research imply? Is the vocabulary–g link leverageable from free text?

### Takeaway
Vocabulary is among the most g-loaded cognitive measures. Free text, however, measures vocabulary indirectly (words used, not words known), with topic and sampling noise. Empirically, free-text models recover a large share of verbal and reading ability in children (R² ≈ 0.55–0.59 in Wolfram 2025), but no study cleanly quantifies "free-text lexical richness vs. vocabulary test" in adults.

### Cited Findings
- Psychometric work links verbal ability and vocabulary strongly to IQ. One study of children's Wechsler scores reported a strong vocabulary–IQ correlation. — [ResearchGate: Relationship between Intelligence and Vocabulary](https://www.researchgate.net/publication/7960682_Relationship_between_Intelligence_and_Vocabulary)
- A non-peer-reviewed explainer puts vocabulary–IQ correlations at roughly r = .70–.80. Treat it with caution. — [Cogn-IQ](https://www.cogn-iq.org/learn/theory/vocabulary/)
- In Wolfram 2025, essay-based prediction was best for reading (R² 0.59 at age 11; 0.58 at age 16) and verbal ability (0.55), and weakest for non-verbal ability (0.37). — [Wolfram 2025 full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12229686/fullTextXML)
- The same study's lexical diversity and lexical sophistication metrics (TAALED/TAALES) added little beyond LLM embeddings, which captured most of the predictive information. — [same](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12229686/fullTextXML)
- In interviews, the verbal content of speech, not voice or face, carried the cognitive-ability signal (Hickman, Tay & Woo 2025). — [abstract via aggregator](https://academicnewsletter.sufe.edu.cn/info/368792)

### Inferences
- Vocabulary tests work because they sample the edges of a person's lexicon systematically with known item difficulty. Free text samples only the words a person chooses to use, and those choices are driven by topic, audience, and register; chat is low-register.
- A practical design implication for the user's project follows. Lexical sophistication from casual chat will be attenuated, and length-normalized measures (e.g., MTLD and other length-robust diversity indices; rare-word rates based on corpus frequency norms) are needed because raw type/token ratios are length-dependent.
- Embedding- or LLM-based holistic judgments appear to subsume hand-crafted lexical metrics (per Wolfram), so an LLM reading chat logs plausibly captures the vocabulary signal implicitly.

### Gaps
- I did not find a peer-reviewed study correlating lexical richness of adults' spontaneous text with a vocabulary subtest (e.g., WAIS Vocabulary) or with full-scale IQ, with explicit r and N.
- Exact g-loadings of vocabulary subtests (e.g., WAIS Vocabulary) were not retrieved from a primary source this session.

---

## Q3. Have 2023–2026 studies used LLMs to estimate intelligence from text and validated against real IQ scores? And how accurate are humans (zero-acquaintance judgments)?

### Takeaway
I found no published study (through Nov 2026) in which an LLM was prompted, zero-shot, to rate a person's IQ from their text and then validated against that person's measured IQ test score. The closest work does one of three things:
- uses LLM embeddings plus supervised ML trained on test scores (Wolfram 2025; r ≈ 0.75 for g in children's essays);
- uses supervised ML on interview speech (Hickman et al. 2025);
- uses zero-shot LLM inference for *personality*, which reaches r ≈ 0.29 average against self-report and is about as good as supervised models.

Human zero-acquaintance judges assess intelligence above chance, generally at modest accuracy (thin-slice literature), though exact pooled r for intelligence was not retrievable.

### Cited Findings
**LLM-era: what exists**
- Wolfram (2025) used LLM embeddings (ada-002 / "GPT-3.5"; GPT-4 embeddings similar; RoBERTa worse) with supervised learners trained on measured cognition: R² 0.57 for g, with about 250-word essays. This is supervised learning on embeddings, not a zero-shot LLM rater. — [Wolfram 2025](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12229686/fullTextXML)
- Peters & Matz (2024, *PNAS Nexus*) is the closest analog for zero-shot LLM trait inference.
  - GPT-3.5 and GPT-4 inferred Big Five traits from Facebook status updates (myPersonality, 2007–2012) with average r = 0.29 (range 0.22–0.33) against self-reports.
  - That is similar to supervised ML. It covers personality, not IQ. — [PMC11211928](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11211928/); [PNAS Nexus](https://academic.oup.com/pnasnexus/article/3/6/pgae231/7692212)
- A 2026 study (Matšenas et al., Univ. of Tartu) ran guided conversations with Gemini 2.5 Flash for Big Five profiling. It correlated r ≈ 0.38–0.58 with IPIP-50, N = 33. This is personality, not IQ. — [arXiv 2602.15848](https://arxiv.org/html/2602.15848)
- Another line of LLM work administers IQ-test items *to LLMs*: top models score about 125 on text-based questions and about 103 on visual questions, and an earlier study reported median converted IQs of 101–123 across five models. These are about LLM capability, not inference about humans, and are irrelevant to estimating a user's IQ. — [PsyPost](https://www.psypost.org/artificial-intelligence-models-show-massive-gaps-on-traditional-human-intelligen/); [ResearchGate preprint](https://www.researchgate.net/publication/370150050_Administration_of_the_text-based_portions_of_a_general_IQ_test_to_five_different_large_language_models)
- A related applied study tested LLM feasibility in *verbal comprehension assessment*: LLMs scoring humans' responses to verbal IQ-subtest items. This is a route to *administering* verbal tests via chat, not inferring IQ from free text. — [JMIR / PMC11894350](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11894350/)

**Human judges (zero-acquaintance / thin slices)**
- Borkenau, Mauer, Riemann, Spinath & Angleitner (2004, *JPSP* 86(4): 599–614):
  - N = 600 participants with intelligence tests, self- and peer reports.
  - Intelligence was rated from 15 videotaped episodes.
  - Thin-slice intelligence inferences "strongly predicted" test scores.
  - Accuracy rose as more episodes were aggregated, with little gain beyond 6 episodes. — [ResearchGate](https://www.researchgate.net/publication/8646931_Thin_Slices_of_Behavior_as_Cues_of_Personality_and_Intelligence); [zhenzhi abstract](https://data.zhenzhi.com/details/1/895966819); [Bielefeld record](https://pub.uni-bielefeld.de/record/1608367)
- Carney, Colvin & Hall (2007) found that intelligence (along with negative affect, extraversion, and conscientiousness) was judged "moderately well" even after 5-second exposures, and that intelligence accuracy was significantly above zero across slice lengths. — [Carney et al. preprint](http://faculty.haas.berkeley.edu/dana_carney/slices.in.press.page.numbers.oct.2007.pdf); [Columbia summary](https://business.columbia.edu/faculty/research/thin-slice-perspective-accuracy-first-impressions)
- Ambady & Rosenthal's (1992) foundational thin-slice meta-analysis (38 studies, mixed criteria, not intelligence-specific) found average accuracy around r ≈ .39–.40. Judgments from under 30 s were about as accurate as those from 5-minute observations. — [Ambady & Rosenthal 1992 PDF](https://web.mit.edu/curhan/www/docs/Articles/15341_Readings/Self-presentation_Impression_Formation/Ambady_&_Rosenthal_1992_Thin_slices.pdf); [Kenny, Interpersonal Perception](https://davidakenny.net/ip/fimp.htm)
- Murphy, Hall & Colvin (2003) is cited in later work as showing thin-slice intelligence judgments agree with targets' measured IQ. Only secondary citations were found this session. — [Murphy PSPB 2014 (EPFL)](https://infoscience.epfl.ch/record/218118/files/Murphy_PSPB_2014.pdf)
- Hall et al. (2002), a meta-analysis plus a new study, found intelligence could be judged better than chance, including from facial photographs. This is per a secondary summary. — [Simply Psychology (weak secondary)](https://www.simplypsychology.org/thin-slicing-psychology.html)

### Inferences
- The relevant benchmarks for an LLM reading chat logs are:
  - roughly r ≈ 0.3–0.5 for human/lay or zero-shot judgment of traits from brief samples (thin slices; zero-shot LLM personality r = 0.29);
  - up to r ≈ 0.75 for a supervised model trained on thousands of people's test scores with standardized writing (Wolfram).
- A zero-shot LLM IQ rater has not been validated in any study I found. Its accuracy must be established empirically against a real test (e.g., ICAR, Raven's, WAIS/WASI, Wonderlic) before any claims are made.
- Aggregation matters: Borkenau found accuracy rises with more independent behavior samples and saturates at about 6 episodes. Chat logs can provide many samples, which should help reliability, but not if all samples share the same low-register context.
- Validity of verbal content over voice and face (Hickman 2025) suggests that text transcripts carry most of the extractable signal in conversational settings.

### Gaps
- **Unverified recollections.** Borkenau et al. (2004) reported that a "reading aloud a standardized text" episode was among the most valid for intelligence, and that aggregated judgments correlated around .4–.5 with IQ. Murphy et al. (2003) found r ≈ .3. These were not confirmed: the primary PDFs were blocked or could not be parsed.
- **No meta-analysis specific to zero-acquaintance *intelligence* judgments** with a pooled r was retrieved, though Hall et al. 2002 and 2008 are referenced in secondary sources.
- **No 2023–2026 paper** validating a zero-shot LLM (GPT-4/Claude/Llama) IQ rating from chat, social posts, or essays against tested IQ was found despite multiple searches. This is either a genuine gap in the literature or very recent or unindexed work.
- I did not find human-judge accuracy studies specifically for *written text only* (e.g., raters estimating IQ from essays or chat) with tested-IQ ground truth.

---

## Q4. Clinical and cognitive-decline language markers: the more validated neighboring domain

### Takeaway
Detecting dementia or Alzheimer's from language is far more mature, with benchmark datasets and challenges. That is a classification of impairment, not estimation of normal-range IQ, and typical accuracies are about 80% (AUC about 0.88–0.92) on picture-description speech. Idea density in early-life writing (the Nun Study) is the classic longitudinal finding.

### Cited Findings
- **Nun Study and Precursors Study.** Idea density was first linked to Alzheimer's in the Nun Study, using autobiographical essays written decades before onset. The Precursors Study similarly linked lower idea density in young-adult essays to later Alzheimer's. — [Sirts, Piguet & Johnson 2017, arXiv 1706.04473](https://arxiv.org/pdf/1706.04473); [Psychiatric News](https://psychiatryonline.org/doi/10.1176/appi.pn.2016.1b4)
- **Automated idea density on transcribed speech (Sirts et al. 2017, CoNLL).** The Alzheimer's group showed significantly lower idea density than controls. The best model, adding word-embedding-cluster features, reached F = 84.8. — [arXiv 1706.04473](https://arxiv.org/pdf/1706.04473); [ACL Anthology K17-1033](https://preview.aclanthology.org/moar-dois/K17-1033.pdf)
- **ADReSS challenge** (DementiaBank Pitt Corpus Cookie Theft subset, age/gender matched):
  - BERT trained on ADReSS alone: 79.8% accuracy, 88.3% AUC.
  - Adding a Wisconsin Longitudinal Study Cookie Theft corpus: 82.1% accuracy, 92.3% AUC. — [Frontiers in Psychology 2020/2021 editorial](https://www.frontiersin.org/articles/10.3389/fpsyg.2020.624137/full); [PMC7845557](https://pmc.ncbi.nlm.nih.gov/articles/PMC7845557)

### Inferences
- The clinical domain shows that language robustly signals *large* cognitive differences (impaired vs. healthy). Even there, accuracy is about 80% on balanced, task-controlled speech (a standardized picture description). That is a useful sanity check: discriminating among healthy adults within the normal IQ range from uncontrolled chat is a harder, lower-signal problem.
- Idea density and propositional density are concrete, validated features worth including. The Nun Study shows they relate to long-run cognitive outcomes.

### Gaps
- The Nun Study's original effect sizes (Snowdon et al., 1996, *JAMA*) were not fetched this session. I am not citing specific percentages.
- I did not retrieve studies relating idea density or speech features to normal-range IQ in healthy adults (e.g., Lothian Birth Cohort speech analyses).

---

## Q5. Which confounds dominate?

### Takeaway
Text-based "IQ" signal is entangled with education, socioeconomic status, age and cohort, writing context and register, native-language (L2) status, and text length. Even in the best study, a pure sociological model (sex, parental education, social class, housing density) predicts educational attainment almost as well as essays, and essays also encode household income.

### Cited Findings
- In Wolfram 2025, a sociological baseline model predicted age-33 educational attainment with R² 0.18 (GLM) or 0.19 (SuperLearner), using sex, parental education, social class, and household density. Parental education alone reached R² 0.12. Essays reached 0.26. — [Wolfram 2025](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12229686/fullTextXML)
- Alvero et al. (2021): college-application essays predicted household income (R² up to 16%) as well as SAT (up to 49%). The text carries SES signal alongside ability signal. — [Wolfram 2025, citing Alvero et al.](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12229686/fullTextXML)
- **Text length.** In Wolfram 2025, essay length alone had some predictive value but was outperformed by the full model "by a factor often exceeding 5–10." The study requested about 250 words, and actual lengths ranged from 1 to 1,239 words. — [Wolfram 2025](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12229686/fullTextXML)
- **Generalization across era and population.** Wolfram cautions that the 1958 British cohort may not generalize to today's pupils or other countries. — [same](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12229686/fullTextXML)
- **Tail compression.** Social-media and stylometry IQ models work at average IQ but struggle at the extremes. — [ACM 2024 Mining Minds](https://dl.acm.org/doi/fullHtml/10.1145/3651671.3651750); [Louisville thesis](https://ir.library.louisville.edu/cgi/viewcontent.cgi?article=4132&context=etd)
- **Modality and bias.** Hickman et al. 2025 found verbal content sufficient and paraverbal/nonverbal cues non-incremental. Industry commentary notes voice and face cues raise bias concerns. — [abstract via aggregator](https://academicnewsletter.sufe.edu.cn/info/368792); [NACE Journal](https://naceweb.org/tag/career-development/8cc985c4-2ad7-4a10-91ac-e330de561874)
- **Language skill vs. language count.** A Manipal study of young Indian adults found no correlation between number of languages spoken and IQ. — [Manipal](https://researcher.manipal.edu/en/publications/study-of-correlation-of-the-number-of-languages-spoken-with-intel)
- **AI-assisted writing (2026).** Research reports structural convergence (homogenization) of AI-augmented student essays. LLM-edited or LLM-written chat text would erode individual-difference signal. — [arXiv 2603.21228](https://arxiv.org/pdf/2603.21228)

### Inferences
Confounds the user's chat-log project must handle:
- **Education and SES.** Text models partly measure schooling and class. Without controls, an "IQ" estimate may function as an education/SES estimate. Validation should report partial correlations controlling for education.
- **L2 and non-native writers.** Second-language writers will show lower lexical sophistication and more grammar errors regardless of g. Error-ratio and lexical features, both used by Wolfram, will be biased against them. No retrieved study quantified this for IQ prediction.
- **Register and typing context.** Chat is terse, uses abbreviations, emoji, and autocorrect, and is often mobile-typed. Models validated on essays will not transfer directly.
- **Topic and task.** A standardized prompt (Wolfram) removes topic variance. Chat logs vary in topic (work vs. social), which shifts vocabulary independently of ability.
- **Length and quantity.** Reliable estimates likely require thousands of words per person spread across contexts. Wolfram's roughly 250 words worked partly because the task was standardized and effortful.
- **Age and cohort.** Vocabulary rises with age while fluid ability declines. Models need age norming.
- **AI contamination.** Messages drafted or polished by LLMs must be excluded or flagged.
- **Restriction of range and tails.** Expect predictions to regress toward the mean. Report calibration at the tails, not just overall r.

### Gaps
- I found no study quantifying how much text-to-IQ accuracy drops for L2 writers, for mobile chat versus essays, or as a function of word count in adults.
- I found no adult study reporting text-based IQ prediction *after* partialling out educational attainment.
