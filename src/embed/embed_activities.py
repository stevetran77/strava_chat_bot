"""Generate an English summary per activity and store its bge-m3 embedding.

Usage: .venv/bin/python src/embed/embed_activities.py
Summaries are built only from database columns (no coordinates). Re-running
updates existing rows (one row per activity and model). Settings come from .env.
"""
import json
import logging
import sys
import urllib.request
from pathlib import Path

import psycopg

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingest"))
from load_sport_records import load_env  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("embed_activities")

BATCH_SIZE = 16


def format_clock(seconds):
    hours, rest = divmod(int(seconds), 3600)
    minutes, secs = divmod(rest, 60)
    return f"{hours}:{minutes:02d}:{secs:02d}" if hours else f"{minutes}:{secs:02d}"


def summarize(row):
    """Fixed English template. Fields that are NULL are left out."""
    parts = [f"{row['sport_name']} on {row['local_date']:%A %Y-%m-%d}."]
    if row["distance_km"] is not None:
        parts.append(f"Distance {float(row['distance_km']):.2f} km.")
    if row["duration_s"] is not None:
        parts.append(f"Duration {format_clock(row['duration_s'])}.")
    if row["avg_pace_s_per_km"] is not None:
        parts.append(f"Average pace {format_clock(row['avg_pace_s_per_km'])} per km.")
    if row["avg_hr"] is not None:
        parts.append(f"Average heart rate {row['avg_hr']} bpm.")
    if row["calories"] is not None:
        parts.append(f"{row['calories']} kcal.")
    if row["avg_cadence"] is not None:
        parts.append(f"Cadence {row['avg_cadence']} spm.")
    if row["avg_power"] is not None:
        parts.append(f"Power {row['avg_power']} W.")
    if row["elevation_gain_m"] is not None:
        parts.append(f"Elevation gain {row['elevation_gain_m']} m.")
    if row["training_load"] is not None:
        parts.append(f"Training load {row['training_load']}.")
    if row["aerobic_te"] is not None:
        parts.append(f"Aerobic effect {float(row['aerobic_te']):.1f}, anaerobic effect {float(row['anaerobic_te']):.1f}.")
    if row["training_focus"]:
        parts.append(f"Training focus {row['training_focus']}.")
    if row["location_label"]:
        parts.append(f"Location: {row['location_label']}.")
    return " ".join(parts)


def embed_texts(base_url, model, texts):
    body = json.dumps({"model": model, "input": texts}).encode()
    request = urllib.request.Request(f"{base_url}/api/embed", body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=300) as response:
        return json.loads(response.read())["embeddings"]


def vector_literal(values):
    return "[" + ",".join(f"{v:.8f}" for v in values) + "]"


UPSERT_SQL = """
INSERT INTO embeddings (kind, label_id, content, model, embedding)
VALUES ('activity', %s, %s, %s, %s::vector)
ON CONFLICT (label_id, model) WHERE kind = 'activity'
DO UPDATE SET content = EXCLUDED.content, embedding = EXCLUDED.embedding, created_at = now()
"""


def main():
    env = load_env()
    model = env["OLLAMA_EMBED_MODEL"]
    base_url = env["OLLAMA_URL"]
    with psycopg.connect(
        host="127.0.0.1", port=env["POSTGRES_PORT"], dbname=env["POSTGRES_DB"],
        user=env["POSTGRES_USER"], password=env["POSTGRES_PASSWORD"],
        row_factory=psycopg.rows.dict_row,
    ) as conn:
        rows = conn.execute("SELECT * FROM activities ORDER BY local_date, label_id").fetchall()
        log.info("summarising %d activities with %s", len(rows), model)
        done = 0
        for start in range(0, len(rows), BATCH_SIZE):
            batch = rows[start:start + BATCH_SIZE]
            texts = [summarize(r) for r in batch]
            vectors = embed_texts(base_url, model, texts)
            for row, text, vector in zip(batch, texts, vectors):
                conn.execute(UPSERT_SQL, (row["label_id"], text, model, vector_literal(vector)))
            done += len(batch)
            log.info("embedded %d/%d", done, len(rows))
    log.info("[OK] stored %d activity embeddings (%s)", done, model)


if __name__ == "__main__":
    main()
