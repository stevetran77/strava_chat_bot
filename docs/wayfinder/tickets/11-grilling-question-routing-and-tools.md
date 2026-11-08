---
title: "Question routing and tool design"
label: wayfinder:grilling
status: closed
blocked_by: []
assignee: stevetran
---

## Question

- How does the local LLM answer a Vietnamese/English question: which tools does it get (free-form read-only SQL, fixed parameterised query tools, vector search, chart tool), and who decides SQL vs vector search?
- How is the database protected (read-only role, query limits) given a 14B model may write wrong SQL?
- How are wrong or empty answers handled (say "I don't know", show the query)?

## Resolution

- Tools: fixed parameterised query tools for common questions (activities by filter, weekly totals, load trend, find similar activities) plus a guarded read-only SQL tool for everything else.
- Routing: the LLM chooses the tool through tool calling from tool descriptions; vector search is for "similar workout" style questions. No separate router unless the build bake-off shows the model picks wrongly.
- DB protection: a dedicated read-only Postgres role limited to the needed tables, with a maximum query time and a maximum row count (both configurable, values chosen at build).
- Wrong or empty answers: always show the tool call or SQL used under the answer, say "no data" on empty results, never state numbers absent from the results.
- Charts (owner choice): the LLM writes plotting code and the system runs it. Not what was recommended (a declarative chart spec); the risk is running model-generated code. Recommended mitigation, not yet confirmed by the owner: run it in a separate process, no network, time limit, only the query result passed in, a small allow-list of libraries.
- Open: reliability of a 14B model at tool choice, SQL writing and plotting code; measured in the build bake-off.
