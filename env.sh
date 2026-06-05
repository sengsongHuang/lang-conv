#!/usr/bin/env bash
# 啟用 venv；若 shell 有 python 別名（常見於 Homebrew），先取消以免繞過 venv。
cd "$(dirname "${BASH_SOURCE[0]}")"
source .venv/bin/activate
if alias python &>/dev/null; then
  unalias python
fi
