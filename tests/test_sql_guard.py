"""SQL guard tests. No database needed."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "tools"))
from sql_guard import UnsafeSql, check_select  # noqa: E402


class AllowedTest(unittest.TestCase):
    def test_plain_select(self):
        self.assertEqual(check_select("SELECT count(*) FROM activities;"), "SELECT count(*) FROM activities")

    def test_with_query(self):
        check_select("WITH w AS (SELECT 1 AS x) SELECT x FROM w")

    def test_keyword_inside_quotes_is_fine(self):
        check_select("SELECT * FROM activities WHERE training_focus = 'update plan'")

    def test_column_names_that_contain_words(self):
        check_select("SELECT started_at, set_count_note FROM activities")


class RejectedTest(unittest.TestCase):
    def reject(self, sql):
        with self.assertRaises(UnsafeSql, msg=sql):
            check_select(sql)

    def test_writes_and_ddl(self):
        for sql in ("DROP TABLE laps", "DELETE FROM laps", "UPDATE activities SET avg_hr = 1",
                    "INSERT INTO laps DEFAULT VALUES", "TRUNCATE laps", "CREATE TABLE t (a int)"):
            self.reject(sql)

    def test_stacked_statements(self):
        self.reject("SELECT 1; DROP TABLE laps")

    def test_select_into(self):
        self.reject("SELECT * INTO copy_of_laps FROM laps")

    def test_comments(self):
        self.reject("SELECT 1 -- hidden")
        self.reject("SELECT /* x */ 1")

    def test_functions_and_settings(self):
        for sql in ("SELECT pg_sleep(10)", "SELECT pg_read_file('/etc/passwd')", "SELECT set_config('a','b',false)",
                    "SELECT current_setting('x')", "SELECT lo_import('/x')"):
            self.reject(sql)

    def test_not_a_select(self):
        self.reject("EXPLAIN SELECT 1")
        self.reject("")


if __name__ == "__main__":
    unittest.main()
