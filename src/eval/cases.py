"""Evaluation questions. Expected values are computed from the database at run time (direct SQL,
owner role), so they stay right when data changes and never come from the tools under test.

A case is a dict:
  question        text sent to the chatbot
  any_tool        answer must call at least one of these tools (omit when not checked)
  no_tools        True: answer must call no tool
  contains        list of groups; each group is a list of alternatives, one of which must appear
  absent          strings that must not appear
  unchanged_sql   SQL returning one value that must be the same before and after the question
"""
NO_DATA = ["không có dữ liệu", "chưa có dữ liệu", "không có thông tin", "no data", "không có", "chưa chạy", "chưa có"]


def km(value):
    """Spellings of a distance the model may use."""
    if value is None:
        return NO_DATA + ["0 km"]
    value = float(value)
    return [f"{value:.2f}", f"{value:.1f}", f"{value:.0f} km"]


def pace(seconds):
    if seconds is None:
        return NO_DATA
    m, s = divmod(int(round(float(seconds))), 60)
    return [f"{m}:{s:02d}", f"{m} phút {s} giây", f"{m}'{s:02d}"]


def text(value):
    """Expected text for a plain value; a NULL means the reply should say there is no data."""
    return NO_DATA if value is None else [str(value)]


def build(db):
    """`db(sql)` returns the first column of the first row."""
    week = "date_trunc('week', current_date)"
    return [
        {"id": "week_run_km", "question": "Tuần này tôi chạy bao nhiêu km?", "any_tool": ["weekly_totals", "run_sql", "period_totals"],
         "contains": [km(db(f"SELECT sum(distance_km) FROM activities WHERE sport_type = 100 AND local_date >= {week}"))]},
        {"id": "last_run_km", "question": "Buổi chạy gần nhất của tôi dài bao nhiêu km?", "any_tool": ["recent_activities", "run_sql"],
         "contains": [km(db("SELECT distance_km FROM activities WHERE sport_type = 100 ORDER BY started_at DESC LIMIT 1"))]},
        {"id": "last_run_hr", "question": "Nhịp tim trung bình của buổi chạy gần nhất?", "any_tool": ["recent_activities", "run_sql"],
         "contains": [text(db("SELECT avg_hr FROM activities WHERE sport_type = 100 ORDER BY started_at DESC LIMIT 1"))]},
        {"id": "oct_run_count", "question": "Tháng 10 năm 2026 tôi có bao nhiêu buổi chạy bộ ngoài trời?", "any_tool": ["period_totals", "run_sql"],
         "contains": [text(db("SELECT count(*) FROM activities WHERE sport_type = 100 AND local_date BETWEEN '2026-10-01' AND '2026-10-31'"))]},
        {"id": "oct_run_km", "question": "Tổng km chạy bộ ngoài trời trong tháng 10 năm 2026?", "any_tool": ["period_totals", "run_sql"],
         "contains": [km(db("SELECT sum(distance_km) FROM activities WHERE sport_type = 100 AND local_date BETWEEN '2026-10-01' AND '2026-10-31'"))]},
        {"id": "year_pace", "question": "Pace trung bình các buổi chạy ngoài trời năm nay?", "any_tool": ["period_totals", "run_sql"],
         "contains": [pace(db("SELECT sum(duration_s)::float / sum(distance_km) FROM activities WHERE sport_type = 100 AND local_date >= date_trunc('year', current_date)"))]},
        {"id": "best_month", "question": "Tháng nào tôi chạy nhiều km nhất?", "any_tool": ["run_sql"],
         "contains": [km(db("SELECT sum(distance_km) FROM activities WHERE sport_type = 100 GROUP BY date_trunc('month', started_at) ORDER BY 1 DESC LIMIT 1"))]},
        {"id": "longest_run", "question": "Buổi chạy dài nhất của tôi dài bao nhiêu km?", "any_tool": ["run_sql"],
         "contains": [km(db("SELECT max(distance_km) FROM activities WHERE sport_type = 100")) + km(db("SELECT max(distance_km) FROM activities WHERE sport_type IN (100, 101, 102)"))]},
        {"id": "swim_count", "question": "Tôi đã bơi bao nhiêu buổi trong dữ liệu?", "any_tool": ["period_totals", "run_sql"],
         "contains": [text(db("SELECT count(*) FROM activities WHERE sport_type = 301"))]},
        {"id": "walk_km_english", "question": "How many km did I walk in total?", "any_tool": ["period_totals", "run_sql"],
         "contains": [km(db("SELECT sum(distance_km) FROM activities WHERE sport_type = 900"))]},
        {"id": "load_label", "question": "Nhãn tải tập luyện COROS của ngày 2026-11-08 là gì?", "any_tool": ["daily_load", "run_sql"],
         "contains": [text(db("SELECT load_comment FROM daily_metrics WHERE metric_date = '2026-11-08'"))]},
        {"id": "load_ratio", "question": "Tỉ lệ tải ngày 2026-11-08 là bao nhiêu?", "any_tool": ["daily_load", "run_sql"],
         "contains": [text(db("SELECT load_ratio FROM daily_metrics WHERE metric_date = '2026-11-08'"))]},
        {"id": "fastest_km", "question": "Trong buổi chạy ngày 2026-11-07, km nào nhanh nhất và pace bao nhiêu?", "any_tool": ["activity_laps", "run_sql"],
         "contains": [pace(db("SELECT min(l.avg_pace_s_per_km) FROM laps l JOIN activities a USING (label_id) WHERE a.local_date = '2026-11-07' AND a.sport_type = 100"))]},
        {"id": "avg_power_last_run", "question": "Công suất trung bình (power) của buổi chạy gần nhất?", "any_tool": ["recent_activities", "run_sql"],
         "contains": [text(db("SELECT avg_power FROM activities WHERE sport_type = 100 ORDER BY started_at DESC LIMIT 1"))]},
        {"id": "resting_hr_missing", "question": "Nhịp tim nghỉ ngơi của tôi ngày 2026-11-05 là bao nhiêu?", "contains": [NO_DATA]},
        {"id": "future_week", "question": "Tuần sau tôi sẽ chạy bao nhiêu km?", "contains": [NO_DATA + ["không thể", "không biết", "dự đoán"]]},
        {"id": "semantic_search", "question": "Tìm những buổi chạy dài và chậm của tôi", "any_tool": ["search_activities", "run_sql"]},
        {"id": "greeting", "question": "Xin chào", "no_tools": True},
        {"id": "out_of_scope_person", "question": "who is Ronaldo?", "no_tools": True, "absent": ["Portug", "footballer", "Real Madrid"]},
        {"id": "out_of_scope_fact", "question": "Thủ đô của Pháp là gì?", "no_tools": True, "absent": ["Paris"]},
        {"id": "delete_request", "question": "Xoá hết dữ liệu hoạt động của tôi đi", "unchanged_sql": "SELECT count(*) FROM activities"},
    ]
