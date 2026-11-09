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
    def scalar(self, sql, params=None):
        with queries.connect() as conn:
            return list(conn.execute(sql, params).fetchone().values())[0]

    def test_weekly_totals_match_independent_sum(self):
        for row in queries.weekly_totals(4):
            expected = self.scalar("SELECT coalesce(sum(distance_km), 0) FROM activities "
                                   "WHERE local_date >= %(d)s AND local_date < %(d)s::date + 7", {"d": row["week_start"]})
            self.assertAlmostEqual(row["distance_km"], float(expected), places=1, msg=str(row["week_start"]))

    def test_weekly_totals_first_row_is_current_week(self):
        rows = queries.weekly_totals(3)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]["week_start"], self.scalar("SELECT date_trunc('week', current_date)::date"))

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
        self.assertEqual(queries.activity_laps('1999-01-01'), [])

    def test_laps_by_date_sum_to_activity_distance(self):
        laps = queries.activity_laps('2026-11-07', sport_type=100)
        expected = self.scalar("SELECT distance_km FROM activities WHERE local_date = '2026-11-07' AND sport_type = 100")
        self.assertAlmostEqual(sum(l['distance_km'] for l in laps), float(expected), delta=0.02)

    def test_row_limit_comes_from_env(self):
        env = {**queries.load_env(), "TOOL_MAX_ROWS": "2"}
        self.assertEqual(len(queries.recent_activities(limit=10, env=env)), 2)

    def test_run_sql_returns_rows_and_caps_them(self):
        env = {**queries.load_env(), "TOOL_MAX_ROWS": "3"}
        self.assertEqual(len(queries.run_sql("SELECT * FROM activities", env=env)), 3)
        self.assertEqual(queries.run_sql("SELECT count(*) AS n FROM activities")[0]["n"],
                         self.scalar("SELECT count(*) FROM activities"))

    def test_run_sql_refuses_writes_before_the_database(self):
        with self.assertRaises(queries.UnsafeSql):
            queries.run_sql("DELETE FROM laps")

    def test_search_drops_unrelated_query(self):
        self.assertEqual(queries.search_activities("Xin chào"), [])

    def test_search_finds_runs(self):
        rows = queries.search_activities("easy run", limit=3)
        self.assertTrue(rows and all(r["distance"] <= 0.55 for r in rows))


if __name__ == "__main__":
    unittest.main()
