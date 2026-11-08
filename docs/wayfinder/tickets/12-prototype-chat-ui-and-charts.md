---
title: "Chat UI and chart prototype"
label: wayfinder:prototype
status: closed
blocked_by: [11-grilling-question-routing-and-tools]
assignee: stevetran
---

## Question

- How should the simple chat UI look and behave, and how are charts shown in it (inline in the conversation, separate panel)?
- Which UI framework fits a local, single-user, learning project?
- Rough take only: stub or mock data, no real pipeline.

## Resolution

- Prototype: `prototype/chat_ui_prototype.html` (3 variants, fake data, throwaway). Kept in place as the reference; the folder is not a git repo, so there is no throwaway branch.
- Chosen look: variant A, a classic single-column chat. Answer bubbles hold the text, the chart or result table inline, and a collapsed "query used" section (per the routing ticket).
- Framework (owner choice): React for the front end plus a Python backend API (FastAPI suggested). The backend runs Ollama calls, Postgres queries and chart code, and returns text, tables and chart images or data. Node 22 and pnpm are already installed.
- Trade-off noted: React plus an API adds front-end work that does not teach vector databases; Streamlit was the lighter option. Owner chose React anyway.
- Open: React chat/streaming libraries and FastAPI details unverified; Python 3.14 compatibility of the backend libraries unverified.
