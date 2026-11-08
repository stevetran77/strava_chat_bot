"""Load daily training load and resting heart rate into `daily_metrics`.

Usage: .venv/bin/python src/ingest/load_daily_metrics.py <training_load.json> [<resting_hr.json>]
Each raw file is the connector text saved as a JSON string. Days are upserted
and only the columns present in a file are touched, so the two files can be
loaded in any order. "No data" days are skipped. HRV is not loaded here.
"""
import json
import logging
import re
import sys
from pathlib import Path

import psycopg

from load_sport_records import load_env

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("load_daily_metrics")

LOAD_BLOCK_RE = re.compile(
    r"(\d{4}-\d{2}-\d{2})\nComment: (.+)\nShort-Term Load: (\d+)\nLong-Term Load: (\d+)\nLoad Ratio: ([\d.]+)"
)
RESTING_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}): (\d+) bpm$", re.M)

LOAD_SQL = """
INSERT INTO daily_metrics (metric_date, short_term_load, long_term_load, load_ratio, load_comment, raw_file)
VALUES (%s, %s, %s, %s, %s, %s)
ON CONFLICT (metric_date) DO UPDATE SET short_term_load = EXCLUDED.short_term_load,
    long_term_load = EXCLUDED.long_term_load, load_ratio = EXCLUDED.load_ratio,
    load_comment = EXCLUDED.load_comment, raw_file = EXCLUDED.raw_file
"""
RESTING_SQL = """
INSERT INTO daily_metrics (metric_date, resting_hr) VALUES (%s, %s)
ON CONFLICT (metric_date) DO UPDATE SET resting_hr = EXCLUDED.resting_hr
"""


def read_text(path):
    return json.loads(Path(path).read_text())


def main(load_path, resting_path):
    env = load_env()
    loads = LOAD_BLOCK_RE.findall(read_text(load_path))
    resting = RESTING_RE.findall(read_text(resting_path)) if resting_path else []
    with psycopg.connect(
        host="127.0.0.1", port=env["POSTGRES_PORT"], dbname=env["POSTGRES_DB"],
        user=env["POSTGRES_USER"], password=env["POSTGRES_PASSWORD"],
    ) as conn:
        for day, comment, short_term, long_term, ratio in loads:
            conn.execute(LOAD_SQL, (day, int(short_term), int(long_term), ratio, comment, load_path))
        for day, bpm in resting:
            conn.execute(RESTING_SQL, (day, int(bpm)))
    log.info("[OK] %d load days, %d resting HR days", len(loads), len(resting))


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) == 3 else None)
