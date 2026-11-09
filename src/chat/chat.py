"""Terminal chat over the COROS data: the LLM picks tools, tools query Postgres, the LLM answers.

Usage: .venv/bin/python src/chat/chat.py            interactive (empty line or Ctrl+D to quit)
       .venv/bin/python src/chat/chat.py "question"  one question
       add --think to turn on the model's thinking mode (slower, maybe better).
Every tool call is printed with its row count, so each answer shows where its numbers came from.
"""
import argparse
import json
import logging
import sys
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from queries import TOOLS, data_span, load_env  # noqa: E402
from tool_specs import TOOL_SPECS, system_prompt  # noqa: E402

log = logging.getLogger("chat")


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
    size = f"{len(result)} row(s)" if isinstance(result, list) else "error"
    return f"  [tool] {name}({json.dumps(arguments, ensure_ascii=False)}) -> {size}"


def answer(env, messages, think, used=None):
    """Loop: model asks for tools, we run them, until it replies with text. `used` collects tool names."""
    for _ in range(int(env["CHAT_MAX_TOOL_ROUNDS"])):
        message = ask_model(env, messages, think)
        messages.append(message)
        calls = message.get("tool_calls") or []
        if not calls:
            return message.get("content", "").strip()
        for call in calls:
            name, arguments = call["function"]["name"], call["function"].get("arguments") or {}
            result = run_tool(name, arguments)
            if used is not None:
                used.append(name)
            print(describe(name, arguments, result))
            messages.append({"role": "tool", "tool_name": name, "content": json.dumps(result, default=str)})
    return "[FAIL] too many tool rounds without an answer"


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
