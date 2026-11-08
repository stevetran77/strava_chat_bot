---
title: "Research: Local LLMs on M4 Pro 24 GB"
label: wayfinder:research
status: closed
blocked_by: []
assignee: research-subagent
---

## Question

- Which open-source models can run locally (Ollama or MLX) on Apple M4 Pro, 24 GB RAM?
- Cover: model size that fits, tokens/sec expectations, tool/function-calling support, Vietnamese and English quality, context window, licenses.
- Output: findings file at `docs/wayfinder/research/02-local-llm.md`, primary sources only (model cards, Ollama docs), with links. State what is unverified.

## Resolution

- Findings: `../research/02-local-llm.md`. Fits 24 GB: qwen3:14b, gemma3:12b, llama3.1:8b, gpt-oss:20b. Tool calling listed for qwen3, llama3.1, gpt-oss. Vietnamese named for Qwen3 only. Agent leans qwen3:14b on Ollama.
- Open: real speed on this machine, Vietnamese quality, MLX tool calling, `num_ctx` (default 4096).
