# lang-conv

Kobo 劃線 → `vocab.sqlite` → Ollama 補中文解釋與字卡。

## 工作流程

0. 建立虛擬環境並安裝依賴（首次）：

```bash
python3 -m venv .venv
source env.sh          # 啟用 venv（會取消 python 別名，避免繞過 .venv）
pip install -r requirements.txt
```

之後每次開新 terminal：`source env.sh`

若不用 `env.sh`，請改用 **`python3`**（不要用 `python`；若 shell 有 `python` 別名指向 Homebrew，activate 後仍會找不到 `ollama`）。

1. 手動複製 Kobo 裝置上的 `KoboReader.sqlite` 到 `working/`
2. 執行 `init_vocab_db.py` 建立 `working/vocab.sqlite`（若尚未建立）
3. 執行 `kobo_highlights.py`：選書 → 章節 → 語言 → 匯入單字
4. 執行 `fill_vocab.py`：依語言逐字產生 `中文解釋` 與 `字卡`

## working/ 目錄

| 檔案 | 用途 |
|------|------|
| `KoboReader.sqlite` | Kobo 劃線來源（需手動從裝置複製） |
| `vocab.sqlite` | 單字庫（程式建立與寫入） |

程式不會自動連接 Kobo 裝置；使用前請先更新 `working/KoboReader.sqlite`。

## vocab.sqlite 結構

三張表結構相同：

| 欄位 | 說明 |
|------|------|
| `serial_no` | 自動遞增序號（各表獨立） |
| `單字` | 該語言單字（同表內大小寫視為同一字，不可重複） |
| `中文解釋` | 依 CSV 模板格式（`fill_vocab.py` 填入） |
| `字卡` | 依 Markdown 模板格式（`fill_vocab.py` 填入） |

| 語言 | 表名 |
|------|------|
| `en` | `english_vocab` |
| `fr` | `french_vocab` |
| `de` | `germany_vocab` |

## init_vocab_db.py

建立或初始化 `working/vocab.sqlite` 三表（可重複執行）：

```bash
python3 init_vocab_db.py
python3 init_vocab_db.py working/vocab.sqlite
```

## kobo_highlights.py

從 Kobo 劃線匯入單字至 `vocab.sqlite`（預設行為，不呼叫 Ollama）。

```bash
python3 kobo_highlights.py
python3 kobo_highlights.py working/KoboReader.sqlite
python3 kobo_highlights.py --vocab-db working/vocab.sqlite
python3 kobo_highlights.py --export-only   # 只印 stdout，不寫 vocab
```

互動流程：

1. 選書
2. 選章節（數字選單章；`all` / `全部` / `a` / 直接 Enter 選全部）
3. 選語言（`en` / `fr` / `de`）
4. 顯示匯入摘要

選 `[all] 全部` 時，單字依章節順序匯入；同一章節內依劃線時間與位置排序。匯入前會對劃線清單去重（大小寫不敏感、保留首次出現）。

## fill_vocab.py

讀取尚未補齊的單字，逐字呼叫 Ollama 產生 `中文解釋` 與 `字卡`。

```bash
python3 fill_vocab.py -l en
python3 fill_vocab.py -l en -n 5          # 最多製作 5 筆後停止
python3 fill_vocab.py -l fr --model qwen3:8b
python3 fill_vocab.py -l de --vocab-db working/vocab.sqlite
```

需求：

- Python 3
- 虛擬環境 + `pip install -r requirements.txt`（Python `ollama` 套件）
- 已安裝並啟動 Ollama（本機 server，預設 `localhost:11434`）
- 預設模型：`qwen3:8b`（`ollama pull qwen3:8b`；可在 `vocab_generate.py` 修改 `OLLAMA_MODEL` 常數）

待處理條件：`中文解釋` 或 `字卡` 為空；兩欄皆已補齊的單字會跳過。

## 模板

- 字卡：`templates/de_md.md`、`templates/fr_md.md`、`templates/en_md.md`
- CSV：`templates/de_csv.md`、`templates/fr_csv.md`、`templates/en_csv.md`

## old/

`old/` 目錄為封存舊腳本（`make_flashcard.py`、`make_vocab_csv.py`、`dedupe_words.py`），不再維護，僅供參考。
