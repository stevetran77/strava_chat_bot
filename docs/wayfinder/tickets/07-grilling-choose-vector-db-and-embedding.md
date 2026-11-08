---
title: "Choose vector DB and embedding model"
label: wayfinder:grilling
status: closed
blocked_by: [03-research-embedding-models, 04-research-vector-db]
assignee: stevetran
---

## Question

- Which vector DB and embedding model do we use, balancing learning value against simplicity and Vietnamese/English quality?

## Added note

- Owner asked about Postgres: pgvector is a candidate (one DB for tables and vectors; needs a local Postgres, not installed; Docker and Homebrew exist). Also decide the SQL engine here, since ticket "Choose data scope and ingestion path" left it open.

## Resolution

- Engine: Postgres + pgvector for both SQL tables and vectors (one DB). Run locally in a Docker container (Docker Desktop must be started; image name and install commands to verify at build time). Fallback if setup is too painful: SQLite + sqlite-vec.
- Embedding: `bge-m3` served through Ollama (1024 dimensions, Vietnamese + English).
- Validation: spec includes a small evaluation (about 20 Vietnamese/English questions on the owner's own data) comparing 2-3 embedding models; switch if results are poor.
- Learning plan: start with exact (no-index) search, then add an HNSW index and compare results and recall against exact search; try cosine distance.
- Tooling: the owner browses the database with TablePlus (GUI client) connected to the local container.
- Open: pgvector/Docker details unverified; Python 3.14 (Homebrew) compatibility with the needed libraries unverified.
