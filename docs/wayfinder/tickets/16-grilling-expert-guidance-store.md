---
title: "Expert guidance store and citation"
label: wayfinder:grilling
status: closed
blocked_by: [15-research-running-expert-guidance]
assignee: stevetran
---

## Question

- How does expert guidance enter the system: curated short notes (paraphrased, each with a source) stored and embedded in the vector database so the LLM retrieves them for advice questions?
- How are guidance and the owner's own numbers combined in one answer, how is the source cited, and what happens when sources disagree or contradict a COROS label?
- Who curates the notes and how are they updated.

## Resolution

- Storage: a `guidance_cards` table in the same Postgres database (adds a fifth table to the schema decided in the schema ticket). Each card is a short paraphrase with: topic, content, source (DOI or link), related metric (load ratio, HRV, taper, ...), consensus level (consensus / mixed / contested), and a `bge-m3` embedding.
- Retrieval: a `search_guidance` vector-search tool added to the tool set from the routing ticket. For advice questions the LLM calls it together with the data tools and combines both.
- Conflicts: the COROS status label is the basis for "where you are now"; cards inform "what to do". When sources disagree or a card is contested, the answer says so briefly instead of picking a side. The model is not the judge between studies.
- Curation: cards come from peer-reviewed papers, COROS pages and sports-science bodies. During the build Claude drafts cards from the sourced research (paraphrased, one link each) and the owner approves every card before it enters the DB. No source, no card. Coach-book ideas are allowed only as the owner's own paraphrase with book and chapter. Number of cards decided at build.
- Open: COROS band figures to recheck against live pages; abstracts-only reading of academic sources.
