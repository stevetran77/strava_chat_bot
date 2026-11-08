"""Consistency checks on the loaded data.

Usage: .venv/bin/python src/checks/check_data.py      Exit code 1 if any check fails.
Checks:
  1. Lap distance and time sums match their activity.
  2. Daily COROS load labels match the published load-ratio bands.
  3. Every activity and every ISO week with activities has an embedding.
"""
import logging
import sys
from pathlib import Path

import psycopg

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingest"))
from load_sport_records import load_env  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("check_data")

# Largest differences seen on real data were 0.003 km and 1 s; these allow a little more.
LAP_DISTANCE_TOLERANCE_KM = 0.02
LAP_TIME_TOLERANCE_S = 3

CHECKS = {
    "lap totals match activity totals": """
        SELECT a.local_date::text FROM activities a JOIN laps l USING (label_id)
        GROUP BY a.label_id, a.local_date, a.distance_km, a.duration_s
        HAVING abs(sum(l.distance_km) - a.distance_km) > %(km_tol)s
            OR abs(sum(l.time_s) - a.duration_s) > %(s_tol)s
    """,
    "load labels match ratio bands": """
        SELECT metric_date::text FROM daily_metrics WHERE load_comment IS NOT NULL AND NOT (
            (load_comment = 'Excessive' AND load_ratio >= 1.5) OR
            (load_comment = 'Optimized' AND load_ratio >= 1.0 AND load_ratio < 1.5) OR
            (load_comment = 'Maintaining' AND load_ratio >= 0.8 AND load_ratio < 1.0) OR
            (load_comment IN ('Resuming', 'Performance') AND load_ratio >= 0.5 AND load_ratio < 0.8) OR
            (load_comment = 'Decreasing' AND load_ratio < 0.5))
    """,
    "every activity has an embedding": """
        SELECT a.local_date::text || ' ' || a.label_id FROM activities a
        LEFT JOIN embeddings e ON e.label_id = a.label_id AND e.kind = 'activity' AND e.model = %(model)s
        WHERE e.id IS NULL
    """,
    "every week with activities has an embedding": """
        SELECT w.week_start::text FROM (SELECT DISTINCT date_trunc('week', local_date)::date AS week_start FROM activities) w
        LEFT JOIN embeddings e ON e.week_start = w.week_start AND e.kind = 'week' AND e.model = %(model)s
        WHERE e.id IS NULL
    """,
}


def main():
    env = load_env()
    params = {"km_tol": LAP_DISTANCE_TOLERANCE_KM, "s_tol": LAP_TIME_TOLERANCE_S, "model": env["OLLAMA_EMBED_MODEL"]}
    failed = 0
    with psycopg.connect(
        host="127.0.0.1", port=env["POSTGRES_PORT"], dbname=env["POSTGRES_DB"],
        user=env["POSTGRES_USER"], password=env["POSTGRES_PASSWORD"],
    ) as conn:
        for name, sql in CHECKS.items():
            bad = [row[0] for row in conn.execute(sql, params).fetchall()]
            if bad:
                failed += 1
                log.error("[FAIL] %s: %d problem(s), e.g. %s", name, len(bad), ", ".join(bad[:3]))
            else:
                log.info("[OK] %s", name)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
