#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

from vocab_db import DEFAULT_VOCAB_DB, connect_vocab_db, ensure_schema, import_words


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="從 txt 檔匯入單字至 vocab.sqlite。")
    parser.add_argument("-l", "--language", required=True, choices=["en", "fr", "de"], help="語言表")
    parser.add_argument("-f", "--file", required=True, type=Path, help="輸入 txt（每行一個單字）")
    parser.add_argument("-s", "--source", required=True, help="來源（寫入 source 欄）")
    parser.add_argument("--vocab-db", type=Path, default=DEFAULT_VOCAB_DB, help="vocab.sqlite 路徑")
    return parser.parse_args()


def load_words(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"找不到檔案：{path}")
    words: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        word = line.strip()
        if word:
            words.append(word)
    return words


def main() -> int:
    args = parse_args()
    try:
        words = load_words(args.file)
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        return 1

    if not words:
        print("檔案中沒有單字。", file=sys.stderr)
        return 1

    conn = connect_vocab_db(args.vocab_db)
    ensure_schema(conn)
    raw_count, added, skipped = import_words(conn, args.language, words, source=args.source)
    conn.close()

    print(f"共讀取 {raw_count} 筆，已新增 {added} 筆，已跳過 {skipped} 筆（已存在）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
