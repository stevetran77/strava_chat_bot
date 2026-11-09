"""Tool descriptions the LLM sees, and the system prompt. Names match src/tools/queries.py."""


def _fn(name, description, properties=None, required=()):
    return {"type": "function", "function": {"name": name, "description": description, "parameters": {
        "type": "object", "properties": properties or {}, "required": list(required)}}}


SPORT = {"type": "integer", "description": "Optional sport filter: 100 run, 102 trail run, 101 indoor run, "
         "900 walk, 301 open water swim, 200 cycling, 402 strength, 400 gym cardio, 902 floor climb."}
DATE = lambda text: {"type": "string", "description": f"{text} (YYYY-MM-DD)"}  # noqa: E731

TOOL_SPECS = [
    _fn("recent_activities", "Newest activities first (date, distance, pace, heart rate, load, focus).",
        {"sport_type": SPORT, "limit": {"type": "integer", "description": "How many rows."}}),
    _fn("period_totals", "ONE total per sport for a date range (count, km, seconds, pace over the whole range, average HR, summed load). Not for per-month or per-day breakdowns.",
        {"start": DATE("First day"), "end": DATE("Last day"), "sport_type": SPORT}, ["start", "end"]),
    _fn("weekly_totals", "Distance, time and count per ISO week (Monday start), newest week first. Distance and time only, no training load.",
        {"weeks": {"type": "integer", "description": "How many weeks back."}, "sport_type": SPORT}),
    _fn("activity_laps", "Per-km laps of one activity (needs its label_id from another tool). Empty if not loaded.",
        {"label_id": {"type": "integer"}}, ["label_id"]),
    _fn("daily_load", "COROS training load per day: short/long-term load, load ratio, label (Optimized, Excessive...) and resting HR. Use for any question about training load or load status.",
        {"start": DATE("First day"), "end": DATE("Last day")}, ["start", "end"]),
    _fn("search_activities", "Find activities by meaning (e.g. 'easy long run'). Use for fuzzy descriptions, "
        "not for exact numbers. Returns nothing when no activity is close enough.",
        {"query": {"type": "string", "description": "Short English description."}, "sport_type": SPORT,
         "limit": {"type": "integer"}}, ["query"]),
    _fn("run_sql", "One read-only SELECT. Use for grouping or ranking the other tools cannot do, e.g. per month (date_trunc), best or longest, averages. Rankings must add NULLS LAST and filter sport_type (a NULL distance sorts first otherwise). Tables: "
        "activities(label_id, sport_type, sport_name, started_at, local_date, duration_s, distance_km, "
        "avg_pace_s_per_km, avg_hr, calories, avg_cadence, avg_power, elevation_gain_m, training_load, "
        "aerobic_te, anaerobic_te, training_focus, location_label); "
        "laps(label_id, lap_index, distance_km, time_s, avg_pace_s_per_km, avg_hr, max_hr); "
        "daily_metrics(metric_date, resting_hr, short_term_load, long_term_load, load_ratio, load_comment).",
        {"sql": {"type": "string"}}, ["sql"]),
]


def system_prompt(today):
    return f"""You answer questions about the user's own COROS training data. Today is {today}; the current year is {today.year}, so 'this year' means {today.year}.
- Get every number from a tool result. Never state a number that is not in a result.
- If a tool returns no rows, say there is no data for that; do not guess.
- Reply in the language of the question (Vietnamese or English), short and clear.
- Pace is seconds per km in the data: show it as min:sec per km. Distances are km. Dates are YYYY-MM-DD.
- COROS load ratio bands: below 0.5 Decreasing, 0.5-0.79 Resuming, 0.8-0.99 Maintaining, 1.0-1.49 Optimized, 1.5+ Excessive.
- Choose tools: training load or ratio -> daily_load; per-month, ranking or other grouping -> run_sql; fuzzy descriptions -> search_activities.
- A single 'running' question means sport_type 100 (add trail run 102 only if asked). Always filter by sport when the question names one.
- Data spans about the last 12 months; do not query earlier years.
- Details (cadence, power, laps) exist only for some activities; a missing value means not loaded."""
