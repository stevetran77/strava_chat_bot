---
title: "Research: Local multilingual embedding models"
label: wayfinder:research
status: closed
blocked_by: []
assignee: research-subagent
---

## Question

- Which embedding models run locally (free) and handle Vietnamese + English well?
- Cover: model candidates (e.g. via Ollama / sentence-transformers), dimensions, size, multilingual benchmark evidence (e.g. MTEB), license, speed on M4 Pro.
- Output: findings file at `docs/wayfinder/research/03-embedding-models.md`, primary sources only, with links.

## Resolution

- Findings: `../research/03-embedding-models.md`. Shortlist: bge-m3, multilingual-e5-large-instruct, Qwen3-Embedding-0.6B, EmbeddingGemma-300M. VN-MTEB: m-e5-large-instruct 67.99, bge-m3 64.90 (machine-translated data).
- Open: speed/memory on M4 Pro, Vietnamese quality of Qwen3/EmbeddingGemma, Python 3.9 compatibility.
