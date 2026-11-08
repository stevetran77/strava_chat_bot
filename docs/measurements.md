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

## Still to measure

- Longer prompts with real tool sets, context size effects on speed and memory, SQL writing quality, matplotlib code quality, tool choice across many questions.
- Memory use while `qwen3:14b` and `bge-m3` are both loaded.
- Docker container start-up latency for the chart sandbox.
- Embedding comparison on the owner's data (bge-m3 against 1-2 other models).
