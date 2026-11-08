---
ticket: tickets/02-research-local-llm.md
date: 2026-11-08
status: findings (primary sources only; gaps marked UNVERIFIED)
---

# Local LLMs on Apple M4 Pro, 24 GB

Legend: [V] = stated by a primary source (linked). [D] = derived by me from [V] facts (arithmetic, not measured). [U] = UNVERIFIED.

## Bottom line (for ticket 06)

- Best-fit candidate: **Qwen3 14B (Q4_K_M, 9.3 GB)** via Ollama. Fits with room for KV cache, has tools + thinking tags, Apache 2.0, Vietnamese explicitly listed by Qwen.
- Alternative: **Qwen3 30B-A3B (MoE, 19 GB)**: 3B active params so likely faster per token [D], but 19 GB weights leave little headroom on 24 GB [D].
- Gemma 3 12B (8.2 GB): strong multilingual claim (140+ languages) but **no "tools" tag on Ollama** [V]; would need prompt-based tool use [D].
- Llama 3.1 8B: Vietnamese **not** in officially supported languages [V]; weakest fit for the Vietnamese requirement.
- No primary source gives tokens/sec for these models on M4 Pro. Speed figures below are [D] estimates; must be measured at build time.

## 1. What fits in 24 GB

Download sizes are Ollama default quant tags (Q4_K_M for Qwen3, per the model pages).

| Model (Ollama tag) | Size on disk | Notes |
|---|---|---|
| qwen3:8b | 5.2 GB | comfortable |
| qwen3:14b | 9.3 GB | comfortable, recommended starting point |
| qwen3:30b (30.5B MoE, 3.3B active) | 19 GB | tight: [D] leaves ~5 GB total for macOS, apps, KV cache |
| qwen3:32b | 20 GB | tight, dense so slow [D] |
| gemma3:12b | 8.2 GB | comfortable |
| gemma3:27b | 17 GB | feasible but tight with context [D] |
| llama3.1:8b | 4.9 GB | comfortable |
| gpt-oss:20b | 14 GB | feasible |
| 70B-class (llama3.1:70b 43 GB, gpt-oss:120b 65 GB) | 43-65 GB | do NOT fit |

Sources: [qwen3 tags](https://ollama.com/library/qwen3), [qwen3:14b](https://ollama.com/library/qwen3:14b), [qwen3:30b](https://ollama.com/library/qwen3:30b), [gemma3](https://ollama.com/library/gemma3), [llama3.1](https://ollama.com/library/llama3.1), [gpt-oss](https://ollama.com/library/gpt-oss).

Memory caveats:
- Unified memory is shared with macOS and the app. MLX-LM docs say large models may run slowly unless the GPU wired memory limit is raised with `sudo sysctl iogpu.wired_limit_mb=N` (macOS 15+), with N above model size and below total RAM [V: [mlx-lm README](https://github.com/ml-explore/mlx-lm/blob/main/README.md)]. The default wired limit on a 24 GB Mac is [U] (not found in primary sources fetched).
- KV cache grows with context and parallel requests: RAM scales with `OLLAMA_NUM_PARALLEL x OLLAMA_CONTEXT_LENGTH` [V: [Ollama FAQ](https://docs.ollama.com/faq)].
- KV cache quantization: `OLLAMA_KV_CACHE_TYPE` f16 (default), q8_0 (~half memory, little quality loss), q4_0 (~quarter, small-to-medium loss). Works best with flash attention, which Ollama enables automatically when supported [V: Ollama FAQ].
- Single-user app: set `OLLAMA_NUM_PARALLEL=1` to save memory [D].

## 2. Tokens/sec expectations

- Only primary benchmark found: llama.cpp discussion #4167, **Llama 2 7B on M4 Pro (273 GB/s)**, build 8e672ef (Nov 2023, old build; newer builds are faster) [V: [llama.cpp #4167](https://github.com/ggml-org/llama.cpp/discussions/4167)]:

| GPU cores | Quant | Prompt (PP512) t/s | Generation (TG128) t/s |
|---|---|---|---|
| 16 | Q4_0 | 364 | 49.6 |
| 16 | Q8_0 | 367 | 30.5 |
| 20 | Q4_0 | 440 | 50.7 |
| 20 | Q8_0 | 450 | 30.7 |

- Which M4 Pro variant (16 or 20 GPU cores) the owner has: [U]; check with `system_profiler SPDisplaysDataType` at build time.
- Derived estimate [D]: token generation is memory-bandwidth bound, so t/s scales roughly with 1 / (bytes read per token). Measured Q4_0 7B (~3.8 GB) reached ~50 t/s, i.e. roughly 70% of the 273 GB/s ceiling. Applying the same ratio:
  - qwen3:8b (5.2 GB): ~25-35 t/s
  - qwen3:14b (9.3 GB): ~15-22 t/s
  - gemma3:12b (8.2 GB): ~17-25 t/s
  - qwen3:30b MoE (3.3B active, roughly 2 GB read per token): possibly 40+ t/s, but MoE routing overhead makes this the least certain number [U]
  - dense 27B-32B (17-20 GB): ~8-11 t/s
- All [D] figures are NOT measured and not from a primary source. Treat as order of magnitude; benchmark with `ollama run <model> --verbose` before deciding (ticket 06 / build phase).
- Thinking mode (Qwen3, gpt-oss) emits hidden reasoning tokens first, so wall-clock latency per answer is higher than the t/s suggests [D].
- MLX vs Ollama speed on M4 Pro: no primary benchmark found [U]. MLX-LM is installable via `pip install mlx-lm` (quantize with `mlx_lm.convert -q`) [V: mlx-lm README]. Note: ticket context says python3 is 3.9.6; mlx-lm's Python requirement is [U] (not stated in the fetched README), likely needs a newer Python [U].

## 3. Tool / function calling

- Ollama supports tool calling in its API: send `tools` (name, description, JSON-schema params); model returns `tool_calls`; you run them and send back `role: tool` messages. Supports parallel calls, multi-turn agent loops, and streaming [V: [Ollama tool calling docs](https://docs.ollama.com/capabilities/tool-calling)].
- Docs examples use only `qwen3`; agent loop has no built-in iteration limit (add one ourselves) [V: same page].
- Per-model capability tags on Ollama:
  - qwen3 (all sizes, incl. 14b and 30b): `tools`, `thinking` [V: [qwen3:14b](https://ollama.com/library/qwen3:14b), [qwen3:30b](https://ollama.com/library/qwen3:30b)]
  - llama3.1: `tools` [V: [llama3.1](https://ollama.com/library/llama3.1)]
  - gpt-oss: `tools`, `thinking` [V: [gpt-oss](https://ollama.com/library/gpt-oss)]
  - gemma3: only `vision` listed, no `tools` [V: [gemma3](https://ollama.com/library/gemma3)]. Google's Gemma 3 docs page fetch failed (HTTP 502) and the HF model card has no function-calling statement, so native Gemma 3 tool support is [U].
- Qwen's model card says "Qwen3 excels in tool calling" and recommends Qwen-Agent [V: [Qwen3-14B card](https://huggingface.co/Qwen/Qwen3-14B)]. Real-world reliability on this project's tools (SQL query, vector search) is [U]; test in evaluation set.
- Llama 3.1 card reports tool-use benchmarks (BFCL, API-Bank) [V: [Llama-3.1-8B-Instruct](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct)].
- mlx_lm.server tool-calling / OpenAI-compatible support: not covered in the README fetched [U]. Ollama is the safer route for tool calling.

## 4. Vietnamese and English quality

- Qwen3: 119 languages and dialects; **Vietnamese explicitly listed** (Austroasiatic family) [V: [Qwen3 blog](https://qwenlm.github.io/blog/qwen3/)]. Qwen3 HF card and GitHub README only say "100+ languages" without naming Vietnamese [V]. No Vietnamese-specific benchmark scores found [U].
- Gemma 3: "multilingual support in over 140 languages" [V: [gemma-3-12b-it card](https://huggingface.co/google/gemma-3-12b-it)]. Vietnamese not named on the card [U]; card notes safety evals used English-only prompts [V].
- Llama 3.1: officially supports English, German, French, Italian, Portuguese, Hindi, Spanish, Thai. **Vietnamese not included**; Meta discourages use in unsupported languages without fine-tuning [V: Llama-3.1-8B-Instruct card].
- gpt-oss: language support not on the Ollama page fetched [U].
- Actual Vietnamese answer quality for Strava coaching text on these models: [U]. Needs a small hands-on Vietnamese test set (belongs to the "evaluation question set" item in the map).

## 5. Context window

- Model capability [V]:
  - Qwen3-14B: 32,768 native, 131,072 with YaRN (static; may hurt short-text quality, enable only if needed) [Qwen3-14B card]. The Qwen blog table lists 128K for 8B/14B/32B/30B-A3B and 32K for 4B and below [Qwen3 blog]. The Ollama page lists 40K for 14b/8b/32b [V: qwen3 tags].
  - Qwen3-30B-A3B: 32,768 native, 131,072 with YaRN [V: [HF card](https://huggingface.co/Qwen/Qwen3-30B-A3B)]
  - Gemma 3 12B/27B: 128K input, 8,192 output cap [V: gemma-3-12b-it card]
  - Llama 3.1 8B: 128K [V: HF card]
  - gpt-oss 20b: 128K [V: Ollama page]
- **Ollama runtime default is lower than model capability**: Ollama FAQ says default `num_ctx` is 4096 [V: Ollama FAQ]; Qwen3 README (older) says 2048 [V: [Qwen3 README](https://github.com/QwenLM/Qwen3/blob/main/README.md)]. Discrepancy likely reflects Ollama version changes; the current default for the installed version is [U]. Set it explicitly (`OLLAMA_CONTEXT_LENGTH`, `num_ctx` in API options).
- Qwen README warns Ollama's context-shifting can misbehave with Qwen3 and recommends setting `num_ctx` and `num_predict` explicitly (example 40960 / 32768) [V: Qwen3 README].
- Sizing for this project [D]: a Q&A over activity summaries needs small prompts (tool results + a few retrieved activities). 8K-16K context is likely enough, which keeps KV cache small. Exact need depends on ticket 05 schema [U].

## 6. Licenses

| Model | License | Source |
|---|---|---|
| Qwen3 dense (0.6B-32B) | Apache 2.0 | [Qwen3 blog](https://qwenlm.github.io/blog/qwen3/), [README](https://github.com/QwenLM/Qwen3/blob/main/README.md) ("all open-weight models Apache 2.0") |
| Qwen3-30B-A3B | Apache 2.0 | Ollama qwen3:30b page shows Apache 2.0 text; blog does not state MoE license but README says all open-weight |
| Gemma 3 | Google Gemma Terms of Use + Prohibited Use Policy (gated on HF, must accept) | [gemma-3-12b-it card](https://huggingface.co/google/gemma-3-12b-it), terms: ai.google.dev/gemma/terms (not fetched) |
| Llama 3.1 | Llama 3.1 Community License (custom) | [HF card](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct) |
| gpt-oss | not stated on the Ollama page [U] | |

- Personal single-user local use: all of the above are likely permissive enough [D]; license text not reviewed in detail for Gemma/Llama [U].

## 7. Gotchas to carry into ticket 06

- Ollama tag drift: as of Aug 2025 `qwen3:30b-a3b` pointed to a Qwen3-2507 thinking build, tags may not match Qwen naming; check the tags page at install time [V: Qwen3 README]. The tag sizes/context on the Ollama qwen3 page (256K for 4b and 30b) hint at 2507 variants under those tags [D, U].
- Ollama version: Qwen README recommends >= 0.9.0 for Qwen3 [V]. MLX-LM >= 0.24.0 for Qwen3 [V].
- Thinking mode: toggle with `/think` `/no_think` or `enable_thinking=False` (Qwen3) [V: Qwen3-14B card]; consider off for simple routing/tool-selection to cut latency [D].
- Out of scope per map: Claude API / paid LLMs; gpt-oss `*-cloud` tags are cloud-hosted and must be excluded [V: gpt-oss page lists them].

## Unverified summary

- Any tokens/sec for Qwen3 / Gemma 3 / gpt-oss on M4 Pro (only Llama 2 7B measured, old build).
- Owner's GPU core count (16 vs 20) and default macOS GPU wired memory limit.
- Gemma 3 native tool calling; gpt-oss language support and license.
- Vietnamese quality benchmarks for any candidate.
- Current Ollama default `num_ctx` for the version to be installed.
- MLX-LM server tool calling, Python version requirement, MLX vs Ollama speed on M4 Pro.
- Which Qwen release (2504 vs 2507) the Ollama `qwen3:14b` / `qwen3:30b` tags currently map to.
