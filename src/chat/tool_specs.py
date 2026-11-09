"""Tool descriptions the LLM sees, and the system prompt. Names match src/tools/queries.py."""

from datetime import timedelta  # noqa: E402


def _fn(name, description, properties=None, required=()):
    return {"type": "function", "function": {"name": name, "description": description, "parameters": {
        "type": "object", "properties": properties or {}, "required": list(required)}}}


SPORT = {"type": "integer", "description": "Optional sport filter: 100 outdoor run (default for any running question), 102 trail run (only if asked), 101 indoor run, "
         "900 walk, 301 open water swim, 200 cycling, 402 strength, 400 gym cardio, 902 floor climb."}
DATE = lambda text: {"type": "string", "description": f"{text} (YYYY-MM-DD)"}  # noqa: E731

TABLES = (
    "activities(label_id, sport_type, sport_name, started_at, local_date, duration_s, distance_km, "
    "avg_pace_s_per_km, avg_hr, calories, avg_cadence, avg_power, elevation_gain_m, training_load, "
    "aerobic_te, anaerobic_te, training_focus, location_label); "
    "laps(label_id, lap_index, distance_km, time_s, avg_pace_s_per_km, avg_hr, max_hr); "
    "daily_metrics(metric_date, resting_hr, short_term_load, long_term_load, load_ratio, load_comment).")

TOOL_SPECS = [
    _fn("recent_activities", "Newest activities first with all per-activity details (distance, pace, HR, cadence, power, elevation, calories, load, training effect, focus).",
        {"sport_type": SPORT, "limit": {"type": "integer", "description": "How many rows."}}),
    _fn("activities_between", "Each activity between two dates with the same details; use it to look up 'the run on <date>'.",
        {"start": DATE("First day"), "end": DATE("Last day"), "sport_type": SPORT}, ["start", "end"]),
    _fn("period_totals", "ONE total per sport for a date range (count, km, seconds, pace over the whole range, average HR, summed load). Not for per-month or per-day breakdowns.",
        {"start": DATE("First day"), "end": DATE("Last day"), "sport_type": SPORT}, ["start", "end"]),
    _fn("weekly_totals", "Distance, time and count per ISO week (Monday start), newest week first. Distance and time only, no training load.",
        {"weeks": {"type": "integer", "description": "How many weeks back."}, "sport_type": SPORT}),
    _fn("activity_laps", "Per-km laps (distance, time, pace, HR) of the activities on one date. Empty if laps were not loaded for that day.",
        {"date": DATE("The activity's day"), "sport_type": SPORT}, ["date"]),
    _fn("daily_load", "COROS training load per day: short/long-term load, load ratio, label (Optimized, Excessive...) and resting HR. Use for any question about training load or load status.",
        {"start": DATE("First day"), "end": DATE("Last day")}, ["start", "end"]),
    _fn("search_activities", "Find activities by meaning (e.g. 'easy long run'). Use for fuzzy descriptions, "
        "not for exact numbers or dates. Returns nothing when no activity is close enough.",
        {"query": {"type": "string", "description": "Short English description."}, "sport_type": SPORT,
         "limit": {"type": "integer"}}, ["query"]),
    _fn("search_guidance", "Expert training guidance cards (COROS definitions, load, taper, easy/hard mix, recovery), each with "
        "a source link and a consensus level. Call it for any advice or 'what should I do' question, and for what a metric or label means.",
        {"query": {"type": "string", "description": "Short English description of the topic."},
         "limit": {"type": "integer"}}, ["query"]),
    _fn("draw_chart", "Draw a chart in the app; the app styles it, you only choose data and shape. `sql` is one SELECT; `kind` is 'bar' (one bar per week, month or category) or 'line' (a trend over many days). "
        "`x` is the result column for the x axis and `y` a list of 1 to 3 numeric result columns: alias them in the SELECT. Cast date_trunc results with ::date. "
        "The sql must already aggregate to the granularity named in the title: per week means GROUP BY date_trunc('week', local_date)::date, per month date_trunc('month', ...); never plot raw days under a weekly title. For 'last N weeks' filter by date (WHERE local_date >= date_trunc('week', current_date) - interval 'N-1 weeks'), never LIMIT: weeks without activity are filled in by the app. "
        "`title` is short, `x_label` and `y_label` name the axes with units, all in the user's language. Returns the rows used (to describe) or an error to fix once. "
        "The sql may use ONLY these tables (tool names are not tables): " + TABLES,
        {"sql": {"type": "string"}, "kind": {"type": "string", "enum": ["bar", "line"]}, "x": {"type": "string"},
         "y": {"type": "array", "items": {"type": "string"}}, "title": {"type": "string"},
         "x_label": {"type": "string"}, "y_label": {"type": "string"}}, ["sql", "kind", "x", "y", "title"]),
    _fn("run_sql", "One read-only SELECT. Use for grouping or ranking the other tools cannot do, e.g. per month (date_trunc), best or longest, averages. Rankings must add NULLS LAST and filter sport_type (a NULL distance sorts first otherwise). Tables: " + TABLES,
        {"sql": {"type": "string"}}, ["sql"]),
]


def system_prompt(today, first_day, last_day):
    monday = today - timedelta(days=today.weekday())
    return f"""You answer questions about the user's own COROS training data. Today is {today}; this ISO week started on Monday {monday}, so 'this week' has data only for days from {monday} on; the current year is {today.year}, so 'this year' means {today.year}.
- Scope: only the user's training, health and fitness data and running or training advice based on it. For anything else (people, news, general knowledge), reply in one sentence that you only answer about their COROS data, and call no tool.
- Get every number from a tool result. Never state a number that is not in a result.
- If a tool returns no rows, say there is no data for that; do not guess.
- Reply in the language of the question (Vietnamese or English), short and clear.
- Pace is seconds per km in the data: show it as min:sec per km. Distances are km. Dates are YYYY-MM-DD.
- COROS load ratio bands: below 0.5 Decreasing, 0.5-0.79 Resuming, 0.8-0.99 Maintaining, 1.0-1.49 Optimized, 1.5+ Excessive.
- Choose tools: training load or ratio -> daily_load; per-month, ranking or other grouping -> run_sql; fuzzy descriptions -> search_activities.
- A single 'running' question means sport_type 100 (add trail run 102 only if asked). Always filter by sport when the question names one.
- The data covers activities from {first_day} to {last_day} only; use a range that covers what the question asks, and for totals 'in the data' use the whole span.
- Per-km or lap questions: call activity_laps with the date. Activity averages are not lap values.
- Questions about training rules, what a label or metric means, or what experts say: call search_guidance first, even when no personal data is needed.
- Advice questions ('should I...', 'is it OK...', how to train): first read the user's own numbers (daily_load, weekly_totals, recent_activities), then call search_guidance. Combine both: state where the user is now from COROS data (numbers and dates), then what the guidance says.
- Sources are appended to your answer automatically; do not write links yourself. If a card has a caveat (consensus_level mixed or contested), say plainly that sources disagree or evidence is weak, before giving the number; never pick a side yourself.
- If daily_load or another data tool has no row for the day asked, say there is no data for that day and give no assessment of it; do not describe other days as if they were that day.
- Charts: when the user asks for a chart, graph or plot, call draw_chart (not run_sql) with a SELECT and the chart kind and columns; if it returns an error, fix the request once. The chart appears in the app by itself. Then describe in one or two sentences what it shows, using only numbers from the returned rows. Never write images or links.
- Never diagnose, give medical conclusions, or advise on medication or diet: say so in one sentence and suggest a doctor or professional. Pain, dizziness or illness always go to a professional.
- End every advice answer with one line: Based on COROS metrics, not medical advice.
- If search_guidance returns nothing, say you have no guidance on that instead of using general knowledge.
- Details (cadence, power, laps) exist only for some activities; a missing value means not loaded."""
