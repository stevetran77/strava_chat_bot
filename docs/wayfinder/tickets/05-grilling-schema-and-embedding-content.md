---
title: "Activity schema and what gets embedded"
label: wayfinder:grilling
status: closed
blocked_by: []
assignee: stevetran
---

## Question

- What is the SQL schema for COROS activities (and health data if in scope)?
- Which text/content gets embedded for the vector DB (generated weekly/monthly summaries, notes?) and what metadata travels with each embedding?
- Privacy: start coordinates are returned per activity; decide whether to store them.

## Added note

- Scope settled by the data-source ticket: activities + per-km laps + daily resting HR, HRV, training load. Raw start coordinates are kept in the raw layer; decide here whether they enter the SQL store.

## Resolution

- Tables (Postgres): `activities` (key = COROS `labelId`; sport, start time, duration, distance, pace, avg HR, calories, cadence, power, elevation, Training Load, Aerobic/Anaerobic TE, location label, start latitude/longitude), `laps` (activity + lap index; per-km pace, HR, power, cadence, running-form metrics), `daily_metrics` (date; resting HR, HRV, short/long-term load, load ratio), `embeddings` (text, 1024-dim vector, key to an activity or a week).
- Units normalised at parse time: km, seconds, seconds/km. Lap distance unit (1 km shown as 100000) unverified; confirm at build.
- Idempotent loads: `labelId` is the key, so re-ingesting never duplicates rows.
- Start coordinates ARE stored in SQL (owner choice, so a BI tool can plot them later). They are private: the database stays local and any BI tool must connect locally, never to a cloud service.
- Embedded: a generated summary per activity ("similar workout" search) and a summary per week (trend questions). Laps and daily metrics are not embedded.
- Summary text: fixed English template; check Vietnamese queries against it in the embedding evaluation, and add Vietnamese summaries if results are poor.
- Hybrid query shape: numbers stay in columns for SQL filtering (sport, date range, distance range); vector similarity ranks the filtered rows. Summary text also mentions the main numbers.
- Open: no free-text titles or notes were seen in COROS data, so vector search runs on generated text only.
