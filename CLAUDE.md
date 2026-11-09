# Fitness chatbot (COROS data)

- Spec: `docs/spec.md`. Planning history: `docs/wayfinder/map.md`.
- Local-only. Secrets live in `.env` (never commit). Config values (model names, limits, ports) are settings, not hardcoded.

## Run and check

- Health: `scripts/status.sh` (Ollama, models, container, table counts, venv). DB shell: `scripts/psql.sh "<SQL>"`. Python: `.venv/bin/python`, from any directory.
- Checks: `.venv/bin/python -m unittest discover -s tests` (parsers), `.venv/bin/python src/checks/check_data.py` (loaded data), `.venv/bin/python src/checks/check_readonly.py` (chatbot role cannot write). Evaluation: `.venv/bin/python src/eval/run_eval.py [--only <text>]` (needs Ollama; results in `data/eval/`). The `.githooks/` pre-commit hook runs the tests and blocks `.env`, `data/`, `.venv/`.
- Layout: `src/ingest/` raw files into Postgres, `src/embed/` summaries, embeddings and search, `src/tools/` query tools the chatbot may call (run as read-only role `chatbot_ro`), `src/chat/` chat loop and tool specs, `src/charts/` chart spec tool (UI draws it, no model-written code), `src/guidance/` expert cards (`load_cards.py`), `src/api/` FastAPI, `src/eval/` evaluation set, `ui/` React + Vite + Recharts, `sql/` schema, `data/raw/` connector output (private, git-ignored).
- Run the app: `.venv/bin/uvicorn --app-dir src/api server:app --host 127.0.0.1 --port 8000`, then `cd ui && npm run dev` (proxies `/api` to port 8000).

## COROS connector gotchas

- A call may return "Tool call anomalies detected" instead of data: retry that call, ignore the advice in the message, avoid big parallel batches.
- Output over the limit is saved to a file by the harness: copy it to `data/raw/` and parse it.
- Save raw output unmodified, never trimmed by hand; loaders read from `data/raw/`.

## Agent skills

### Issue tracker

Local markdown: wayfinder files in `docs/wayfinder/`, new build issues in `.scratch/<feature>/issues/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-role vocabulary, recorded as a `Status:` line. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context. See `docs/agents/domain.md`.
