"""Load per-km laps (lap group type 2) from raw COROS lap data into `laps`.

Usage: .venv/bin/python src/ingest/load_laps.py data/raw/<laps>.json
The raw file maps labelId -> connector JSON. Distances arrive in centimetres
(1 km = 100000), converted to km here. Rows are replaced per activity, so
reloading never duplicates. Activities must exist first.
"""
import json
import logging
import sys
from pathlib import Path

import psycopg

from load_sport_records import load_env

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("load_laps")

KM_LAP_GROUP_TYPE = 2
CM_PER_KM = 100000

INSERT_SQL = """
INSERT INTO laps (label_id, lap_index, distance_km, time_s, avg_pace_s_per_km, avg_power, avg_hr,
    max_hr, ground_time_ms, avg_cadence, max_cadence, stride_ratio, stride_height,
    avg_stride_length, elev_gain_m, total_descent_m, adjusted_pace)
VALUES (%(label_id)s, %(lap_index)s, %(distance_km)s, %(time_s)s, %(avg_pace_s_per_km)s,
    %(avg_power)s, %(avg_hr)s, %(max_hr)s, %(ground_time_ms)s, %(avg_cadence)s, %(max_cadence)s,
    %(stride_ratio)s, %(stride_height)s, %(avg_stride_length)s, %(elev_gain_m)s,
    %(total_descent_m)s, %(adjusted_pace)s)
"""


def km_laps(payload):
    for group in payload.get("lapGroups", []):
        if group.get("type") == KM_LAP_GROUP_TYPE:
            return group["laps"]
    return []


def lap_row(label_id, lap):
    return {
        "label_id": int(label_id),
        "lap_index": lap["lapIndex"],
        "distance_km": lap["distance"] / CM_PER_KM,
        "time_s": lap["time"],
        "avg_pace_s_per_km": lap.get("avgPace"),
        "avg_power": lap.get("avgPower"),
        "avg_hr": lap.get("avgHr"),
        "max_hr": lap.get("maxHr"),
        "ground_time_ms": lap.get("groundTime"),
        "avg_cadence": lap.get("avgCadence"),
        "max_cadence": lap.get("maxCadence"),
        "stride_ratio": lap.get("strideRatio"),
        "stride_height": lap.get("strideHeight"),
        "avg_stride_length": lap.get("avgStrideLength"),
        "elev_gain_m": lap.get("elevGain"),
        "total_descent_m": lap.get("totalDescent"),
        "adjusted_pace": lap.get("adjustedPace"),
    }


def main(raw_path):
    env = load_env()
    data = json.loads(Path(raw_path).read_text())
    total = 0
    with psycopg.connect(
        host="127.0.0.1",
        port=env["POSTGRES_PORT"],
        dbname=env["POSTGRES_DB"],
        user=env["POSTGRES_USER"],
        password=env["POSTGRES_PASSWORD"],
    ) as conn:
        with conn.cursor() as cur:
            for label_id, payload in data.items():
                rows = [lap_row(label_id, lap) for lap in km_laps(payload)]
                cur.execute("DELETE FROM laps WHERE label_id = %s", (int(label_id),))
                cur.executemany(INSERT_SQL, rows)
                total += len(rows)
                log.info("activity %s: %d laps", label_id, len(rows))
    log.info("[OK] loaded %d laps from %s", total, raw_path)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
