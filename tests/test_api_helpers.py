"""API wiring. No server, database or Docker needed."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "api"))
import server  # noqa: E402


class ChatRouteTest(unittest.TestCase):
    def test_empty_question_is_rejected(self):
        with self.assertRaises(server.HTTPException) as caught:
            server.chat(server.ChatRequest(question="   "))
        self.assertEqual(caught.exception.status_code, 400)

    def test_unknown_model_is_rejected(self):
        with self.assertRaises(server.HTTPException) as caught:
            server.chat(server.ChatRequest(question="hi", model="not-a-model"))
        self.assertEqual(caught.exception.status_code, 400)

    def test_allowed_models_keeps_default_first(self):
        default, names = server.allowed_models({"OLLAMA_CHAT_MODEL": "a", "OLLAMA_CHAT_MODELS": "b, c"})
        self.assertEqual((default, names), ("a", ["a", "b", "c"]))
        self.assertEqual(server.allowed_models({"OLLAMA_CHAT_MODEL": "a"})[1], ["a"])


if __name__ == "__main__":
    unittest.main()
