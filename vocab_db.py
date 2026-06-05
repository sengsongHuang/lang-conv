import sqlite3
from pathlib import Path
from typing import Any, Optional


DEFAULT_VOCAB_DB = Path(__file__).parent / "working" / "vocab.sqlite"

LANGUAGE_TO_TABLE = {
    "en": "english_vocab",
    "fr": "french_vocab",
    "de": "germany_vocab",
}

TABLE_DDL = """
CREATE TABLE IF NOT EXISTS {table} (
    serial_no INTEGER PRIMARY KEY AUTOINCREMENT,
    單字 TEXT NOT NULL,
    中文解釋 TEXT,
    字卡 TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_{table}_word_nocase ON {table}(單字 COLLATE NOCASE);
"""


def connect_vocab_db(db_path: Optional[Path] = None) -> sqlite3.Connection:
    path = db_path or DEFAULT_VOCAB_DB
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_schema(conn: sqlite3.Connection) -> None:
    for table in LANGUAGE_TO_TABLE.values():
        conn.executescript(TABLE_DDL.format(table=table))
    conn.commit()


def table_for_language(language: str) -> str:
    if language not in LANGUAGE_TO_TABLE:
        raise ValueError(f"unsupported language: {language}")
    return LANGUAGE_TO_TABLE[language]


def word_exists(conn: sqlite3.Connection, language: str, word: str) -> bool:
    table = table_for_language(language)
    row = conn.execute(
        f'SELECT 1 FROM {table} WHERE 單字 = ? COLLATE NOCASE LIMIT 1',
        (word,),
    ).fetchone()
    return row is not None


def insert_word(conn: sqlite3.Connection, language: str, word: str) -> bool:
    if word_exists(conn, language, word):
        return False
    table = table_for_language(language)
    conn.execute(
        f'INSERT INTO {table} (單字, 中文解釋, 字卡) VALUES (?, NULL, NULL)',
        (word,),
    )
    conn.commit()
    return True


def fetch_pending_words(conn: sqlite3.Connection, language: str) -> list[dict[str, Any]]:
    table = table_for_language(language)
    rows = conn.execute(
        f"""
        SELECT serial_no, 單字, 中文解釋, 字卡
        FROM {table}
        WHERE 中文解釋 IS NULL OR 字卡 IS NULL
           OR TRIM(中文解釋) = '' OR TRIM(字卡) = ''
        ORDER BY serial_no
        """
    ).fetchall()
    return [dict(row) for row in rows]


def update_word_content(
    conn: sqlite3.Connection,
    language: str,
    serial_no: int,
    zh_meaning: str,
    flashcard: str,
) -> None:
    table = table_for_language(language)
    conn.execute(
        f'UPDATE {table} SET 中文解釋 = ?, 字卡 = ? WHERE serial_no = ?',
        (zh_meaning, flashcard, serial_no),
    )
    conn.commit()


def fetch_word(conn: sqlite3.Connection, language: str, word: str) -> Optional[dict[str, Any]]:
    table = table_for_language(language)
    row = conn.execute(
        f"""
        SELECT serial_no, 單字, 中文解釋, 字卡
        FROM {table}
        WHERE 單字 = ? COLLATE NOCASE
        LIMIT 1
        """,
        (word,),
    ).fetchone()
    return dict(row) if row else None


def fetch_words(
    conn: sqlite3.Connection,
    language: str,
    start_serial: Optional[int] = None,
    limit: Optional[int] = None,
) -> list[dict[str, Any]]:
    table = table_for_language(language)
    query = f"""
        SELECT serial_no, 單字, 中文解釋, 字卡
        FROM {table}
    """
    params: list[Any] = []
    if start_serial is not None:
        query += " WHERE serial_no >= ?"
        params.append(start_serial)
    query += " ORDER BY serial_no"
    if limit is not None:
        query += " LIMIT ?"
        params.append(limit)
    rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def dedupe_words_preserve_order(words: list[str]) -> tuple[list[str], int]:
    seen: set[str] = set()
    result: list[str] = []
    for word in words:
        key = word.casefold()
        if key not in seen:
            seen.add(key)
            result.append(word)
    return result, len(words)
