---
title: "Research: COROS connector data and limits"
label: wayfinder:research
status: closed
blocked_by: []
assignee: stevetran
---

## Question

- What does the claude.ai COROS connector expose, and can it feed a local chatbot?
- Cover: tool inventory (read-only vs write), fields per activity/lap/health record, history depth, pagination and rate limits, cost, FIT file download, whether the data comes from a COROS device or synced sources (queryDevices returned none yet activities exist).
- Can a client outside Claude (the local chatbot) call this MCP server directly, or only a Claude session? Check COROS docs and terms for AI/data-storage restrictions.
- Output: findings file at `docs/wayfinder/research/09-coros-connector.md`. Primary sources only; mark unverified items. Read-only calls only: never call create/update/schedule/upload tools.
- Note: connector tools need an authenticated Claude session; a subagent may not have them.

## Resolution

- Findings: `../research/09-coros-connector.md`. Read tools cover activities, laps (JSON), health, training load, FIT download; list and detail output is text, not JSON. History reaches at least 2023-12-31. Large pulls must be chunked by date.
- Open: official status, cost, rate limits and terms unknown; direct use from a local client not established (assume data enters via a Claude session); `queryDevices` empty although activities exist.
