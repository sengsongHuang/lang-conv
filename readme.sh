#!/bin/sh
# lang-conv 指令速查

cat <<'EOF'
lang-conv 指令速查
==================

詳細流程與使用場景請見 README.md

──────────────────────────────────────────────────────────────

init_vocab_db.py
  建立 / 更新 working/vocab.sqlite 三語言表
  Usage python3 init_vocab_db.py [vocab.sqlite]

import_vocab.py
  從 txt 匯入單字（每行一詞）至 vocab.sqlite
  Usage python3 import_vocab.py -l en -f words.txt -s "書名"
        -l   語言：en / fr / de
        -f   輸入 txt
        -s   source（來源書名）
        --vocab-db  預設 working/vocab.sqlite

kobo_highlights.py
  從 Kobo 劃線匯入單字（互動：選書 → 章節 → 語言）
  Usage python3 kobo_highlights.py [KoboReader.sqlite]
        --export-only     只印劃線，不寫 vocab
        --vocab-db PATH   預設 working/vocab.sqlite

fill_vocab.py
  用 Ollama 逐字補齊 中文解釋 與 字卡（需 Ollama server）
  Usage python3 fill_vocab.py -l en [-n N] [--model qwen3:8b]
        -l   語言：en / fr / de
        -n   最多製作 N 筆（已補齊的不計）
        --vocab-db PATH

dump_vocab.py
  從 vocab.sqlite 匯出 CSV / 字卡，或查詢單字
  Usage python3 dump_vocab.py -l en --csv [-o out.csv]
        python3 dump_vocab.py -l en --flashcard [-o out.md]
        python3 dump_vocab.py -l en --check WORD
        --start N   從 serial_no >= N
        --count N   最多 N 筆

env.sh
  啟用 .venv（並取消 python 別名）
  Usage source env.sh

EOF
