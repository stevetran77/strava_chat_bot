"""Tool queries against the real local database; skipped when it is not reachable.

Run: .venv/bin/python -m unittest discover -s tests -v
Each expected value comes from an independent SQL query, not from the tool under test.
"""
import sys
import unittest
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "tools"))

import queries  # noqa: E402


def database_available():
    try:
        with queries.connect():
            return True
    except (psycopg.Error, KeyError, FileNotFoundError):
        return False


@unittest.skipUnless(database_available(), "local database not reachable")
class QueriesDbTest(unittest.TestCase):
    def scalar(self, sql, params=()):
        with queries.connect() as conn:
            return list(conn.execute(sql, params).fetchone().values())[0]

    def test_weekly_totals_match_independent_sum(self):
        newest = queries.weekly_totals(1)[0]
        expected = self.scalar("SELECT sum(distance_km) FROM activities WHERE local_date >= %s", (newest["week_start"],))
        self.assertAlmostEqual(newest["distance_km"], float(expected), places=1)

    def test_period_totals_count_matches(self):
        rows = queries.period_totals("2000-01-01", "2100-01-01")
        self.assertEqual(sum(r["activities"] for r in rows), self.scalar("SELECT count(*) FROM activities"))

    def test_recent_activities_newest_first_and_limited(self):
        rows = queries.recent_activities(limit=3)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]["local_date"], self.scalar("SELECT max(local_date) FROM activities"))

    def test_sport_filter(self):
        self.assertTrue(all(r["sport_name"] == "Outdoor Run" for r in queries.recent_activities(100, 10)))

    def test_laps_of_unknown_activity_is_empty(self):
        self.assertEqual(queries.activity_laps(1), [])

    def test_row_limit_comes_from_env(self):
        env = {**queries.load_env(), "TOOL_MAX_ROWS": "2"}
        self.assertEqual(len(queries.recent_activities(limit=10, env=env)), 2)


if __name__ == "__main__":
    unittest.main()
