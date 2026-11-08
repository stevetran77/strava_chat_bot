"""Parser tests on made-up samples shaped like the COROS connector output.

Run: .venv/bin/python -m unittest discover -s tests -v
The numbers, label ids and coordinates below are invented; no personal data.
"""
import sys
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "ingest"))
sys.path.insert(0, str(ROOT / "src" / "embed"))

import embed_activities  # noqa: E402
import load_activity_details  # noqa: E402
import load_laps  # noqa: E402
import load_sport_records  # noqa: E402

SPORT_RECORDS = """Sport Records — 2026-01-01 to 2026-01-07 (3 records)
========================

1. Outdoor Run — 2026-01-05
   Location: Test City Run
   Start Coordinates: 10.000000, 106.000000
   Time Window: startTimestamp=1767600000 | endTimestamp=1767602700
   Duration: 45:00 | Distance: 6.50 km
   Average Pace: 6:55 /km | Avg HR: 140 bpm | Calories: 500 kcal
   LabelId: 100000000000000001 | SportType: 100

2. Open Water Swim — 2026-01-04
   Location: Test Lake
   Start Coordinates: 10.100000, 106.100000
   Time Window: startTimestamp=1767500000 | endTimestamp=1767500600
   Duration: 10:00 | Distance: 996 m
   Average Pace: 3:00 /km | Avg HR: 110 bpm | Calories: 90 kcal
   LabelId: 100000000000000002 | SportType: 301

3. Strength — 2026-01-03
   Location: Strength
   Time Window: startTimestamp=1767400000 | endTimestamp=1767401800
   Duration: 1:30:00
   LabelId: 100000000000000003 | SportType: 402"""

ACTIVITY_DETAIL = """Outdoor Run Activity Details
========================================

Workout Time: 45:00
Distance: 6.50 km
Average Heart Rate: 140 bpm
Average Cadence: 160 spm
Average Power: 170 W
Elevation Gain / Loss: 12 m / 9 m
Calories: 500 kcal
Training Load: 80
Aerobic TE: 2.7
Anaerobic TE: 0.4
Training Focus: Base
Performance: Good
Perceived Effort: Somewhat Tired"""

LAP_PAYLOAD = {
    "lapGroups": [
        {"type": 2, "laps": [
            {"lapIndex": 1, "distance": 100000, "time": 400.5, "avgPace": 400.5, "avgHr": 140},
            {"lapIndex": 2, "distance": 55000, "time": 230.0, "avgPace": 418.0, "avgHr": 150, "elevGain": 1.0},
        ]},
        {"type": 11, "laps": [{"lapIndex": 1, "distance": 500000, "time": 2000.0}]},
    ]
}


class SportRecordsTest(unittest.TestCase):
    def setUp(self):
        self.records = load_sport_records.parse_records(SPORT_RECORDS)

    def test_all_blocks_parsed(self):
        self.assertEqual([r["label_id"] for r in self.records],
                         [100000000000000001, 100000000000000002, 100000000000000003])

    def test_run_fields(self):
        run = self.records[0]
        self.assertEqual(run["sport_name"], "Outdoor Run")
        self.assertEqual(run["local_date"], "2026-01-05")
        self.assertEqual(run["duration_s"], 2700)
        self.assertAlmostEqual(run["distance_km"], 6.5)
        self.assertEqual(run["avg_pace_s_per_km"], 415)
        self.assertEqual((run["avg_hr"], run["calories"]), (140, 500))
        self.assertEqual((run["start_lat"], run["start_lon"]), (10.0, 106.0))
        self.assertEqual(run["started_at"], datetime.fromtimestamp(1767600000, tz=timezone.utc))

    def test_metres_become_km(self):
        self.assertAlmostEqual(self.records[1]["distance_km"], 0.996)

    def test_missing_fields_stay_none(self):
        strength = self.records[2]
        for key in ("distance_km", "avg_pace_s_per_km", "avg_hr", "calories", "start_lat"):
            self.assertIsNone(strength[key], key)
        self.assertEqual(strength["duration_s"], 5400)

    def test_duration_helper(self):
        self.assertEqual(load_sport_records.duration_to_seconds("44:10"), 2650)
        self.assertEqual(load_sport_records.duration_to_seconds("1:19:38"), 4778)


class ActivityDetailTest(unittest.TestCase):
    def test_detail_fields(self):
        detail = load_activity_details.parse_detail(ACTIVITY_DETAIL)
        self.assertEqual(detail["avg_cadence"], 160)
        self.assertEqual(detail["avg_power"], 170)
        self.assertEqual((detail["elevation_gain_m"], detail["elevation_loss_m"]), (12, 9))
        self.assertEqual(detail["training_load"], 80)
        self.assertEqual((detail["aerobic_te"], detail["anaerobic_te"]), (2.7, 0.4))
        self.assertEqual(detail["training_focus"], "Base")

    def test_unknown_text_gives_none(self):
        detail = load_activity_details.parse_detail("nothing useful here")
        self.assertTrue(all(value is None for value in detail.values()))


class LapTest(unittest.TestCase):
    def test_only_km_group_is_used(self):
        self.assertEqual(len(load_laps.km_laps(LAP_PAYLOAD)), 2)

    def test_centimetres_become_km(self):
        rows = [load_laps.lap_row("77", lap) for lap in load_laps.km_laps(LAP_PAYLOAD)]
        self.assertAlmostEqual(rows[0]["distance_km"], 1.0)
        self.assertAlmostEqual(rows[1]["distance_km"], 0.55)
        self.assertEqual(rows[1]["label_id"], 77)
        self.assertIsNone(rows[0]["max_hr"])

    def test_payload_without_km_group(self):
        self.assertEqual(load_laps.km_laps({"lapGroups": [{"type": 11, "laps": []}]}), [])


class SummaryTest(unittest.TestCase):
    BASE = {
        "sport_name": "Outdoor Run", "local_date": date(2026, 1, 5), "distance_km": 6.5,
        "duration_s": 2700, "avg_pace_s_per_km": 415, "avg_hr": 140, "calories": 500,
        "avg_cadence": None, "avg_power": None, "elevation_gain_m": None, "training_load": None,
        "aerobic_te": None, "anaerobic_te": None, "training_focus": None, "location_label": "Test City Run",
        "start_lat": 10.0, "start_lon": 106.0,
    }

    def test_template_and_null_fields(self):
        text = embed_activities.summarize(self.BASE)
        self.assertTrue(text.startswith("Outdoor Run on Monday 2026-01-05."))
        self.assertIn("Average pace 6:55 per km.", text)
        self.assertNotIn("Cadence", text)
        self.assertNotIn("Training load", text)

    def test_coordinates_never_in_summary(self):
        text = embed_activities.summarize(self.BASE)
        self.assertNotIn("10.0", text)
        self.assertNotIn("106", text)

    def test_clock_format(self):
        self.assertEqual(embed_activities.format_clock(2650), "44:10")
        self.assertEqual(embed_activities.format_clock(4778), "1:19:38")


if __name__ == "__main__":
    unittest.main()
