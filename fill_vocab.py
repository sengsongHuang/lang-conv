#!/usr/bin/env python3
import argparse
from pathlib import Path

from vocab_db import DEFAULT_VOCAB_DB, connect_vocab_db, ensure_schema
from vocab_generate import OLLAMA_MODEL, fill_pending_words


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fill vocab.sqlite with Ollama-generated content.")
    parser.add_argument("-l", "--language", required=True, choices=["en", "fr", "de"], help="Language table")
    parser.add_argument("-n", type=int, metavar="N", help="最多製作 N 筆（已補齊的不計入）")
    parser.add_argument("--model", default=OLLAMA_MODEL, help=f"Ollama model (default: {OLLAMA_MODEL})")
    parser.add_argument("--vocab-db", type=Path, default=DEFAULT_VOCAB_DB, help="Path to vocab.sqlite")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.n is not None and args.n < 1:
        raise SystemExit("-n 必須為正整數。")

    conn = connect_vocab_db(args.vocab_db)
    ensure_schema(conn)
    fill_pending_words(conn, args.language, args.model, limit=args.n)
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
