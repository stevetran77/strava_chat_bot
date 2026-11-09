"""Terminal chat over the COROS data: the LLM picks tools, tools query Postgres, the LLM answers.

Usage: .venv/bin/python src/chat/chat.py            interactive (empty line or Ctrl+D to quit)
       .venv/bin/python src/chat/chat.py "question"  one question
       add --think to turn on the model's thinking mode (slower, maybe better).
Every tool call is printed with its row count, so each answer shows where its numbers came from.
"""
import argparse
import json
import logging
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "charts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from draw import draw_chart  # noqa: E402
from queries import TOOLS as QUERY_TOOLS, data_span, load_env  # noqa: E402
from tool_specs import TOOL_SPECS, system_prompt  # noqa: E402

log = logging.getLogger("chat")
TOOLS = {**QUERY_TOOLS, "draw_chart": draw_chart}


def ask_model(env, messages, think):
    body = json.dumps({"model": env["OLLAMA_CHAT_MODEL"], "messages": messages, "tools": TOOL_SPECS,
                       "stream": False, "think": think}).encode()
    request = urllib.request.Request(f"{env['OLLAMA_URL']}/api/chat", body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=600) as response:
        return json.loads(response.read())["message"]


def run_tool(name, arguments):
    """Run one tool call; errors go back to the model as data so it can retry or explain."""
    if name not in TOOLS:
        return {"error": f"unknown tool {name}"}
    try:
        return TOOLS[name](**arguments)
    except Exception as exc:  # noqa: BLE001 - any failure is reported to the model
        log.warning("tool %s failed: %s", name, exc)
        return {"error": f"{type(exc).__name__}: {exc}"}


def describe(name, arguments, result):
    if isinstance(result, dict) and "chart" in result:
        size = f"chart '{result['chart']['title']}' ({result['rows_used']} rows)"
    else:
        size = f"{len(result)} row(s)" if isinstance(result, list) else "error"
    return f"  [tool] {name}({json.dumps(arguments, ensure_ascii=False)[:300]}) -> {size}"


def sources_footer(cards):
    """Source list for the guidance cards the model read, added by code so it never depends on the model."""
    seen, lines = set(), []
    for card in cards:
        if card["source_url"] not in seen:
            seen.add(card["source_url"])
            note = "" if card["consensus_level"] == "consensus" else f" ({card['consensus_level']})"
            lines.append(f"  - {card['topic']}{note}: {card['source_url']}")
    return "\nSources:\n" + "\n".join(lines) if lines else ""


DISCLAIMER = "Based on COROS metrics, not medical advice."


def with_disclaimer(text):
    return text if DISCLAIMER.lower() in text.lower() else f"{text}\n\n{DISCLAIMER}"


IMAGE_MARKDOWN = re.compile(r"!\[[^\]]*\]\([^)]*\)")
TOOL_ROUNDS_EXCEEDED = "[FAIL] too many tool rounds without an answer"


def answer_full(env, messages, think):
    """Loop: model asks for tools, we run them, until it replies with text.

    Returns {"text", "tools": [{name, arguments, summary}], "charts": [spec, ...], "sources": [card, ...]}.
    Sources, charts and the disclaimer come from code, never from what the model chose to write.
    """
    tools, charts, cards = [], [], []
    for _ in range(int(env["CHAT_MAX_TOOL_ROUNDS"])):
        message = ask_model(env, messages, think)
        messages.append(message)
        calls = message.get("tool_calls") or []
        if not calls:
            text = re.sub(r"\n{3,}", "\n\n", IMAGE_MARKDOWN.sub("", message.get("content", ""))).strip()
            return {"text": with_disclaimer(text) if cards else text, "tools": tools, "charts": charts, "sources": cards}
        for call in calls:
            name, arguments = call["function"]["name"], call["function"].get("arguments") or {}
            result = run_tool(name, arguments)
            if name == "search_guidance" and isinstance(result, list):
                cards.extend(result)
            tools.append({"name": name, "arguments": arguments, "summary": describe(name, arguments, result).split("-> ")[-1]})
            if isinstance(result, dict) and "chart" in result:
                charts.append(result["chart"])
                result = {"chart_drawn": True, "rows_used": result["rows_used"], "rows": result["chart"]["rows"][:int(env["TOOL_MAX_ROWS"])]}
            messages.append({"role": "tool", "tool_name": name, "content": json.dumps(result, default=str)})
    return {"text": TOOL_ROUNDS_EXCEEDED, "tools": tools, "charts": charts, "sources": cards}


def answer(env, messages, think, used=None):
    """Text-only view of answer_full for the terminal and the evaluation runner."""
    result = answer_full(env, messages, think)
    for tool in result["tools"]:
        print(f"  [tool] {tool['name']}({json.dumps(tool['arguments'], ensure_ascii=False)[:300]}) -> {tool['summary']}")
        if used is not None:
            used.append(tool["name"])
    chart_lines = "".join(f"\n[chart] {chart['kind']} \"{chart['title']}\" ({len(chart['rows'])} rows)" for chart in result["charts"])
    return result["text"] + chart_lines + sources_footer(result["sources"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question", nargs="?")
    parser.add_argument("--think", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.WARNING, format="%(message)s")
    env = load_env()
    span = data_span()
    messages = [{"role": "system", "content": system_prompt(date.today(), span["first_day"], span["last_day"])}]
    while True:
        question = args.question or input("\nYou> ").strip()
        if not question:
            return
        messages.append({"role": "user", "content": question})
        print(answer(env, messages, args.think))
        if args.question:
            return


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print()
