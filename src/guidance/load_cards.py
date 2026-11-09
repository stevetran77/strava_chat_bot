"""Load guidance cards from cards.json into Postgres, approved and embedded.

Usage: .venv/bin/python src/guidance/load_cards.py
Cards are matched by (topic, source_url), so re-running updates rather than duplicates. A card without a
source_url is rejected ("no source, no card"). Every card in cards.json is loaded as approved: the owner
approves by leaving a card in the file, and removes one by deleting it there and from the table.
"""
import json
import logging
import sys
from pathlib import Path

import psycopg

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingest"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "embed"))
from embed_activities import embed_texts, vector_literal  # noqa: E402
from load_sport_records import load_env  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("load_cards")

CARDS_FILE = Path(__file__).with_name("cards.json")
LEVELS = {"consensus", "mixed", "contested"}


def read_cards(path=CARDS_FILE):
    cards = json.loads(path.read_text())
    for card in cards:
        if not card.get("source_url", "").startswith("http"):
            raise ValueError(f"card without a source link: {card.get('topic')}")
        if card.get("consensus_level") not in LEVELS:
            raise ValueError(f"bad consensus_level on card: {card.get('topic')}")
    return cards


def card_text(card):
    return f"{card['topic']}. {card['content']}"


def main():
    env = load_env()
    cards = read_cards()
    vectors = embed_texts(env["OLLAMA_URL"], env["OLLAMA_EMBED_MODEL"], [card_text(c) for c in cards])
    with psycopg.connect(
        host="127.0.0.1", port=env["POSTGRES_PORT"], dbname=env["POSTGRES_DB"],
        user=env["POSTGRES_USER"], password=env["POSTGRES_PASSWORD"],
    ) as conn:
        for card, vector in zip(cards, vectors):
            conn.execute("DELETE FROM guidance_cards WHERE topic = %s AND source_url = %s",
                         (card["topic"], card["source_url"]))
            conn.execute(
                """INSERT INTO guidance_cards (topic, content, source_url, related_metric, consensus_level, approved_at, embedding)
                   VALUES (%s, %s, %s, %s, %s, now(), %s::vector)""",
                (card["topic"], card["content"], card["source_url"], card.get("related_metric"),
                 card["consensus_level"], vector_literal(vector)))
        total = conn.execute("SELECT count(*) FROM guidance_cards WHERE approved_at IS NOT NULL").fetchone()[0]
    log.info("[OK] loaded %d card(s); %d approved cards in the database", len(cards), total)


if __name__ == "__main__":
    main()
