---
title: "Research: Local vector DB options"
label: wayfinder:research
status: closed
blocked_by: []
assignee: research-subagent
---

## Question

- Compare local, free vector DBs for a small personal dataset (thousands of items): Chroma, LanceDB, sqlite-vec, pgvector, and any other strong option.
- Cover: setup effort, metadata filtering, hybrid with SQL, persistence, Python API, what each teaches about vector DB concepts (indexes, distance metrics).
- Output: findings file at `docs/wayfinder/research/04-vector-db.md`, primary sources only (official docs), with links.

## Resolution

- Findings: `../research/04-vector-db.md`. sqlite-vec fits hybrid SQL best but is pre-v1 and needs non-system Python. LanceDB, Chroma, pgvector teach index concepts better.
- Open: several items marked `[UNVERIFIED]` in the file; recheck key defaults against linked docs.
