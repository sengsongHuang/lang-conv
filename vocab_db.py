import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


DEFAULT_VOCAB_DB = Path(__file__).parent / "working" / "vocab.sqlite"

LANGUAGE_TO_TABLE = {
    "en": "english_vocab",
    "fr": "french_vocab",
    "de": "germany_vocab",
}

VOCAB_COLUMNS = ("serial_no", "單字", "中文解釋", "字卡", "source", "create_at")

TABLE_DDL = """
CREATE TABLE IF NOT EXISTS {table} (
    serial_no INTEGER PRIMARY KEY AUTOINCREMENT,
    單字 TEXT NOT NULL,
    中文解釋 TEXT,
    字卡 TEXT,
    source TEXT,
    create_at INTEGER
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
    migrate_schema(conn)


def table_columns(conn: sqlite3.Connection, table: str) -> dict[str, str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {row["name"]: row["type"].upper() for row in rows}


def rebuild_table_with_integer_create_at(conn: sqlite3.Connection, table: str) -> None:
    conn.executescript(
        f"""
        CREATE TABLE {table}_new (
            serial_no INTEGER PRIMARY KEY AUTOINCREMENT,
            單字 TEXT NOT NULL,
            中文解釋 TEXT,
            字卡 TEXT,
            source TEXT,
            create_at INTEGER
        );
        INSERT INTO {table}_new (serial_no, 單字, 中文解釋, 字卡, source, create_at)
        SELECT
            serial_no,
            單字,
            中文解釋,
            字卡,
            source,
            CASE
                WHEN create_at IS NULL OR TRIM(CAST(create_at AS TEXT)) = '' THEN NULL
                WHEN CAST(create_at AS TEXT) GLOB '[0-9]*' THEN CAST(create_at AS INTEGER)
                ELSE CAST(strftime('%s', create_at) AS INTEGER)
            END
        FROM {table};
        DROP TABLE {table};
        ALTER TABLE {table}_new RENAME TO {table};
        CREATE UNIQUE INDEX IF NOT EXISTS idx_{table}_word_nocase ON {table}(單字 COLLATE NOCASE);
        """
    )


def migrate_schema(conn: sqlite3.Connection) -> None:
    for table in LANGUAGE_TO_TABLE.values():
        columns = table_columns(conn, table)
        if not columns:
            continue

        if "source" not in columns:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN source TEXT")

        if "create_at" not in columns:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN create_at INTEGER")
        elif columns["create_at"] != "INTEGER":
            rebuild_table_with_integer_create_at(conn, table)

    conn.commit()


def select_columns() -> str:
    return ", ".join(VOCAB_COLUMNS)


def now_timestamp() -> int:
    return int(datetime.now().timestamp())


def format_create_at(value: Any) -> str:
    if value is None or str(value).strip() == "":
        return ""
    try:
        ts = int(value)
    except (TypeError, ValueError):
        return str(value)
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


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


def insert_word(
    conn: sqlite3.Connection,
    language: str,
    word: str,
    source: Optional[str] = None,
    create_at: Optional[int] = None,
) -> bool:
    if word_exists(conn, language, word):
        return False
    table = table_for_language(language)
    if create_at is None:
        create_at = now_timestamp()
    conn.execute(
        f"""
        INSERT INTO {table} (單字, 中文解釋, 字卡, source, create_at)
        VALUES (?, NULL, NULL, ?, ?)
        """,
        (word, source, create_at),
    )
    conn.commit()
    return True


def fetch_pending_words(conn: sqlite3.Connection, language: str) -> list[dict[str, Any]]:
    table = table_for_language(language)
    rows = conn.execute(
        f"""
        SELECT {select_columns()}
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
        SELECT {select_columns()}
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
        SELECT {select_columns()}
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


def import_words(
    conn: sqlite3.Connection,
    language: str,
    words: list[str],
    source: str,
) -> tuple[int, int, int]:
    deduped, raw_count = dedupe_words_preserve_order(words)
    added = 0
    skipped = 0
    for word in deduped:
        if insert_word(conn, language, word, source=source):
            added += 1
        else:
            skipped += 1
    return raw_count, added, skipped
