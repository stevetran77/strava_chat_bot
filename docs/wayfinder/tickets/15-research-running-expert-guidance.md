---
title: "Research: Running expert guidance sources"
label: wayfinder:research
status: closed
blocked_by: []
assignee: research-subagent
---

## Question

- Which high-trust sources of running training guidance can the chatbot lean on for assessments and suggestions: load progression, recovery, easy vs hard days, tapering, reading HR/HRV/load ratio?
- Cover: candidate sources (peer-reviewed papers, sports-science bodies, well-known coaches' published methods), what each recommends in checkable terms, where sources disagree, and copyright limits on storing their text locally (paraphrase with citation versus copying).
- Cover how COROS defines its load metrics and labels, from COROS's own documentation if it exists.
- The owner may have specific coaches or books in mind: list candidates and let the owner add or veto sources.
- Output: findings file at `docs/wayfinder/research/15-running-expert-guidance.md`. Primary sources only, with links; mark unverified items. No medical claims beyond what the sources state.

## Resolution

- Findings: `../research/15-running-expert-guidance.md`. COROS defines its own load metrics and labels (Intensity Trend = Load Impact / Base Fitness; bands Decreasing, Resuming/Performance, Maintaining 80-99%, Optimized 100-149%, Excessive 150%+; recovery bands). HRV and resting HR have no numeric cut-offs, so use the owner's baseline and trend.
- Literature: acute/chronic load and the 10% rule are contested; taper size varies between sources; 80/20 and polarized training are supported. Coach books are unverified candidates.
- Storage: paraphrased "guidance cards" with DOI or link; no copied text.
- Open: COROS figures need rechecking against live pages (support pages returned 502); academic sources read via abstracts only; COROS terms of use and legal side unchecked.
