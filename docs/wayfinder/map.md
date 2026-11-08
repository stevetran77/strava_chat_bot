---
label: wayfinder:map
---

# Map: Fitness Q&A chatbot (COROS data)

## Destination

- A build-ready spec for a personal fitness chatbot (build is a separate effort).
- Local-only, hybrid (SQL for numbers/charts + vector DB for semantic search), data from the COROS connector, local open-source LLM, simple web UI (Vietnamese/English) with charts.

## Notes

- Purpose: learn vector databases and the steps to build an AI chatbot. The spec should keep the learning rationale.
- Single user (the owner). Free, runs locally on Apple M4 Pro, 24 GB RAM. Ollama not installed; python3 is 3.9.6.
- Data source changed from Strava to COROS (Strava API returned 403 Inactive, tied to a paid subscription).
- COROS connector is a claude.ai connector (needs an authenticated Claude session). Use read-only tools only. Activity records include start coordinates: treat as private.
- Plan, don't do: tickets produce decisions, not code.
- Tracker: local markdown. Tickets live in `tickets/`; each has `type`, `status` (open/closed), `blocked_by`, `assignee`. Research findings in `research/`.

## Decisions so far

- [Research: Strava API for personal use](tickets/01-research-strava-api.md): superseded by the source change; kept as record (single-player app, polling, limits).
- [Research: Local LLMs on M4 Pro 24 GB](tickets/02-research-local-llm.md): qwen3:14b leading candidate; speed and Vietnamese quality unmeasured.
- [Research: Local multilingual embedding models](tickets/03-research-embedding-models.md): bge-m3 / m-e5-large-instruct best Vietnamese evidence; others unverified.
- [Research: Local vector DB options](tickets/04-research-vector-db.md): sqlite-vec best SQL fit (pre-v1); LanceDB/Chroma better for learning indexes.
- [Register Strava developer app](tickets/08-task-register-strava-app.md): app blocked by 403 Inactive; owner switched the data source to COROS.
- [Research: COROS connector data and limits](tickets/09-research-coros-connector.md): read tools cover activities, laps (JSON), health, load; list/detail output is text; history to at least 2023-12-31; direct local use unproven, official terms unknown.

- [Choose data scope and ingestion path](tickets/10-grilling-choose-data-source-and-ingestion.md): activities + laps + daily resting HR/HRV/load; Claude-session pull into raw local files, parsed into a local SQL store; 12-month backfill; manual incremental refresh.

- [Choose vector DB and embedding model](tickets/07-grilling-choose-vector-db-and-embedding.md): Postgres + pgvector in local Docker (one DB for tables and vectors); bge-m3 via Ollama; evaluate on own data; learn exact vs HNSW search; TablePlus as GUI.

- [Activity schema and what gets embedded](tickets/05-grilling-schema-and-embedding-content.md): 4 Postgres tables (activities, laps, daily_metrics, embeddings), `labelId` key, coordinates stored (private, local only, for later BI); embed per-activity and per-week English summaries; numbers filter in SQL, vectors rank.

- [Choose the local LLM](tickets/06-grilling-choose-llm.md): Ollama + qwen3:14b (fallback gpt-oss:20b); locked now, bake-off at build; model and context size configurable.

- [Question routing and tool design](tickets/11-grilling-question-routing-and-tools.md): fixed query tools + guarded read-only SQL tool, LLM picks tools, read-only DB role with limits, show the query used, LLM-written plotting code run by the system (sandbox recommended, unconfirmed).

- [Chat UI and chart prototype](tickets/12-prototype-chat-ui-and-charts.md): variant A (single-column chat, inline chart/table, collapsed query); React front end + Python backend API; prototype kept at `prototype/chat_ui_prototype.html`.

- [Sandbox for LLM-written chart code](tickets/13-grilling-chart-code-sandbox.md): short-lived network-off Docker container per run; query result mounted read-only, one PNG out; prebuilt image (matplotlib, pandas, numpy); one retry on failure; code shown collapsed; limits configurable.

- [Advice and analysis guardrails](tickets/14-grilling-advice-guardrails.md): stats + evidence-backed observations + text-only training suggestions; judged by COROS metrics and running-expert guidance; one-line uncertainty note on advice; no medical/diagnosis/diet advice; cite numbers and dates; advice cases in the evaluation set.

- [Research: Running expert guidance sources](tickets/15-research-running-expert-guidance.md): COROS defines its own load bands and labels; HRV/resting HR have no cut-offs (use own baseline); acute/chronic load and 10% rule contested; store paraphrased cards with links, not copied text; figures to recheck against live pages.

- [Expert guidance store and citation](tickets/16-grilling-expert-guidance-store.md): `guidance_cards` table (paraphrased cards with source, metric, consensus level, embedding); `search_guidance` tool; COROS label = current status, cards = what to do; say so when sources disagree; owner approves each card, no source no card.

## Open tickets (index, frontier marked with *)

- None. Remaining build-phase items are listed in Not yet specified.

## Not yet specified

- Automated refresh (scheduled routine) instead of manual sync.
- Sleep, stress, VO2max and race-prediction data.
- Parser design for the text outputs of the connector.
- Evaluation question set for the chatbot.
- Python environment setup (3.9.6 is too old for some candidates) and Ollama install.
- Per-second streams / FIT files ingestion.

## Out of scope

- Strava bulk export (dropped by owner; COROS is the only source).

- Multi-user support.
- Cloud deployment.
- Claude API / paid LLMs.
- Strava API (paid subscription gate).
- Writing anything to COROS (creating plans, workouts, routes): the project is read-only.
