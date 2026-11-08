"""Exact (no index) similarity search over activity summaries.

Usage: .venv/bin/python src/embed/search_activities.py "<query>" [--sport-type N] [--limit N]
Embeds the query with the model from .env, then ranks rows by cosine distance.
--sport-type filters in SQL first (the hybrid shape); vectors rank the rest.
"""
import argparse
import sys
from pathlib import Path

import psycopg

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingest"))
from load_sport_records import load_env  # noqa: E402
from embed_activities import embed_texts, vector_literal  # noqa: E402

SEARCH_SQL = """
SELECT a.local_date, a.sport_name, a.distance_km, a.avg_pace_s_per_km, a.avg_hr, a.training_load,
       a.training_focus, e.embedding <=> %(q)s::vector AS distance
FROM embeddings e JOIN activities a USING (label_id)
WHERE e.kind = 'activity' AND e.model = %(model)s
  AND (%(sport)s::int IS NULL OR a.sport_type = %(sport)s::int)
ORDER BY e.embedding <=> %(q)s::vector
LIMIT %(limit)s
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query")
    parser.add_argument("--sport-type", type=int, default=None)
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()
    env = load_env()
    model = env["OLLAMA_EMBED_MODEL"]
    vector = embed_texts(env["OLLAMA_URL"], model, [args.query])[0]
    with psycopg.connect(
        host="127.0.0.1", port=env["POSTGRES_PORT"], dbname=env["POSTGRES_DB"],
        user=env["POSTGRES_USER"], password=env["POSTGRES_PASSWORD"],
    ) as conn:
        rows = conn.execute(SEARCH_SQL, {"q": vector_literal(vector), "model": model,
                                         "sport": args.sport_type, "limit": args.limit}).fetchall()
    print(f"query: {args.query}")
    for date, sport, km, pace, hr, load, focus, dist in rows:
        km_text = f"{float(km):5.2f} km" if km is not None else "   -    "
        decimal_pace = f"{pace / 60:.2f} min/km" if pace else "      -    "
        print(f"  {dist:.3f}  {date}  {sport:<12} {km_text}  {decimal_pace}  HR {hr}  load {load}  {focus or ''}")


if __name__ == "__main__":
    main()
