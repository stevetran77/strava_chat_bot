---
title: "Choose the local LLM"
label: wayfinder:grilling
status: closed
blocked_by: [02-research-local-llm]
assignee: stevetran
---

## Question

- Which local model and runtime (Ollama vs MLX) does the chatbot use, given tool-calling reliability, Vietnamese quality, and speed on the user's machine?

## Resolution

- Runtime: Ollama (also serves the `bge-m3` embedding model).
- Primary model: `qwen3:14b` (tool-calling label on Ollama, Vietnamese listed by Qwen, Apache 2.0, fits 24 GB). Fallback: `gpt-oss:20b`; `gemma3:12b` and `llama3.1:8b` are weaker candidates (tool calling unverified / Vietnamese not listed).
- Decision locked now, measured later: the spec includes a small bake-off (speed, Vietnamese quality, tool-calling reliability) and swaps the model if results are poor.
- Settings to keep configurable, not hardcoded: model name, context size (Ollama default `num_ctx` is 4096; set explicitly after measuring).
- Open: real speed on this machine, Vietnamese quality, whether qwen3 reasoning mode needs to be on or off for tool calling.
