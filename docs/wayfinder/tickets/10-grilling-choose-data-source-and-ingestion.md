---
title: "Choose data scope and ingestion path"
label: wayfinder:grilling
status: closed
blocked_by: [09-research-coros-connector]
assignee: stevetran
---

## Question

- Which COROS data is in scope: activities only, or also sleep/HRV/recovery/training load?
- How does data reach the local store: Claude-assisted pull into SQLite/vector DB, direct MCP from the chatbot (if allowed), or FIT file download?
- Is Strava bulk export kept as a supplement?

## Resolution

- Scope: activities + per-km laps, plus daily data (resting HR, HRV, training load). Sleep, stress, VO2max/race predictions are fog.
- Ingestion: via a Claude session pulling from the COROS connector (read-only tools). Two layers: raw connector output saved as local files (kept as-is, including start coordinates, local only), then a Python script parses raw files into a local SQL store. SQL engine (SQLite or Postgres/pgvector) is decided in the vector DB ticket.
- Initial backfill: last 12 months. Refresh: manual, incremental since the last synced date, by asking Claude in a session.
- Dropped: Strava (API and export), unofficial coros-cli, FIT file parsing (fog), direct MCP call from the chatbot (unproven).
