#!/usr/bin/env python3
import sys
from pathlib import Path

from vocab_db import DEFAULT_VOCAB_DB, connect_vocab_db, ensure_schema


def main() -> int:
    db_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_VOCAB_DB
    conn = connect_vocab_db(db_path)
    ensure_schema(conn)
    conn.close()
    print(f"已初始化：{db_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
