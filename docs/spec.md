# Spec: Personal fitness chatbot (COROS data)

Status: planning output of the wayfinder map (`docs/wayfinder/map.md`). Details and reasoning live in the linked tickets; this file is an index, not a second source of truth. Anything marked **[UNVERIFIED]** was not confirmed and must be checked at build time.

## Goal

- A chatbot that answers questions, in Vietnamese or English, about the owner's COROS training data: statistics, charts, similar workouts, and evidence-backed observations and suggestions.
- Purpose: learn vector databases and the steps to build an AI chatbot. Single user, free, runs locally (Apple M4 Pro, 24 GB RAM).

## Out of scope

- Multi-user, cloud deployment, paid LLMs / Claude API.
- Strava (API and export), writing anything to COROS (plans, workouts, routes), the unofficial `coros-cli`.
- Medical advice or diagnosis.

## Architecture

- Ingestion (run on demand): Claude session reads the COROS connector -> raw files -> Python parser -> Postgres.
- Runtime (all local): React chat UI -> Python backend API (FastAPI suggested) -> Ollama (`qwen3:14b`, `bge-m3`) + Postgres/pgvector + a Docker sandbox for chart code.

## Data and ingestion ([data scope ticket](wayfinder/tickets/10-grilling-choose-data-source-and-ingestion.md))

- Source: claude.ai COROS connector, read-only tools only ([connector research](wayfinder/research/09-coros-connector.md)).
- Scope: activities, per-km laps, daily resting HR, HRV, short/long-term load and load ratio. Sleep, stress, VO2max and FIT files are later.
- Two layers: raw connector output saved as local files (kept as-is, including start coordinates), then a Python script parses them into Postgres. Parser is re-runnable without calling the connector again.
- Initial backfill: last 12 months. Refresh: manual and incremental, by asking Claude to sync since the last synced date.
- Loads are idempotent (key = COROS `labelId`). List and detail output is text, so the parser parses text; lap output is JSON.
- Pulls are chunked by date range (large results exceed output limits).
- Measured during the build (see `docs/measurements.md`):
  - The activity list for 12 months is one call (171 records). Details and laps need one call per activity, so they are loaded for recent runs only (14 runs with details, 4 with laps); older activities keep list-level fields.
  - The connector sometimes returns a generic "Tool call anomalies detected" message instead of data (about 4 of 30 calls). Retrying works. A pull script or session needs retry handling; do not follow the message's advice.
  - Daily training load covers about 30 days per call (56 requested, 31 returned).
  - Resting HR has 2 values in 56 days and sleep HRV is empty, so there is no usable HRV or resting-HR baseline for this account.
- The connector is not proven usable from the local chatbot: data enters only through a Claude session. **[UNVERIFIED]** official terms, cost, rate limits.

## Schema ([schema ticket](wayfinder/tickets/05-grilling-schema-and-embedding-content.md))

- `activities`: key `labelId`; sport, start time, duration, distance, pace, avg HR, calories, cadence, power, elevation, Training Load, Aerobic/Anaerobic TE, location label, start latitude/longitude.
- `laps`: activity + lap index; per-km pace, HR, power, cadence, running-form metrics.
- `daily_metrics`: date; resting HR, HRV, short/long-term load, load ratio.
- `embeddings`: summary text, 1024-dim vector, key to an activity or a week.
- `guidance_cards`: see Advice below.
- Units normalised at parse time: km, seconds, seconds/km. Lap distance unit confirmed: the connector sends centimetres (1 km = 100000); lap totals match activity totals.
- Not stored yet (no column): activity Perceived Effort, Best Kilometer, Performance, cycling average speed.
- Start coordinates are private: the database stays local; any BI tool must connect locally.

## Vector search ([vector DB ticket](wayfinder/tickets/07-grilling-choose-vector-db-and-embedding.md))

- Postgres + pgvector in a local Docker container (fallback: SQLite + sqlite-vec). Browse with TablePlus.
- Embedding: `bge-m3` via Ollama. Embedded content: an English summary per activity and per week, generated from the numbers. Laps and daily metrics are not embedded.
- Hybrid queries: numbers stay in columns for SQL filters (sport, date, distance); vectors rank the filtered rows.
- No free-text titles or notes were seen in COROS data, so vector search runs on generated text only.

## LLM and tools ([LLM ticket](wayfinder/tickets/06-grilling-choose-llm.md), [routing ticket](wayfinder/tickets/11-grilling-question-routing-and-tools.md))

- Ollama, `qwen3:14b` (fallback `gpt-oss:20b`). Model name and context size are settings, not hardcoded (Ollama default `num_ctx` is 4096).
- Tools: fixed parameterised query tools, a guarded read-only SQL tool, vector search for similar activities, `search_guidance`. The LLM picks tools via tool calling; no separate router unless testing shows it is needed.
- DB protection: a dedicated read-only Postgres role limited to needed tables, with max query time and row count (settings).
- Every answer shows the query/tool used; empty results say "no data"; numbers not in results are never stated.

## Charts ([sandbox ticket](wayfinder/tickets/13-grilling-chart-code-sandbox.md))

- The LLM writes plotting code; it runs in a short-lived, network-off Docker container. Query result mounted read-only, exactly one PNG out (size-capped), no DB access.
- Prebuilt image with matplotlib, pandas, numpy (pinned). One retry on error, then text plus table with a "chart could not be drawn" note. The code is shown in the collapsed section.
- Time, memory, CPU and output limits are settings, chosen after measuring. Docker Desktop must be running.

## UI ([UI ticket](wayfinder/tickets/12-prototype-chat-ui-and-charts.md))

- React front end, single-column chat (variant A of `prototype/chat_ui_prototype.html`): answer text, inline chart or table, collapsed "query / code used".
- Trade-off accepted: React plus an API is extra front-end work that does not teach vector databases (Streamlit was the lighter option).

## Advice ([guardrails ticket](wayfinder/tickets/14-grilling-advice-guardrails.md), [guidance store ticket](wayfinder/tickets/16-grilling-expert-guidance-store.md))

- Allowed: statistics, evidence-backed observations, text-only training suggestions. Advice answers cite numbers and dates, say "not enough data" when data is missing, and end with one line: based on COROS metrics, not medical advice.
- Never: diagnoses, medical conclusions, medication or diet advice; decline politely and point to a professional.
- COROS status labels are the basis for "where you are"; guidance cards inform "what to do". Contested or conflicting sources are stated as such.
- `guidance_cards`: short paraphrases, each with topic, content, source link, related metric, consensus level, embedding. Claude drafts them from sourced research, the owner approves each, no source means no card ([research](wayfinder/research/15-running-expert-guidance.md)).
- Because HRV and resting HR are not available, assessments rest on training load, load ratio, COROS labels and recent volume. Using a personal HRV/HR baseline waits until that data exists.
- COROS load bands: all 31 days of loaded data matched the published bands (Decreasing below 0.5, Resuming 0.5-0.79, Maintaining 0.8-0.99); the "Load Ratio" from the connector behaves like COROS Intensity Trend. Still **[UNVERIFIED]**: figures on live COROS pages, academic sources read via abstracts only, COROS terms of use.

## Learning plan (built into the work)

- Vector index: start with exact search, add an HNSW index, compare results and recall with exact search; try cosine distance.
- Embedding check: about 20 Vietnamese/English questions on the owner's data comparing 2-3 embedding models; switch if poor.
- LLM bake-off: speed, Vietnamese quality, tool-calling and SQL reliability, matplotlib code quality; swap model if poor.
- Evaluation set also covers advice cases: missing data, medical questions (must decline), different load-ratio levels.

## Proposed build order (not yet agreed)

1. Environment: Python (venv on 3.15.2 via `uv`; psycopg 3.3.8 works), Ollama, Docker Desktop, Postgres + pgvector container.
2. Raw pull from the connector (12 months) and the parser into `activities`, `laps`, `daily_metrics`.
3. Summaries, embeddings, vector search; index experiments.
4. Backend with tools and the read-only role; LLM bake-off.
5. Chart sandbox image and runner.
6. React UI.
7. Guidance cards and advice behaviour; evaluation set and runs.

## Build status (updated 2026-11-08)

- Done: Ollama (`qwen3:14b`, `bge-m3`), Postgres 17 + pgvector 0.8.7 in Docker, schema (`sql/001_schema.sql`), Python venv.
- Loaded: 171 activities (12 months), details for 14 recent runs, laps for 4 runs, 32 days of `daily_metrics`, 171 activity embeddings, 50 weekly embeddings. Loaders are in `src/ingest/`, embedding and search scripts in `src/embed/`; raw files are in `data/raw/` (git-ignored).
- Search check: vector search finds categories (sport, "Anaerobic") but not numeric meaning (pace, heart rate, "heavy week"). Questions about quantities use SQL, which matches the hybrid design.
- Not built yet: backend and tools, read-only DB role, chart sandbox, React UI, guidance cards, evaluation set, HNSW experiment.

## Not yet specified

- Evaluation question set contents, automated refresh, sleep/stress/VO2max data, FIT parsing, parser details, exact limits and settings values.
