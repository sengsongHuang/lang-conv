#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

from vocab_db import (
    DEFAULT_VOCAB_DB,
    connect_vocab_db,
    fetch_word,
    fetch_words,
    format_create_at,
)

SEPARATOR = "\t"
CARD_SEPARATOR = "---"
EMPTY = "（空）"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="從 vocab.sqlite 匯出 CSV 或字卡。")
    parser.add_argument("-l", "--language", required=True, choices=["en", "fr", "de"], help="語言表")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--csv", action="store_true", help="匯出 CSV：單字\\t單行中文解釋")
    group.add_argument("--flashcard", action="store_true", help="匯出字卡 Markdown")
    group.add_argument("--check", metavar="WORD", help="查詢單字並顯示 serial_no、中文解釋、字卡")
    parser.add_argument("--start", type=int, metavar="N", help="從 serial_no >= N 開始（含 N）")
    parser.add_argument("--count", type=int, metavar="N", help="最多匯出 N 筆")
    parser.add_argument("-o", "--output", type=Path, help="輸出檔（省略則寫 stdout）")
    parser.add_argument("--vocab-db", type=Path, default=DEFAULT_VOCAB_DB, help="vocab.sqlite 路徑")
    return parser.parse_args()


def to_single_line(text: str) -> str:
    return " ".join(line.strip() for line in text.splitlines() if line.strip())


def field_text(value: object) -> str:
    if value is None or not str(value).strip():
        return EMPTY
    return str(value).strip()


def format_create_at_field(value: object) -> str:
    if value is None or str(value).strip() == "":
        return EMPTY
    return f"{value} ({format_create_at(value)})"


def format_check_output(row: dict) -> str:
    serial_no = row["serial_no"]
    lines = [
        f"serial_no = {serial_no}",
        "",
        "單字",
        row["單字"],
        "",
        "source",
        field_text(row.get("source")),
        "",
        "create_at",
        format_create_at_field(row.get("create_at")),
        "",
        "中文解釋",
        field_text(row.get("中文解釋")),
        "",
        "字卡",
        field_text(row.get("字卡")),
        "",
    ]
    return "\n".join(lines)


def build_csv_rows(rows: list[dict]) -> list[str]:
    lines: list[str] = []
    for row in rows:
        meaning = row.get("中文解釋")
        if not meaning or not str(meaning).strip():
            continue
        word = row["單字"]
        lines.append(f"{word}{SEPARATOR}{to_single_line(str(meaning))}")
    return lines


def build_flashcard_text(rows: list[dict]) -> str:
    cards: list[str] = []
    for row in rows:
        card = row.get("字卡")
        if not card or not str(card).strip():
            continue
        cards.append(str(card).strip())
    return f"\n\n{CARD_SEPARATOR}\n\n".join(cards)


def main() -> int:
    args = parse_args()
    conn = connect_vocab_db(args.vocab_db)

    if args.check:
        row = fetch_word(conn, args.language, args.check)
        conn.close()
        if row is None:
            print(f"找不到單字：{args.check}", file=sys.stderr)
            return 1
        sys.stdout.write(format_check_output(row))
        return 0

    if args.start is not None and args.start < 1:
        print("--start 必須為正整數。", file=sys.stderr)
        return 1
    if args.count is not None and args.count < 1:
        print("--count 必須為正整數。", file=sys.stderr)
        return 1

    rows = fetch_words(conn, args.language, start_serial=args.start, limit=args.count)
    conn.close()

    if args.csv:
        content = "\n".join(build_csv_rows(rows))
        if content:
            content += "\n"
    else:
        content = build_flashcard_text(rows)
        if content:
            content += "\n"

    if not content.strip():
        print("沒有可匯出的資料。", file=sys.stderr)
        return 1

    if args.output:
        args.output.write_text(content, encoding="utf-8")
        print(f"已寫入 {len(content.encode('utf-8'))} bytes → {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
