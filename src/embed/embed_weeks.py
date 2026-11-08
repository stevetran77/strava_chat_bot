"""Generate an English summary per ISO week (Monday start) and store its embedding.

Usage: .venv/bin/python src/embed/embed_weeks.py
Built from `activities` and `daily_metrics`; no coordinates. Re-running updates
existing rows (one row per week and model). Settings come from .env.
"""
import logging
import sys
from collections import defaultdict
from datetime import timedelta
from pathlib import Path

import psycopg

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingest"))
from load_sport_records import load_env  # noqa: E402
from embed_activities import embed_texts, format_clock, vector_literal  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("embed_weeks")

RUN_SPORT_TYPES = {100, 101, 102, 103}

WEEK_ACTIVITIES_SQL = """
SELECT date_trunc('week', local_date)::date AS week_start, sport_type, sport_name,
       count(*) AS n, sum(distance_km) AS km, sum(duration_s) AS seconds,
       sum(avg_hr * duration_s)::float / NULLIF(sum(duration_s) FILTER (WHERE avg_hr IS NOT NULL), 0) AS hr_weighted,
       sum(training_load) AS load_sum, count(training_load) AS n_with_load
FROM activities GROUP BY 1, 2, 3 ORDER BY 1, 3
"""
LAST_LOAD_SQL = """
SELECT DISTINCT ON (date_trunc('week', metric_date)) date_trunc('week', metric_date)::date AS week_start,
       metric_date, short_term_load, long_term_load, load_ratio, load_comment
FROM daily_metrics WHERE load_ratio IS NOT NULL
ORDER BY date_trunc('week', metric_date), metric_date DESC
"""


def describe_group(group):
    n = group["n"]
    noun = group["sport_name"].lower() + ("s" if n > 1 else "")
    text = f"{n} {noun}"
    details = []
    if group["km"]:
        details.append(f"{float(group['km']):.1f} km")
    if group["seconds"]:
        details.append(f"{format_clock(group['seconds'])} total")
    if group["sport_type"] in RUN_SPORT_TYPES and group["km"] and group["seconds"]:
        details.append(f"average pace {format_clock(group['seconds'] / float(group['km']))} per km")
    if group["hr_weighted"]:
        details.append(f"average heart rate {group['hr_weighted'] / 1:.0f} bpm")
    if group["n_with_load"]:
        details.append(f"training load {group['load_sum']} over {group['n_with_load']} of {n}")
    return text + (" (" + ", ".join(details) + ")" if details else "")


def summarize_week(week_start, groups, last_load):
    week_end = week_start + timedelta(days=6)
    total = sum(g["n"] for g in groups)
    iso_year, iso_week, _ = week_start.isocalendar()
    parts = [f"Week {iso_year}-W{iso_week:02d} ({week_start} to {week_end}): {total} activities."]
    parts.append("; ".join(describe_group(g) for g in groups) + ".")
    if last_load:
        parts.append(
            f"Training load status on {last_load['metric_date']}: {last_load['load_comment']}, "
            f"load ratio {float(last_load['load_ratio']):.2f}, short-term load {last_load['short_term_load']}, "
            f"long-term load {last_load['long_term_load']}."
        )
    return " ".join(parts)


UPSERT_SQL = """
INSERT INTO embeddings (kind, week_start, content, model, embedding)
VALUES ('week', %s, %s, %s, %s::vector)
ON CONFLICT (week_start, model) WHERE kind = 'week'
DO UPDATE SET content = EXCLUDED.content, embedding = EXCLUDED.embedding, created_at = now()
"""


def main():
    env = load_env()
    model = env["OLLAMA_EMBED_MODEL"]
    with psycopg.connect(
        host="127.0.0.1", port=env["POSTGRES_PORT"], dbname=env["POSTGRES_DB"],
        user=env["POSTGRES_USER"], password=env["POSTGRES_PASSWORD"],
        row_factory=psycopg.rows.dict_row,
    ) as conn:
        by_week = defaultdict(list)
        for row in conn.execute(WEEK_ACTIVITIES_SQL).fetchall():
            by_week[row["week_start"]].append(row)
        last_loads = {r["week_start"]: r for r in conn.execute(LAST_LOAD_SQL).fetchall()}
        weeks = sorted(by_week)
        texts = [summarize_week(w, by_week[w], last_loads.get(w)) for w in weeks]
        log.info("embedding %d weekly summaries with %s", len(texts), model)
        vectors = []
        for start in range(0, len(texts), 16):
            vectors += embed_texts(env["OLLAMA_URL"], model, texts[start:start + 16])
        for week, text, vector in zip(weeks, texts, vectors):
            conn.execute(UPSERT_SQL, (week, text, model, vector_literal(vector)))
    log.info("[OK] stored %d weekly embeddings (%s)", len(weeks), model)


if __name__ == "__main__":
    main()
