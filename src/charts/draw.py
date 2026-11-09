"""The draw_chart tool: guarded SQL -> rows -> a chart spec the web UI draws.

The model never writes plotting code. It names a chart kind and result columns; this module checks them
against the real rows, so colours, fonts and layout always come from the UI theme.
"""
import logging
import re
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "tools"))
from queries import load_env, run_sql  # noqa: E402

log = logging.getLogger("draw")
KINDS = ("bar", "line")
MAX_SERIES = 3
WEEKLY_WORDS = re.compile(r"mỗi tuần|theo tuần|hàng tuần|per week|weekly|each week", re.IGNORECASE)


class ChartError(Exception):
    """A chart request the model should correct; the message says how."""


def check_granularity(sql, title):
    """A weekly title over a query that is not grouped by week is a wrong chart; say so the model can fix it."""
    if WEEKLY_WORDS.search(title) and "date_trunc('week'" not in sql.lower().replace('"', "'"):
        return "the chart is titled per week but the SQL does not GROUP BY date_trunc('week', local_date)::date; aggregate by week"
    if WEEKLY_WORDS.search(title) and re.search(r"\blimit\b", sql, re.IGNORECASE):
        return "do not use LIMIT for weeks (weeks without activity would be skipped); filter with WHERE local_date >= date_trunc('week', current_date) - interval 'N-1 weeks'"
    return None


def json_value(value):
    """Row value as plain JSON: midnight timestamps become dates, decimals become numbers."""
    if isinstance(value, datetime):
        return value.date().isoformat() if (value.hour, value.minute, value.second, value.microsecond) == (0, 0, 0, 0) else value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def check_columns(rows, x, y):
    """Columns must exist and every y value must be a number (or NULL); raises ChartError otherwise."""
    if not rows:
        raise ChartError("the query returned no rows; check the date range and filters")
    if not 1 <= len(y) <= MAX_SERIES:
        raise ChartError(f"y needs 1 to {MAX_SERIES} columns")
    missing = [name for name in [x, *y] if name not in rows[0]]
    if missing:
        raise ChartError(f"columns {missing} are not in the result; the result has {list(rows[0])}. Alias them in the SELECT")
    for name in y:
        if any(row[name] is not None and not isinstance(json_value(row[name]), (int, float)) for row in rows):
            raise ChartError(f"y column '{name}' is not numeric")


def next_period(day, step):
    """The next week start (step 'week') or month start (step 'month')."""
    if step == "week":
        return day + timedelta(days=7)
    return date(day.year + day.month // 12, day.month % 12 + 1, 1)


def period_step(days):
    """'week' when every x is a Monday, 'month' when every x is the 1st, else None."""
    if len(days) < 2:
        return None
    if all(day.weekday() == 0 for day in days):
        return "week"
    return "month" if all(day.day == 1 for day in days) else None


def fill_gaps(rows, x, y, kind, sql):
    """Bar charts per week or month show every period: a missing one gets 0 for sums and counts, NULL otherwise."""
    if kind != "bar":
        return rows
    try:
        days = [date.fromisoformat(str(json_value(row[x]))) for row in rows]
    except ValueError:
        return rows
    step = period_step(days)
    if not step:
        return rows
    empty = 0 if re.search(r"\b(sum|count)\s*\(", sql, re.IGNORECASE) else None
    by_day = dict(zip(days, rows))
    filled, day = [], min(days)
    while day <= max(days):
        filled.append(by_day.get(day) or {x: day, **{name: empty for name in y}})
        day = next_period(day, step)
    return filled


def build_spec(kind, title, x, y, x_label, y_label, rows):
    return {"kind": kind, "title": title, "x": x, "y": list(y), "x_label": x_label, "y_label": y_label,
            "rows": [{key: json_value(value) for key, value in row.items() if key in (x, *y)} for row in rows]}


def draw_chart(sql, kind, x, y, title, x_label=None, y_label=None, env=None):
    """Run one guarded SELECT and describe a chart over its result.

    Returns {"chart": spec, "rows_used"} or {"error"} so the model can correct its request once.
    """
    env = env or load_env()
    if kind not in KINDS:
        return {"error": f"kind must be one of {KINDS}"}
    problem = check_granularity(sql, title)
    if problem:
        return {"error": problem}
    try:
        rows = run_sql(sql, env={**env, "TOOL_MAX_ROWS": env["CHART_MAX_ROWS"]})
        check_columns(rows, x, y)
        rows = fill_gaps(rows, x, y, kind, sql)
    except ChartError as exc:
        return {"error": str(exc)}
    return {"chart": build_spec(kind, title, x, y, x_label, y_label, rows), "rows_used": len(rows)}
