"""Chart tool pre-checks. No database or Docker needed."""
import sys
import unittest
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "charts"))
from draw import ChartError, build_spec, check_columns, check_granularity, fill_gaps, json_value  # noqa: E402

ROWS = [{"week": date(2026, 11, 2), "km": Decimal("12.5"), "hr": None}, {"week": date(2026, 11, 9), "km": Decimal("0"), "hr": 150}]


class GranularityTest(unittest.TestCase):
    def test_weekly_title_needs_week_grouping(self):
        self.assertIsNotNone(check_granularity("SELECT local_date, distance_km FROM activities", "Số km mỗi tuần"))

    def test_week_grouping_passes(self):
        sql = "SELECT date_trunc('week', local_date)::date AS w, sum(distance_km) FROM activities GROUP BY 1"
        self.assertIsNone(check_granularity(sql, "Số km mỗi tuần"))

    def test_weekly_chart_must_not_use_limit(self):
        sql = "SELECT date_trunc('week', local_date)::date AS w, sum(distance_km) FROM activities GROUP BY 1 ORDER BY 1 DESC LIMIT 12"
        self.assertIn("LIMIT", check_granularity(sql, "Số km mỗi tuần"))

    def test_other_charts_are_not_checked(self):
        self.assertIsNone(check_granularity("SELECT local_date, avg_hr FROM activities", "Nhịp tim mỗi buổi chạy"))


class JsonValueTest(unittest.TestCase):
    def test_midnight_timestamp_becomes_a_date(self):
        self.assertEqual(json_value(datetime(2025, 11, 1, tzinfo=timezone.utc)), "2025-11-01")

    def test_real_time_of_day_is_kept(self):
        self.assertEqual(json_value(datetime(2025, 11, 1, 6, 30)), "2025-11-01T06:30:00")

    def test_dates_decimals_and_numbers(self):
        self.assertEqual(json_value(date(2025, 11, 1)), "2025-11-01")
        self.assertEqual(json_value(Decimal("12.5")), 12.5)
        self.assertEqual(json_value(7), 7)


class ColumnCheckTest(unittest.TestCase):
    def test_valid_columns_pass(self):
        check_columns(ROWS, "week", ["km", "hr"])

    def test_missing_column_names_the_available_ones(self):
        with self.assertRaisesRegex(ChartError, "week"):
            check_columns(ROWS, "week", ["distance"])

    def test_empty_result_and_series_count(self):
        with self.assertRaises(ChartError):
            check_columns([], "week", ["km"])
        with self.assertRaises(ChartError):
            check_columns(ROWS, "week", [])

    def test_text_in_y_is_rejected(self):
        with self.assertRaises(ChartError):
            check_columns([{"w": "a", "k": "b"}], "w", ["k"])


class SpecTest(unittest.TestCase):
    def test_spec_is_plain_json_with_only_used_columns(self):
        spec = build_spec("bar", "Km mỗi tuần", "week", ["km"], "Tuần", "km", [{**row, "extra": 1} for row in ROWS])
        self.assertEqual(spec["rows"], [{"week": "2026-11-02", "km": 12.5}, {"week": "2026-11-09", "km": 0.0}])


class FillGapsTest(unittest.TestCase):
    weeks = [{"w": date(2026, 11, 2), "km": 5}, {"w": date(2026, 11, 16), "km": 7}]

    def test_missing_week_is_zero_for_sums(self):
        rows = fill_gaps(self.weeks, "w", ["km"], "bar", "SELECT sum(distance_km) AS km")
        self.assertEqual([row["km"] for row in rows], [5, 0, 7])
        self.assertEqual(rows[1]["w"], date(2026, 11, 9))

    def test_missing_week_is_null_for_averages(self):
        self.assertIsNone(fill_gaps(self.weeks, "w", ["km"], "bar", "SELECT avg(avg_hr) AS km")[1]["km"])

    def test_missing_month_is_filled_across_a_year_end(self):
        months = [{"m": date(2025, 11, 1), "km": 1}, {"m": date(2026, 2, 1), "km": 2}]
        self.assertEqual(len(fill_gaps(months, "m", ["km"], "bar", "SELECT sum(x)")), 4)

    def test_lines_and_plain_dates_are_untouched(self):
        self.assertEqual(fill_gaps(self.weeks, "w", ["km"], "line", "sum("), self.weeks)
        days = [{"w": date(2026, 11, 3), "km": 1}, {"w": date(2026, 11, 5), "km": 2}]
        self.assertEqual(fill_gaps(days, "w", ["km"], "bar", "sum("), days)


if __name__ == "__main__":
    unittest.main()
