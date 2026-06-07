#!/usr/bin/env python3
import argparse
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any, Optional, Union

from vocab_db import (
    DEFAULT_VOCAB_DB,
    connect_vocab_db,
    ensure_schema,
    import_words,
)


DEFAULT_DB = Path(__file__).parent / "working" / "KoboReader.sqlite"

LANGUAGE_CHOICES = [
    ("en", "english_vocab"),
    ("fr", "french_vocab"),
    ("de", "germany_vocab"),
]


def connect_kobo_db(db_path: Path) -> sqlite3.Connection:
    if not db_path.exists():
        print(f"找不到資料庫：{db_path}", file=sys.stderr)
        sys.exit(1)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def fetch_books(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT bm.VolumeID,
               (
                   SELECT BookTitle
                   FROM content
                   WHERE BookID = bm.VolumeID
                     AND BookTitle IS NOT NULL
                   LIMIT 1
               ) AS BookTitle,
               COUNT(*) AS cnt
        FROM Bookmark bm
        WHERE bm.Text IS NOT NULL
        GROUP BY bm.VolumeID
        ORDER BY BookTitle COLLATE NOCASE
        """
    ).fetchall()


def content_id_to_title(content_id: str) -> str:
    if "!EPUB!" in content_id:
        return content_id.split("!EPUB!", 1)[1]
    if content_id.startswith("EPUB/"):
        return content_id[len("EPUB/") :]
    if "!" in content_id:
        return content_id.rsplit("!", 1)[-1]
    return content_id


def is_file_like_title(title: str) -> bool:
    return "/" in title or title.endswith((".xhtml", ".html", ".htm"))


def chapter_sort_key(title: str, volume_index: Optional[int]) -> tuple[Any, ...]:
    if volume_index is not None:
        return (0, volume_index, title)

    chapter_match = re.search(r"chapter0*(\d+)", title, re.IGNORECASE)
    if chapter_match:
        return (1, int(chapter_match.group(1)), title)

    xhtml_match = re.search(r"xhtml-0-(\d+)", title, re.IGNORECASE)
    if xhtml_match:
        return (1, int(xhtml_match.group(1)), title)

    return (2, title.lower())


def fetch_chapters(conn: sqlite3.Connection, volume_id: str) -> list[dict[str, Any]]:
    content_rows = conn.execute(
        """
        SELECT ContentID, Title, VolumeIndex
        FROM content
        WHERE BookID = ?
        """,
        (volume_id,),
    ).fetchall()

    bookmark_rows = conn.execute(
        """
        SELECT ContentID, COUNT(*) AS cnt
        FROM Bookmark
        WHERE VolumeID = ?
          AND Text IS NOT NULL
        GROUP BY ContentID
        """,
        (volume_id,),
    ).fetchall()

    chapters: dict[str, dict[str, Any]] = {}

    for row in content_rows:
        title = row["Title"]
        if not is_file_like_title(title):
            continue
        chapters[row["ContentID"]] = {
            "ContentID": row["ContentID"],
            "Title": title,
            "VolumeIndex": row["VolumeIndex"],
            "cnt": 0,
        }

    for row in bookmark_rows:
        content_id = row["ContentID"]
        if content_id in chapters:
            chapters[content_id]["cnt"] = row["cnt"]
            continue

        chapters[content_id] = {
            "ContentID": content_id,
            "Title": content_id_to_title(content_id),
            "VolumeIndex": None,
            "cnt": row["cnt"],
        }

    result = list(chapters.values())
    result.sort(
        key=lambda item: chapter_sort_key(item["Title"], item["VolumeIndex"])
    )
    return result


def fetch_highlights_for_chapter(conn: sqlite3.Connection, content_id: str) -> list[str]:
    rows = conn.execute(
        """
        SELECT Text
        FROM Bookmark
        WHERE ContentID = ?
          AND Text IS NOT NULL
        ORDER BY DateCreated, StartOffset
        """,
        (content_id,),
    ).fetchall()
    return [row["Text"].strip() for row in rows if row["Text"].strip()]


def fetch_highlights_for_book(
    conn: sqlite3.Connection, volume_id: str, chapters: list[dict[str, Any]]
) -> list[str]:
    order = {chapter["ContentID"]: index for index, chapter in enumerate(chapters)}
    rows = conn.execute(
        """
        SELECT ContentID, Text, DateCreated, StartOffset
        FROM Bookmark
        WHERE VolumeID = ?
          AND Text IS NOT NULL
        """,
        (volume_id,),
    ).fetchall()
    rows = sorted(
        rows,
        key=lambda row: (
            order.get(row["ContentID"], 10_000),
            row["DateCreated"] or "",
            row["StartOffset"] or 0,
        ),
    )
    return [row["Text"].strip() for row in rows if row["Text"].strip()]


def prompt_choice(label: str, max_index: int, allow_all: bool = False) -> Union[int, str]:
    while True:
        try:
            raw = input(f"{label} ").strip()
        except EOFError:
            print(file=sys.stderr)
            sys.exit(1)

        if allow_all and (not raw or raw.lower() in {"all", "[all]", "全部", "a"}):
            return "all"

        if not raw.isdigit():
            print("請輸入數字。", file=sys.stderr)
            continue

        choice = int(raw)
        if 1 <= choice <= max_index:
            return choice

        print(f"請輸入 1 到 {max_index} 之間的數字。", file=sys.stderr)


def prompt_language() -> str:
    print()
    for index, (code, _) in enumerate(LANGUAGE_CHOICES, start=1):
        print(f"[{index}] {code}")
    while True:
        try:
            raw = input("選擇語言... ").strip()
        except EOFError:
            print(file=sys.stderr)
            sys.exit(1)
        if raw.isdigit():
            choice = int(raw)
            if 1 <= choice <= len(LANGUAGE_CHOICES):
                return LANGUAGE_CHOICES[choice - 1][0]
        print("請輸入 1 到 3 之間的數字。", file=sys.stderr)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="從 Kobo SQLite 匯入劃線單字至 vocab.sqlite。")
    parser.add_argument(
        "database",
        nargs="?",
        default=str(DEFAULT_DB),
        help=f"KoboReader.sqlite 路徑（預設：{DEFAULT_DB}）",
    )
    parser.add_argument(
        "--vocab-db",
        type=Path,
        default=DEFAULT_VOCAB_DB,
        help=f"vocab.sqlite 路徑（預設：{DEFAULT_VOCAB_DB}）",
    )
    parser.add_argument(
        "--export-only",
        action="store_true",
        help="只印出劃線至 stdout，不寫入 vocab.sqlite",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    db_path = Path(args.database)
    kobo_conn = connect_kobo_db(db_path)

    books = fetch_books(kobo_conn)
    if not books:
        print("資料庫中沒有劃線資料。", file=sys.stderr)
        return 1

    print()
    for index, book in enumerate(books, start=1):
        title = book["BookTitle"] or book["VolumeID"]
        print(f"[{index}] {title} ({book['cnt']})")

    book_choice = prompt_choice("選擇書本...", len(books))
    selected_book = books[book_choice - 1]
    volume_id = selected_book["VolumeID"]
    book_title = selected_book["BookTitle"] or selected_book["VolumeID"]

    chapters = fetch_chapters(kobo_conn, volume_id)
    if not chapters:
        print("這本書找不到章節檔案。", file=sys.stderr)
        return 1

    print()
    for index, chapter in enumerate(chapters, start=1):
        print(f"[{index}] {chapter['Title']} ({chapter['cnt']})")
    print("[all] 全部")

    chapter_choice = prompt_choice("選擇章節...", len(chapters), allow_all=True)

    if chapter_choice == "all":
        highlights = fetch_highlights_for_book(kobo_conn, volume_id, chapters)
    else:
        selected_chapter = chapters[chapter_choice - 1]
        highlights = fetch_highlights_for_chapter(kobo_conn, selected_chapter["ContentID"])

    kobo_conn.close()

    if args.export_only:
        for word in highlights:
            print(word)
        return 0

    language = prompt_language()

    vocab_conn = connect_vocab_db(args.vocab_db)
    ensure_schema(vocab_conn)
    raw_count, added, skipped = import_words(
        vocab_conn, language, highlights, source=book_title
    )
    vocab_conn.close()

    print()
    print(f"共讀取 {raw_count} 筆劃線，已新增 {added} 筆，已跳過 {skipped} 筆（已存在）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
