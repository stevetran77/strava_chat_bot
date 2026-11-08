---
title: "Advice and analysis guardrails"
label: wayfinder:grilling
status: closed
blocked_by: []
assignee: stevetran
---

## Question

- How far does the chatbot go beyond statistics: overtraining checks, training suggestions, comments on heart rate or recovery?
- Decide: which inputs it may use (load ratio, resting HR, HRV, recent volume), how it states uncertainty, what it must not say (medical advice, diagnoses), and whether answers cite the numbers behind a suggestion.
- A 14B local model can sound confident and be wrong: decide how advice answers are checked in the evaluation step.

## Resolution

- Scope (owner choice, beyond the recommendation): descriptive stats, evidence-backed observations, and concrete training suggestions (e.g. next week). Suggestions are text only; the project never writes to COROS (no plan or workout creation tools).
- Judging basis: COROS labels and metrics (load comment, load ratio, short/long-term load, resting HR, HRV) plus guidance taken from running experts, used as the reference for assessments. Which experts and sources, and how that guidance is stored and cited, is not decided here: see the research and grilling tickets on expert guidance.
- Uncertainty: advice and observation answers end with one short line (based on COROS metrics, not medical advice). Plain statistics answers do not.
- Never say: diagnoses of illness or injury, heart/medical conclusions, medication or diet advice. Such questions are declined politely with a pointer to a professional; relevant numbers can still be shown on request.
- Evidence: every advice answer cites the numbers and dates from the tool results; if data is missing it says "not enough data". The evaluation set includes advice cases: missing data, medical questions (must decline), and different load-ratio levels.
- Open: a 14B model's reliability at advice; expert-guidance sourcing (new tickets).
