---
title: "Research: Strava API for personal use"
label: wayfinder:research
status: closed
blocked_by: []
assignee: research-subagent
---

## Question

- How does a single personal user pull their own activity data from the Strava API?
- Cover: app registration and OAuth flow (token refresh), rate limits, fields available on activity summaries (and laps), pagination, polling vs webhooks for new activities, any restrictions on local storage/AI use of the data (API agreement).
- Output: findings file at `docs/wayfinder/research/01-strava-api.md`, primary sources only, with links.

## Resolution

- Findings: `../research/01-strava-api.md`. Personal app in Single Player Mode, scope `activity:read_all`, localhost callback, tokens rotate. Limits 100 req/15 min and 1,000/day (non-upload). Polling with `after=` fits local-only; webhooks need a public URL.
- Open: HR/`suffer_score` fields, API Agreement AI/ML clause, subscription requirement, max `per_page` (all unverified).
