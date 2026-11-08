---
title: "Register Strava developer app"
label: wayfinder:task
status: closed
blocked_by: [01-research-strava-api]
assignee: stevetran
---

## Question

- Register a Strava API application for personal use and obtain credentials, so later tickets can judge the real API output.
- HITL checklist to be written from the Strava API research findings. Record where credentials are stored (never commit them).

## Resolution

- App created and credentials saved in the project `.env`. First API call returned 403 `Application / Status / Inactive`; community reports (unverified, not official docs) tie this to the app owner needing a Strava subscription.
- Decision (owner): switch data source to the COROS connector instead of paying. Strava API is out of scope. Real activity field check (HR, suffer_score) never completed.
