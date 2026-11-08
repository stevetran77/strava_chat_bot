"""Parse raw COROS getActivityDetail text and fill detail columns of `activities`.

Usage: .venv/bin/python src/ingest/load_activity_details.py data/raw/<details>.json
The raw file maps labelId -> connector text, saved as-is.
Rows must already exist (load_sport_records.py runs first).
"""
import json
import logging
import re
import sys
from pathlib import Path

import psycopg

from load_sport_records import load_env

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("load_activity_details")


def field(pattern, text, cast):
    match = re.search(pattern, text)
    return cast(match.group(1)) if match else None


def parse_detail(text):
    elevation = re.search(r"Elevation Gain / Loss: (\d+) m / (\d+) m", text)
    return {
        "avg_cadence": field(r"Average Cadence: (\d+) spm", text, int),
        "avg_power": field(r"Average Power: (\d+) W", text, int),
        "elevation_gain_m": int(elevation.group(1)) if elevation else None,
        "elevation_loss_m": int(elevation.group(2)) if elevation else None,
        "training_load": field(r"Training Load: (\d+)", text, int),
        "aerobic_te": field(r"Aerobic TE: ([\d.]+)", text, float),
        "anaerobic_te": field(r"Anaerobic TE: ([\d.]+)", text, float),
        "training_focus": field(r"Training Focus: (.+)", text, str),
    }


UPDATE_SQL = """
UPDATE activities SET avg_cadence = %(avg_cadence)s, avg_power = %(avg_power)s,
    elevation_gain_m = %(elevation_gain_m)s, elevation_loss_m = %(elevation_loss_m)s,
    training_load = %(training_load)s, aerobic_te = %(aerobic_te)s,
    anaerobic_te = %(anaerobic_te)s, training_focus = %(training_focus)s
WHERE label_id = %(label_id)s
"""


def main(raw_path):
    env = load_env()
    details = json.loads(Path(raw_path).read_text())
    rows = []
    for label_id, text in details.items():
        row = parse_detail(text)
        row["label_id"] = int(label_id)
        rows.append(row)
    updated = 0
    with psycopg.connect(
        host="127.0.0.1",
        port=env["POSTGRES_PORT"],
        dbname=env["POSTGRES_DB"],
        user=env["POSTGRES_USER"],
        password=env["POSTGRES_PASSWORD"],
    ) as conn:
        with conn.cursor() as cur:
            for row in rows:
                cur.execute(UPDATE_SQL, row)
                if cur.rowcount == 0:
                    log.warning("[FAIL] no activity row for label_id %s", row["label_id"])
                updated += cur.rowcount
    log.info("[OK] updated %d of %d activities from %s", updated, len(rows), raw_path)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
