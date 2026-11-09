# Measurements

Hands-on checks made during the build. Each number comes from one run unless stated, so treat them as indicative, not statistically reliable. Spec: `docs/spec.md`.

## Environment (2026-11-08)

- Apple M4 Pro, 24 GB RAM. Ollama 0.40.15 installed with Homebrew and run as a background service (`brew services`).
- Models pulled: `qwen3:14b` (9.3 GB), `bge-m3` (1.2 GB). Two older models were already present and are not used: `qwen2.5:7b`, `qwen2.5-coder:1.5b`.
- Context size left at the Ollama default for these runs.

## qwen3:14b

- Generation speed: about 25 tokens/second in all four runs, model already loaded.
- Thinking mode costs time: Vietnamese explanation took 4.0 s with thinking off and 25.5 s with it on; a tool call took 2.6 s off and 8.1 s on.
- Tool calling (one question, "Tuan 2026-W45 toi chay bao nhieu km?" in Vietnamese): the model chose `get_weekly_totals` with `week=2026-W45` and `sport=run` in both modes. One question is not enough to judge reliability.
- Vietnamese: fluent text, but the content was wrong with thinking off. Asked what a training load ratio of 0.82 means, it answered "82% of VO2max / maximum". Per COROS the ratio is the 7-day load divided by the 42-day base load. With thinking on the answer was closer (relative to long-term load) but added "lower injury risk", a claim the research found contested.
- Conclusion for the design: do not let the model explain training metrics from its own knowledge. Use COROS status labels and sourced guidance cards (spec: Advice).

## bge-m3 (embeddings)

- Returns 1024-dimension vectors, normalised (length 1.0). Two short inputs took about 1.2 s in total (first call, may include model load).
- Cosine similarity between an English template summary and a Vietnamese sentence about a similar run: 0.489. There is no baseline yet, so this says nothing about quality; the 20-question evaluation will.

## Data pulls and search (2026-11-08)

- COROS connector: about 4 of 30 calls returned a generic "Tool call anomalies detected" text instead of data; retrying worked. Calls made in parallel batches of 14-16 were hit most.
- Activity list, 12 months, limit 300: 171 records, 56 KB of text (saved to a file by the harness because it exceeded the output limit).
- Daily training load requested for 56 days returned 31 days; resting HR for 56 days returned 2 values; sleep HRV for 7 days returned none.
- Loaded totals: lap distance and time sums matched activity totals within 0.003 km and 1 s.
- Exact vector search (no index) over 171 activity summaries and 50 weekly summaries, `bge-m3`, a handful of queries, no systematic scoring:
  - Works for categories: "hard anaerobic interval session" ranked the Anaerobic run first; "swimming in open water" returned only swims; "long run about 10 km" returned mostly runs near 10 km.
  - Weak for numbers: a query copying the template of a 4 km, 10:20/km, HR 108 recovery run did not return the real recovery run in its top 4; "week with load ratio decreasing and little training" returned weeks with 15-17 km of running.
  - Cosine distances: about 0.16-0.18 for a template-style English query that matched in form, 0.35-0.41 for Vietnamese queries against English summaries.

## Still to measure

- Longer prompts with real tool sets, context size effects on speed and memory, SQL writing quality, matplotlib code quality, tool choice across many questions.
- Memory use while `qwen3:14b` and `bge-m3` are both loaded.
- Embedding comparison on the owner's data (bge-m3 against 1-2 other models).
