# Fitness chatbot (COROS data)

- Spec: `docs/spec.md`. Planning history: `docs/wayfinder/map.md`.
- Local-only. Secrets live in `.env` (never commit). Config values (model names, limits, ports) are settings, not hardcoded.

## Agent skills

### Issue tracker

Local markdown: wayfinder files in `docs/wayfinder/`, new build issues in `.scratch/<feature>/issues/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-role vocabulary, recorded as a `Status:` line. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context. See `docs/agents/domain.md`.
