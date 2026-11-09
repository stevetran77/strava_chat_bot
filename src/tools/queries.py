"""Fixed, parameterised query tools. Every number the chatbot states comes from here.

All queries run as the read-only role `chatbot_ro` and return plain dicts, so the LLM layer
can serialise them. Parameters are bound by the driver, never formatted into SQL.
Row limit comes from TOOL_MAX_ROWS in .env.
"""
import logging
import sys
from datetime import date
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingest"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "embed"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from embed_activities import embed_texts, vector_literal  # noqa: E402
from load_sport_records import load_env  # noqa: E402
from sql_guard import UnsafeSql, check_select  # noqa: E402,F401

log = logging.getLogger("tools")


def connect(env=None):
    env = env or load_env()
    return psycopg.connect(
        host="127.0.0.1", port=env["POSTGRES_PORT"], dbname=env["POSTGRES_DB"],
        user="chatbot_ro", password=env["CHATBOT_RO_PASSWORD"], row_factory=dict_row,
    )


def _run(sql, params, env=None):
    env = env or load_env()
    params = {**params, "max_rows": int(env["TOOL_MAX_ROWS"])}
    with connect(env) as conn:
        rows = conn.execute(sql, params).fetchall()
    log.info("tool query returned %d row(s)", len(rows))
    return [{k: (float(v) if hasattr(v, "as_tuple") else v) for k, v in row.items()} for row in rows]


ACTIVITY_COLUMNS = """local_date, sport_name, distance_km, duration_s, avg_pace_s_per_km, avg_hr, avg_cadence,
               avg_power, elevation_gain_m, calories, training_load, aerobic_te, anaerobic_te, training_focus"""


def recent_activities(sport_type=None, limit=5, env=None):
    """Newest activities first, optionally one sport_type (100 = outdoor run)."""
    return _run(f"""
        SELECT {ACTIVITY_COLUMNS}
        FROM activities WHERE (%(sport)s::int IS NULL OR sport_type = %(sport)s::int)
        ORDER BY started_at DESC NULLS LAST, local_date DESC LIMIT least(%(limit)s, %(max_rows)s)
    """, {"sport": sport_type, "limit": limit}, env)


def activities_between(start, end, sport_type=None, env=None):
    """Each activity with start <= local_date <= end (ISO dates), oldest first. Use for 'the run on 2026-11-07'."""
    return _run(f"""
        SELECT {ACTIVITY_COLUMNS}
        FROM activities WHERE local_date BETWEEN %(start)s::date AND %(end)s::date
          AND (%(sport)s::int IS NULL OR sport_type = %(sport)s::int)
        ORDER BY started_at LIMIT %(max_rows)s
    """, {"start": start, "end": end, "sport": sport_type}, env)


def period_totals(start, end, sport_type=None, env=None):
    """Totals for activities with start <= local_date <= end (ISO dates), per sport."""
    return _run("""
        SELECT sport_name, count(*) AS activities, round(sum(distance_km), 2) AS distance_km,
               sum(duration_s) AS duration_s, round(sum(duration_s) / nullif(sum(distance_km), 0)) AS avg_pace_s_per_km,
               round(avg(avg_hr)) AS avg_hr, sum(training_load) AS training_load
        FROM activities
        WHERE local_date BETWEEN %(start)s::date AND %(end)s::date
          AND (%(sport)s::int IS NULL OR sport_type = %(sport)s::int)
        GROUP BY sport_name ORDER BY sport_name LIMIT %(max_rows)s
    """, {"start": start, "end": end, "sport": sport_type}, env)


def weekly_totals(weeks=8, sport_type=None, env=None):
    """Distance, time and count for each of the last `weeks` ISO weeks (Monday start), newest first.

    The current week is always the first row, with zeros when nothing has happened yet.
    """
    return _run("""
        SELECT w.week_start, count(a.label_id) AS activities,
               coalesce(round(sum(a.distance_km), 2), 0) AS distance_km, coalesce(sum(a.duration_s), 0) AS duration_s
        FROM generate_series(date_trunc('week', current_date)::date - 7 * (least(%(weeks)s, %(max_rows)s) - 1),
                             date_trunc('week', current_date)::date, interval '7 days') AS g(d)
        CROSS JOIN LATERAL (SELECT g.d::date AS week_start) w
        LEFT JOIN activities a ON date_trunc('week', a.local_date)::date = w.week_start
                              AND (%(sport)s::int IS NULL OR a.sport_type = %(sport)s::int)
        GROUP BY w.week_start ORDER BY w.week_start DESC
    """, {"weeks": weeks, "sport": sport_type}, env)


def data_span(env=None):
    """First and last activity date in the database."""
    return _run("SELECT min(local_date) AS first_day, max(local_date) AS last_day FROM activities", {}, env)[0]


def activity_laps(date, sport_type=None, env=None):
    """Per-km laps of the activities on one local date (ISO). Empty when laps were not loaded for them.

    Keyed by date, not label_id: 18-digit ids lose precision when a model copies them as JSON numbers.
    """
    return _run("""
        SELECT a.local_date, a.sport_name, l.lap_index, l.distance_km, l.time_s, l.avg_pace_s_per_km,
               l.avg_hr, l.max_hr, l.avg_cadence
        FROM laps l JOIN activities a USING (label_id)
        WHERE a.local_date = %(date)s::date AND (%(sport)s::int IS NULL OR a.sport_type = %(sport)s::int)
        ORDER BY a.started_at, l.lap_index LIMIT %(max_rows)s
    """, {"date": date, "sport": sport_type}, env)


def daily_load(start, end, env=None):
    """COROS training load, load ratio and label per day, oldest first."""
    return _run("""
        SELECT metric_date, short_term_load, long_term_load, load_ratio, load_comment, resting_hr
        FROM daily_metrics WHERE metric_date BETWEEN %(start)s::date AND %(end)s::date
        ORDER BY metric_date LIMIT %(max_rows)s
    """, {"start": start, "end": end}, env)


def search_activities(query, sport_type=None, limit=5, env=None):
    """Activities whose summary is closest in meaning to the query text (cosine distance, lower = closer).

    Rows farther than SEARCH_MAX_DISTANCE are dropped, so unrelated queries return nothing.
    """
    env = env or load_env()
    vector = embed_texts(env["OLLAMA_URL"], env["OLLAMA_EMBED_MODEL"], [query])[0]
    return _run("""
        SELECT a.local_date, a.sport_name, a.distance_km, a.avg_pace_s_per_km, a.avg_hr,
               a.training_load, a.training_focus, round((e.embedding <=> %(q)s::vector)::numeric, 3) AS distance
        FROM embeddings e JOIN activities a USING (label_id)
        WHERE e.kind = 'activity' AND e.model = %(model)s
          AND (%(sport)s::int IS NULL OR a.sport_type = %(sport)s::int)
          AND e.embedding <=> %(q)s::vector <= %(max_dist)s::float
        ORDER BY e.embedding <=> %(q)s::vector LIMIT least(%(limit)s, %(max_rows)s)
    """, {"q": vector_literal(vector), "model": env["OLLAMA_EMBED_MODEL"], "sport": sport_type,
          "limit": limit, "max_dist": float(env["SEARCH_MAX_DISTANCE"])}, env)


def run_sql(sql, env=None):
    """One guarded SELECT. Raises UnsafeSql for anything else; the read-only role is the last defence."""
    query = check_select(sql)
    return _run(f"SELECT * FROM ({query}) AS q LIMIT %(max_rows)s", {}, env)


TOOLS = {f.__name__: f for f in (recent_activities, activities_between, period_totals, weekly_totals, activity_laps, daily_load,
                                 search_activities, run_sql)}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    for name, rows in (("recent_activities", recent_activities(100, 3)),
                       ("weekly_totals", weekly_totals(3)),
                       ("period_totals", period_totals("2026-10-01", str(date.today()))),
                       ("daily_load", daily_load("2026-11-01", "2026-11-08"))):
        print(f"{name}: {len(rows)} row(s); first: {rows[0] if rows else None}")
