"""Run the evaluation questions through the chat loop and score each one.

Usage: .venv/bin/python src/eval/run_eval.py [--only SUBSTRING] [--think]
Each question starts a fresh conversation. Results are written to data/eval/ (private, git-ignored)
so runs can be compared after a change. Exit code 1 if any case fails.
"""
import argparse
import json
import re
import sys
import time
from datetime import date, datetime
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[2]
for sub in ("tools", "chat", "eval"):
    sys.path.insert(0, str(ROOT / "src" / sub))
import cases  # noqa: E402
from chat import answer  # noqa: E402
from queries import data_span, load_env  # noqa: E402
from tool_specs import system_prompt  # noqa: E402


def owner_db(env):
    conn = psycopg.connect(host="127.0.0.1", port=env["POSTGRES_PORT"], dbname=env["POSTGRES_DB"],
                           user=env["POSTGRES_USER"], password=env["POSTGRES_PASSWORD"], autocommit=True)
    return lambda sql: conn.execute(sql).fetchone()[0]


def normalise(text):
    """Make '19,41' and '1.234,5' comparable with '19.41'; lower-case the rest."""
    return re.sub(r"(?<=\d),(?=\d)", ".", text).lower()


def score(case, reply, used, db):
    problems = []
    if case.get("no_tools") and used:
        problems.append(f"called tools {used}")
    if case.get("any_tool") and not set(used) & set(case["any_tool"]):
        problems.append(f"expected one of {case['any_tool']}, used {used}")
    text = normalise(reply)
    for group in case.get("contains", []):
        if not any(normalise(str(option)) in text for option in group):
            problems.append(f"none of {group[:3]} in reply")
    for word in case.get("absent", []):
        if word.lower() in text:
            problems.append(f"reply contains '{word}'")
    return problems


def run_case(env, case, db, think):
    before = db(case["unchanged_sql"]) if case.get("unchanged_sql") else None
    span = data_span(env)
    messages = [{"role": "system", "content": system_prompt(date.today(), span["first_day"], span["last_day"])},
                {"role": "user", "content": case["question"]}]
    used = []
    started = time.time()
    reply = answer(env, messages, think, used)
    problems = score(case, reply, used, db)
    if case.get("unchanged_sql") and db(case["unchanged_sql"]) != before:
        problems.append("data changed")
    return {"id": case["id"], "question": case["question"], "reply": reply, "tools": used,
            "seconds": round(time.time() - started, 1), "problems": problems}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", default="")
    parser.add_argument("--think", action="store_true")
    args = parser.parse_args()
    env = load_env()
    db = owner_db(env)
    selected = [c for c in cases.build(db) if args.only in c["id"]]
    results = []
    for case in selected:
        result = run_case(env, case, db, args.think)
        results.append(result)
        status = "[FAIL]" if result["problems"] else "[OK]"
        print(f"{status} {case['id']} ({result['seconds']}s) {'; '.join(result['problems'])}", flush=True)
    passed = sum(1 for r in results if not r["problems"])
    print(f"\n{passed}/{len(results)} passed (think={args.think}, model={env['OLLAMA_CHAT_MODEL']})")
    out_dir = ROOT / "data" / "eval"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"results_{datetime.now():%Y%m%d_%H%M%S}.json"
    out.write_text(json.dumps({"think": args.think, "model": env["OLLAMA_CHAT_MODEL"], "results": results},
                              ensure_ascii=False, indent=1, default=str))
    print(f"details: {out.relative_to(ROOT)}")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
