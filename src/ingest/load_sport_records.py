"""Parse a raw COROS querySportRecords file and upsert it into `activities`.

Usage: .venv/bin/python src/ingest/load_sport_records.py data/raw/<file>.json
The raw file is the connector output saved as-is (a JSON string of text).
Fields the list does not carry (cadence, power, elevation, load, TE, focus)
stay NULL until activity details are loaded.
"""
import json
import logging
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import psycopg

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("load_sport_records")

HEADER_RE = re.compile(r"^(\d+)\. (.+?) — (\d{4}-\d{2}-\d{2})$", re.M)


def load_env(path=".env"):
    values = {}
    for line in Path(path).read_text().splitlines():
        if line.strip() and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip()
    return values


def duration_to_seconds(text):
    parts = [int(p) for p in text.split(":")]
    seconds = 0
    for part in parts:
        seconds = seconds * 60 + part
    return seconds


def distance_to_km(text):
    match = re.match(r"([\d.,]+)\s*(km|m)\b", text.strip())
    if not match:
        return None
    value = float(match.group(1).replace(",", ""))
    return value if match.group(2) == "km" else value / 1000


def first_match(pattern, block):
    match = re.search(pattern, block)
    return match.group(1) if match else None


def parse_block(sport_name, local_date, block):
    label_id = first_match(r"LabelId: (\d+)", block)
    sport_type = first_match(r"SportType: (\d+)", block)
    if not label_id or not sport_type:
        return None
    coords = re.search(r"Start Coordinates: (-?[\d.]+), (-?[\d.]+)", block)
    start_ts = first_match(r"startTimestamp=(\d+)", block)
    end_ts = first_match(r"endTimestamp=(\d+)", block)
    duration = first_match(r"Duration: ([\d:]+)", block)
    distance = first_match(r"Distance: ([\d.,]+ (?:km|m))\b", block)
    pace = first_match(r"Average Pace: ([\d:]+) /km", block)
    avg_hr = first_match(r"Avg HR: (\d+) bpm", block)
    calories = first_match(r"Calories: (\d+) kcal", block)
    to_dt = lambda ts: datetime.fromtimestamp(int(ts), tz=timezone.utc) if ts else None
    return {
        "label_id": int(label_id),
        "sport_type": int(sport_type),
        "sport_name": sport_name,
        "started_at": to_dt(start_ts),
        "ended_at": to_dt(end_ts),
        "local_date": local_date,
        "duration_s": duration_to_seconds(duration) if duration else None,
        "distance_km": distance_to_km(distance) if distance else None,
        "avg_pace_s_per_km": duration_to_seconds(pace) if pace else None,
        "avg_hr": int(avg_hr) if avg_hr else None,
        "calories": int(calories) if calories else None,
        "location_label": first_match(r"Location: (.+)", block),
        "start_lat": float(coords.group(1)) if coords else None,
        "start_lon": float(coords.group(2)) if coords else None,
    }


def parse_records(text):
    headers = list(HEADER_RE.finditer(text))
    records = []
    for i, header in enumerate(headers):
        end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
        record = parse_block(header.group(2), header.group(3), text[header.end():end])
        if record is None:
            log.warning("[FAIL] skipped block without LabelId: %s %s", header.group(2), header.group(3))
            continue
        records.append(record)
    return records


UPSERT_SQL = """
INSERT INTO activities (label_id, sport_type, sport_name, started_at, ended_at, local_date,
    duration_s, distance_km, avg_pace_s_per_km, avg_hr, calories, location_label,
    start_lat, start_lon, raw_file)
VALUES (%(label_id)s, %(sport_type)s, %(sport_name)s, %(started_at)s, %(ended_at)s, %(local_date)s,
    %(duration_s)s, %(distance_km)s, %(avg_pace_s_per_km)s, %(avg_hr)s, %(calories)s,
    %(location_label)s, %(start_lat)s, %(start_lon)s, %(raw_file)s)
ON CONFLICT (label_id) DO UPDATE SET
    sport_type = EXCLUDED.sport_type, sport_name = EXCLUDED.sport_name,
    started_at = EXCLUDED.started_at, ended_at = EXCLUDED.ended_at, local_date = EXCLUDED.local_date,
    duration_s = EXCLUDED.duration_s, distance_km = EXCLUDED.distance_km,
    avg_pace_s_per_km = EXCLUDED.avg_pace_s_per_km, avg_hr = EXCLUDED.avg_hr,
    calories = EXCLUDED.calories, location_label = EXCLUDED.location_label,
    start_lat = EXCLUDED.start_lat, start_lon = EXCLUDED.start_lon, raw_file = EXCLUDED.raw_file
"""


def main(raw_path):
    env = load_env()
    text = json.loads(Path(raw_path).read_text())
    records = parse_records(text)
    for record in records:
        record["raw_file"] = raw_path
    with psycopg.connect(
        host="127.0.0.1",
        port=env["POSTGRES_PORT"],
        dbname=env["POSTGRES_DB"],
        user=env["POSTGRES_USER"],
        password=env["POSTGRES_PASSWORD"],
    ) as conn:
        with conn.cursor() as cur:
            cur.executemany(UPSERT_SQL, records)
    log.info("[OK] upserted %d activities from %s", len(records), raw_path)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
