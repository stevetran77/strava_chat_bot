# Research 03: Local multilingual embedding models (Vietnamese + English)

Date: 2026-11-08. Ticket: `tickets/03-research-embedding-models.md`.
Legend: [V] verified on a primary source (link given). [U] unverified / not found in a primary source.

## Summary

- Shortlist: `bge-m3`, `multilingual-e5-large-instruct`, `Qwen3-Embedding-0.6B`, `EmbeddingGemma-300M`. `nomic-embed-text-v2-moe` is a weaker-evidence extra.
- Only one primary source tests Vietnamese directly: the VN-MTEB paper (Table 3). There, `m-e5-large-instruct` (67.99 avg) > `bge-m3` (64.90). Qwen3-Embedding and EmbeddingGemma were NOT in that table.
- Easiest path in Ollama: `bge-m3` (1.2 GB), `qwen3-embedding:0.6b` (639 MB), `embeddinggemma` (622 MB). `multilingual-e5-large-instruct` is not confirmed in Ollama [U]; use sentence-transformers.
- Speed on M4 Pro: no primary benchmark found [U]. Must be measured on the owner's machine.
- Data here is short activity text, so context length (512 to 8K) is not a constraint for any candidate.

## Candidate comparison

| Model | Params | Dim | Max input | License | Ollama (size) | Prefix/instruction needed |
|---|---|---|---|---|---|---|
| BAAI/bge-m3 | 567M [V] | 1024 [V] | 8192 [V] | MIT [V] | `bge-m3`, 1.2 GB [V] | No [V] |
| intfloat/multilingual-e5-large-instruct | ~560M [V] | 1024 [V] | 512 [V] | MIT [V] | not found [U] | Yes, queries: `Instruct: {task}\nQuery: {q}`; docs none [V] |
| Qwen/Qwen3-Embedding-0.6B | ~596M [V] | up to 1024, MRL 32-1024 [V] | 32K [V] | Apache-2.0 [V] | `qwen3-embedding:0.6b`, 639 MB [V] | Optional but recommended (+1-5%, English instructions) [V] |
| google/embeddinggemma-300m | ~303M [V] | 768, MRL to 512/256/128 [V] | 2048 [V] | Gemma terms (gated; not OSI open source) [V] | `embeddinggemma`, 622 MB [V] | Yes, `task: search result \| query: ` / `title: none \| text: ` [V] |
| nomic-ai/nomic-embed-text-v2-moe | 475M total, 305M active [V] | 768, MRL to 256 [V] | 512 [V] | Apache-2.0 [V] | `nomic-embed-text-v2-moe`, 958 MB [V] | Yes, `search_query: ` / `search_document: ` [V] |

Notes:
- License column comes from the Hugging Face API metadata (`license` field), not the model-card prose, which often omits it.
- EmbeddingGemma: do not use float16 (use float32 or bfloat16) per the model card.
- nomic v2 needs `trust_remote_code=True` in sentence-transformers.
- bge-m3 also offers sparse and multi-vector (ColBERT) outputs via FlagEmbedding. Relevant to the vector-DB ticket (04) only if hybrid sparse+dense is wanted.

## Vietnamese evidence

### Direct (VN-MTEB, arXiv 2507.21500, Table 3, 41 Vietnamese datasets, machine-translated from MTEB) [V]

| Model | Params | Dim | Retrieval (15 ds) | Clustering | STS | Avg (41) |
|---|---|---|---|---|---|---|
| m-e5-large-instruct | 560M | 1024 | 40.88 | 52.96 | 82.94 | 67.99 |
| bge-m3 | 568M | 1024 | 39.84 | 45.90 | 78.84 | 64.90 |
| gte-multilingual-base | 305M | 768 | 38.38 | 50.25 | 81.51 | 65.22 |
| m-e5-large (non-instruct) | 560M | 1024 | 37.65 | 45.78 | 80.65 | 63.87 |
| m-e5-base | 278M | 768 | 34.50 | 45.70 | 79.45 | 62.42 |

- Caveats [V from paper, interpretation mine]: the benchmark data is machine-translated, not native Vietnamese. Differences of about 1 point on Retrieval are small.
- Qwen3-Embedding, EmbeddingGemma and nomic v2 are not in this table [U for their Vietnamese quality].
- Source: https://arxiv.org/abs/2507.21500 (PDF: https://arxiv.org/pdf/2507.21500).

### Indirect (multilingual aggregate)

- Qwen3-Embedding model card, MTEB (Multilingual) table [V]:
  - Qwen3-Embedding-0.6B: Mean(Task) 64.33, Retrieval 64.64.
  - multilingual-e5-large-instruct: 63.22, Retrieval 57.12.
  - BGE-M3: 59.56, Retrieval 54.60.
  - Self-reported by Qwen; averages across many languages, Vietnamese not isolated.
  - Source: https://huggingface.co/Qwen/Qwen3-Embedding-0.6B
- EmbeddingGemma card, MTEB Multilingual v2, 768d: Mean(Task) 61.15 [V]. Source: https://huggingface.co/google/embeddinggemma-300m. Note the Qwen card's table is a different score set, so do not compare these two numbers across cards directly [interpretation].
- nomic v2 card [V]: BEIR 52.86, MIRACL 65.80 vs mE5 Large 51.40 / 66.50 and BGE M3 48.80 / 69.20. Source: https://huggingface.co/nomic-ai/nomic-embed-text-v2-moe
- Vietnamese is not in the MIRACL language set [U: from my memory of MIRACL, not checked on a source here], so MIRACL numbers say little about Vietnamese.
- Language lists: the e5 and nomic v2 HF metadata list `vi` explicitly [V via HF API]. bge-m3, Qwen3 and EmbeddingGemma cards claim "100+ languages" without naming Vietnamese [V that it is unnamed; Vietnamese support itself is therefore unconfirmed on the cards].

## Running locally

- Ollama (not installed on the owner's machine per map): `bge-m3`, `qwen3-embedding` (tags `0.6b`, `4b`, `8b`), `embeddinggemma` (needs Ollama >= 0.11.10), `nomic-embed-text-v2-moe` are all in the library [V].
  - https://ollama.com/library/bge-m3
  - https://ollama.com/library/qwen3-embedding
  - https://ollama.com/library/embeddinggemma
  - https://ollama.com/library/nomic-embed-text-v2-moe
- sentence-transformers: all five load via `SentenceTransformer(...)` [V per cards]. Qwen3 needs `transformers>=4.51.0`, `sentence-transformers>=2.7.0` [V]. The map notes python3 is 3.9.6; compatibility of those versions with 3.9 is [U] and should be checked when setting up the environment.
- Sizes on disk: Ollama sizes above are the quantized/packaged downloads [V]. RAM at inference not found on primary sources [U]; all are under 1 GB on disk, well inside 24 GB.
- Ollama page for bge-m3 says "updated 2 years ago" [V], which is just a freshness note.

## Speed on M4 Pro

- No primary-source benchmark for these models on M4 Pro or Apple Silicon found [U].
- Not estimated here. Recommend measuring: embed the owner's real activity texts (likely a few thousand short strings) with 2-3 finalists and time it. Ticket 07 can include that as a check.

## Observations for ticket 07 (not decisions)

- If Vietnamese retrieval quality is the top criterion, the only direct evidence favors `multilingual-e5-large-instruct`, then `bge-m3`.
- `bge-m3` has the simplest operations: Ollama, no prefixes, MIT, 8K context, sparse option.
- `Qwen3-Embedding-0.6B` has the best multilingual aggregate and Apache-2.0, but no direct Vietnamese result found [U].
- `embeddinggemma` is smallest with 768 dims, but has Gemma usage terms and a 2K context.
- A cheap, decisive step: build a small Vietnamese+English query set from the owner's own activities and compare 2-3 models (ties into the "Evaluation question set" item in the map).

## Gaps / not verified

- Vietnamese scores for Qwen3-Embedding, EmbeddingGemma, nomic v2: not found in a primary source. [U]
- MTEB leaderboard (https://huggingface.co/spaces/mteb/leaderboard) is a dynamic app and could not be read via fetch; no leaderboard numbers were used.
- Whether `multilingual-e5-large-instruct` is available in Ollama: not found. [U]
- Speed and memory on M4 Pro: [U].
- Python 3.9 compatibility of required library versions: [U].
