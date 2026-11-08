---
ticket: tickets/04-research-vector-db.md
label: wayfinder:research
date: 2026-11-08
sources: official docs / official READMEs only
---

# Research: Local vector DB options

Scope: thousands of items, single user, macOS M4 Pro, system python3 3.9.6, free + local.
Marker `[UNVERIFIED]` = not confirmed on a fetched official page.

## Summary table

| | Chroma | LanceDB | sqlite-vec | pgvector |
|---|---|---|---|---|
| Form | Embedded client (also server) | Embedded library, no server | SQLite extension | Postgres extension (needs a Postgres server) |
| Setup effort | Low | Low | Low, but macOS Python caveat | Highest (run Postgres) |
| Persistence | `PersistentClient(path=...)` | Lance format on local disk | A normal SQLite file | Postgres storage |
| Default metric | l2 (squared) | l2 | L2 | exact search; operator picks metric |
| Other metrics | cosine, ip | cosine, dot, hamming | cosine (`distance_metric=cosine`) | cosine, inner product, L1, Hamming, Jaccard |
| Index | HNSW | IVF_* / HNSW variants, or flat | brute force (no ANN documented) | HNSW, IVFFlat, or exact |
| Metadata filter | `where` dict operators | SQL string in `where()` | metadata columns in KNN WHERE | full SQL |
| SQL hybrid | Not SQL | SQL filter, no joins documented | Native SQL (it is SQLite) | Native SQL |
| Keyword + vector hybrid | `[UNVERIFIED]` | FTS + vector, RRF default | `[UNVERIFIED]` (SQLite FTS5 not checked) | Postgres FTS + vector, RRF documented |

## Chroma

- Persistence: `chromadb.PersistentClient(path="/path/to/save/to")`; data persists automatically; default path is `.chroma`. `chromadb.Client()` is in-memory. [Clients](https://docs.trychroma.com/docs/run-chroma/clients)
- HNSW config per collection: `space` default `l2` (squared L2), options `cosine`, `ip`; `ef_construction` default 100 (immutable after creation); `ef_search` default 100 (modifiable); `max_neighbors` default 16. [Collection config](https://docs.trychroma.com/docs/collections/configure)
- Metadata filtering: `where` supports `$eq`, `$gt`, `$gte`, `$lte`, `$and`, `$or`, `$in`, `$nin`, `$contains` (array fields); bare value = `$eq`. `where_document` with `$contains` filters on text. Both can be combined with `query_texts`/`n_results` in one call. [Metadata filtering](https://docs.trychroma.com/docs/querying-collections/metadata-filtering)
  - Note: `$lt` was not listed on the fetched page (page lists `$eq/$gt/$gte/$lte`); `[UNVERIFIED]` whether it exists.
- Python install command and default embedding function: the Getting Started page does not state them; `[UNVERIFIED]` (the page only says "install `chromadb`"). [Getting started](https://docs.trychroma.com/docs/overview/getting-started)
- Joins with SQL: none documented; numeric/SQL work would stay in a separate store.
- Learning value: exposes HNSW knobs (`ef_construction`, `ef_search`, `max_neighbors`) and the `space` choice directly in config, good for teaching index and metric concepts.

## LanceDB

- Embedded OSS library that runs in-process, no server; same Lance format also used by the Enterprise offering. [Docs home](https://docs.lancedb.com/)
- Install: `pip install lancedb`. [Vector search](https://docs.lancedb.com/search/vector-search)
- Metrics: `l2`, `cosine`, `dot`, `hamming` (binary only). Unindexed search uses `l2`; when an index exists the query metric must match it, otherwise a slower brute-force search is forced. [Vector search](https://docs.lancedb.com/search/vector-search)
- Indexes: `IVF_FLAT`, `IVF_PQ`, `IVF_SQ`, `IVF_RQ`, `IVF_HNSW_FLAT/PQ/SQ`. No index = flat search over every vector, 100% recall; `.bypass_vector_index()` forces exhaustive search to measure ANN recall. Good for demonstrating the recall vs speed tradeoff.
- Filtering: `where()` takes a SQL expression string (`AND/OR/NOT`, `IN`, `LIKE`, `IS NULL`, `regexp_match`, DataFusion scalar functions). Prefiltering is the default; postfiltering can return fewer results than requested. Optional scalar index for filtered columns. Chained `where` calls are ANDed only in Python 0.34.0+. [Filtering](https://docs.lancedb.com/search/filtering)
- Hybrid: vector search + full-text search merged by a reranker; RRF is the default. Needs an FTS index on the text column. [Hybrid search](https://docs.lancedb.com/search/hybrid-search)
  - Whether FTS uses BM25 or Tantivy is not stated on the page; `[UNVERIFIED]`.
- Persistence: tables stored on local disk in Lance format (Arrow types in memory). [Filtering](https://docs.lancedb.com/search/filtering)
- Joining with an external SQL DB: not documented; `[UNVERIFIED]` whether it can query alongside SQLite directly.

## sqlite-vec

- Pre-v1: "expect breaking changes". Install `pip install sqlite-vec`. Development sponsored by Mozilla Builders and others. [GitHub README](https://github.com/asg017/sqlite-vec)
- Python: `sqlite3` connection, enable extension loading, `sqlite_vec.load(conn)`, disable loading; `serialize_float32()` for lists; NumPy arrays must be `float32`. SQLite 3.41+ recommended. [Python guide](https://alexgarcia.xyz/sqlite-vec/python.html)
- macOS caveat (relevant here): the SQLite bundled with macOS (system Python) does not support extensions; `enable_load_extension` raises `AttributeError`. Documented fix: Homebrew Python (`/opt/homebrew/bin/python3`). The project has system python3 3.9.6, so a venv from a newer Python is likely required; `[UNVERIFIED]` whether 3.9.6 here is system or Homebrew.
- KNN: manual brute force with `vec_distance_L2/L1/cosine()` scanning every row, or `vec0` virtual tables. `vec0` default is L2; `distance_metric=cosine` on the vector column switches to cosine. The KNN page does not discuss ANN. [KNN](https://alexgarcia.xyz/sqlite-vec/features/knn.html)
- `vec0` extra columns: metadata columns (TEXT/INTEGER/FLOAT/BOOLEAN, max 16) usable in KNN WHERE with `= != > >= < <=`; partition key columns (max 4) shard the index; auxiliary `+` columns store unindexed data and cannot be filtered in KNN. `IS NULL`, `LIKE`, `GLOB`, `REGEXP` are not supported there. [vec0](https://alexgarcia.xyz/sqlite-vec/features/vec0.html)
- Hybrid with SQL: strongest fit, since vectors live in the same SQLite file as activity tables, so joins are plain SQL (vec0 results must be joined back to the source table).
- Learning value: shows what a vector search actually is (distance function over blobs, brute-force scan); fewer index concepts to learn.
- Keyword + vector hybrid via FTS5: `[UNVERIFIED]` (not checked).

## pgvector

- Postgres extension; supports exact and approximate NN; vector, halfvec, bit, sparsevec. Postgres 13+. Mac install: `brew install pgvector`, Postgres.app (15+), source build, Docker, conda-forge. `CREATE EXTENSION vector;` per database. [pgvector README](https://github.com/pgvector/pgvector)
- Operators: `<->` L2, `<#>` negative inner product, `<=>` cosine distance, `<+>` L1, `<~>` Hamming, `<%>` Jaccard.
- Indexes: exact by default. HNSW (`m` 16, `ef_construction` 64, `hnsw.ef_search` 40; slower build, more memory, can be built on empty table). IVFFlat (create after loading data; lists = rows/1000 up to 1M rows). Index dimension limit for `vector`: 2,000.
- Filtering: B-tree on filter column for selective filters; approximate indexes filter after the scan so fewer rows can return; `hnsw.iterative_scan` mitigates. Partial indexes / partitioning for many values.
- Hybrid: combine with Postgres full-text search (`plainto_tsquery`, `ts_rank_cd`); merge with Reciprocal Rank Fusion.
- Python: separate `pgvector-python` package (`pip install pgvector`); supports Psycopg 3/2, SQLAlchemy, asyncpg, Django, others; call `register_vector(conn)` after `CREATE EXTENSION`. [pgvector-python](https://github.com/pgvector/pgvector-python)
- Trade-off: needs a running Postgres server (more setup) but the single store can hold both SQL tables and vectors; most transferable skill for production systems.
- At thousands of rows an index is unnecessary (exact search is the default); this is a framing point, not a sourced claim.

## Other options

- Qdrant: local-mode/embedded details could not be verified from official pages fetched (the Python client reference page did not describe local mode; it mentions "Qdrant Edge" as an embedded engine, relation to local mode not stated). `[UNVERIFIED]`. Not recommended without further check.
- Others (FAISS, Milvus Lite, etc.): not researched. `[UNVERIFIED]`.

## Observations for the decision ticket (07)

- Closest to "hybrid with SQL" with minimal infrastructure: sqlite-vec (one file) or pgvector (full SQL but a server).
- Best for learning index concepts (HNSW/IVF params, recall measurement): LanceDB (flat vs ANN, recall baseline) or Chroma (HNSW config), pgvector (HNSW + IVFFlat).
- Risks: sqlite-vec is pre-v1 and has the macOS system-Python extension issue; Chroma/LanceDB are separate stores, so numeric queries still need SQLite/DuckDB alongside.
- Open verification items: Chroma install/default embedder, Chroma/sqlite-vec keyword hybrid, LanceDB FTS engine, Qdrant local mode, version/maintenance status of each project.

## Process note

- Fetches were summarized by WebFetch's small model, not read raw; several pages were rate-limited (HTTP 429) and retried. Re-check critical numbers (defaults, limits) against the linked pages before the final spec.
