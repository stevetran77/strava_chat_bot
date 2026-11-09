"""Local HTTP API for the chat UI.

Usage: .venv/bin/uvicorn --app-dir src/api server:app --host 127.0.0.1 --port 8000
Binds to localhost only: the data is private. Conversations live in memory and vanish on restart.
GET /api/models -> chat models the UI may pick (OLLAMA_CHAT_MODELS, comma list; falls back to OLLAMA_CHAT_MODEL) and the default.
POST /api/chat {conversation_id?, question, model?, think?} -> answer text, tools used, charts [{kind, title, x, y, x_label, y_label, rows}], sources.
"""
import sys
import uuid
from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[2]
for sub in ("chat", "tools"):
    sys.path.insert(0, str(ROOT / "src" / sub))
from chat import answer_full  # noqa: E402
from queries import data_span, load_env  # noqa: E402
from tool_specs import system_prompt  # noqa: E402

app = FastAPI(title="COROS chatbot")
conversations = {}


class ChatRequest(BaseModel):
    question: str
    conversation_id: str | None = None
    think: bool = False
    model: str | None = None


def allowed_models(env):
    """Models the UI may choose: the optional OLLAMA_CHAT_MODELS list, always including the default chat model."""
    listed = [name.strip() for name in env.get("OLLAMA_CHAT_MODELS", "").split(",") if name.strip()]
    default = env["OLLAMA_CHAT_MODEL"]
    return default, listed if default in listed else [default, *listed]


def new_messages():
    span = data_span()
    return [{"role": "system", "content": system_prompt(date.today(), span["first_day"], span["last_day"])}]


@app.get("/api/models")
def models():
    default, names = allowed_models(load_env())
    return {"default": default, "models": names}


@app.post("/api/chat")
def chat(request: ChatRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="empty question")
    env = load_env()
    default, names = allowed_models(env)
    model = request.model or default
    if model not in names:
        raise HTTPException(status_code=400, detail="unknown model")
    conversation_id = request.conversation_id or uuid.uuid4().hex
    messages = conversations.setdefault(conversation_id, new_messages())
    messages.append({"role": "user", "content": question})
    result = answer_full({**env, "OLLAMA_CHAT_MODEL": model}, messages, request.think)
    return {"conversation_id": conversation_id, **result}
