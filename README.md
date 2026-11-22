# LLM-IQ

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24448787.svg)](https://doi.org/10.5281/zenodo.24448787)

Can an LLM judge someone's IQ (or EQ) from their chat records? This project looks at that question
in two parts:

- **Research** on prior work, accuracy, the validity of "EQ", bias, law and ethics, ending with what is
  worth building: [`reports/IQ and EQ from chat logs.md`](reports/IQ%20and%20EQ%20from%20chat%20logs.md),
  with the underlying notes in `research_notes/`. Short answer: nobody has validated an LLM's IQ guess from
  chats against real test scores.
- **[`iq-audit-harness/`](iq-audit-harness/)**, the tool the research recommended building first: an audit
  of what moves an LLM's IQ number when the content of a chat stays the same (dialect, non-native English,
  Chinese, jargon, pasted text, flattering prompts). Synthetic chats only. See its README for results
  so far and how to run it.
