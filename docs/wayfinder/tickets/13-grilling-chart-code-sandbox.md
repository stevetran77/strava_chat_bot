---
title: "Sandbox for LLM-written chart code"
label: wayfinder:grilling
status: closed
blocked_by: []
assignee: stevetran
---

## Question

- The owner chose to let the LLM write plotting code that the system runs. How is that code contained?
- Decide: process isolation, no network, time and memory limits, allowed libraries, what data goes in (query result only, never DB access), and what comes out (image or chart data for the React front end).
- Decide what happens when the code fails or returns nothing.
- Recommended starting point from the routing ticket (unconfirmed): separate process, no network, time limit, query result only, small library allow-list.

## Resolution

- Isolation: each run of LLM-written chart code happens in a short-lived Docker container with the network disabled; the container is removed afterwards. If start-up is too slow at build time, consider keeping a warm container.
- Data in/out: the backend writes the query result to a file (CSV or JSON) mounted read-only; the container never gets DB access or credentials. It writes exactly one PNG to a dedicated output folder, with a size cap; the backend reads it and returns it to the React front end.
- Libraries: one prebuilt image with matplotlib, pandas and numpy at pinned versions. No package install at run time (network is off). Adding a library means rebuilding the image.
- Output format: PNG image (static), shown inline in the chat bubble.
- Failure: send the error back to the LLM for one retry (retry count configurable). If it still fails, answer with text and the data table plus a "chart could not be drawn" note.
- Transparency: the plotting code is shown in the collapsed section under the chart, next to the query used.
- Limits (run time, memory, CPU, output size): configurable settings, values chosen at build after measuring; none fixed here.
- Open: container start-up latency, how well a 14B model writes matplotlib code, exact Docker flags (all to verify at build). Docker Desktop must be running.
