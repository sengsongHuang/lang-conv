# lang-conv

Kobo 劃線 → `vocab.sqlite` → Ollama 補中文解釋與字卡。

指令速查：`sh readme.sh`

## 工作流程

0. 建立虛擬環境並安裝依賴（首次）：

```bash
python3 -m venv .venv
source env.sh          # 啟用 venv（會取消 python 別名，避免繞過 .venv）
pip install -r requirements.txt
python3 init_vocab_db.py
```

之後每次開新 terminal：`source env.sh`

若不用 `env.sh`，請改用 **`python3`**（不要用 `python`；若 shell 有 `python` 別名指向 Homebrew，activate 後仍會找不到 `ollama`）。

## 使用場景

### 更新 Kobo 劃線單字到 vocab.sqlite

1. 插上 Kobo 裝置，複製資料庫：

```bash
cp <KOBO_DEVICE_PATH>/.kobo/KoboReader.sqlite working/
```

2. 互動匯入：

```bash
python3 kobo_highlights.py
```

### 從文字檔匯入單字到 vocab.sqlite

```bash
python3 import_vocab.py -l en -f words.txt -s "書名"
```

### 用 Ollama 補齊中文解釋與字卡

```bash
python3 fill_vocab.py -l en
python3 fill_vocab.py -l en -n 5   # 最多 5 筆
```

需已安裝並啟動 Ollama（`ollama pull qwen3:8b`）。

### 匯出字卡或 CSV

```bash
python3 dump_vocab.py -l en --flashcard -o cards.md
python3 dump_vocab.py -l en --csv -o words.csv
python3 dump_vocab.py -l en --check scrawny
```

### 用字卡學習（Calibre → Books / Kobo）

1. Calibre 新增一本書，將 `cards.md` 拖曳進去
2. 編輯詮釋資料（書名、作者方便日後歸類），設計封面
3. **iPhone / iPad（Apple Books）**
   - 輸出 EPUB
   - AirDrop 或雲端分享到手機，用 Books 開啟即可匯入
4. **Kobo 閱讀器**
   - 輸出 KEPUB
   - Kobo USB 連接電腦，選「連接電腦」
   - Calibre 對該書「傳輸書籍至裝置」，只勾選 KEPUB

### 用 CSV 匯入 Quizlet

1. 到 [Quizlet](https://quizlet.com) 新增學習集
2. 選 CSV 匯入，分隔字元選 **Tab**
3. 貼上 `dump_vocab.py --csv` 產出的內容
4. 確認輸入／輸出語言是否正確

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
| `source` | 來源（Kobo 匯入時為書名） |
| `create_at` | 加入時間（Unix timestamp，INTEGER；可排序、可比較） |

| 語言 | 表名 |
|------|------|
| `en` | `english_vocab` |
| `fr` | `french_vocab` |
| `de` | `germany_vocab` |

`create_at` 查詢範例（sqlite3）：

```sql
-- 三個月內
SELECT serial_no, 單字, datetime(create_at, 'unixepoch', 'localtime')
FROM english_vocab
WHERE create_at >= strftime('%s', 'now', '-3 months')
ORDER BY create_at DESC;

-- 上個月（整個曆月）
SELECT serial_no, 單字, datetime(create_at, 'unixepoch', 'localtime')
FROM english_vocab
WHERE create_at >= strftime('%s', 'now', 'start of month', '-1 month')
  AND create_at < strftime('%s', 'now', 'start of month');
```

## init_vocab_db.py

建立或初始化 `working/vocab.sqlite` 三表（可重複執行）：

```bash
python3 init_vocab_db.py
python3 init_vocab_db.py working/vocab.sqlite
```

## import_vocab.py

從 txt 匯入單字（每行一詞）：

```bash
python3 import_vocab.py -l en -f words.txt -s "Percy Jackson and the Lightning Thief (Book 1)"
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

## dump_vocab.py

從 `vocab.sqlite` 匯出 CSV、字卡，或查詢單字：

```bash
python3 dump_vocab.py -l en --csv [-o out.csv]
python3 dump_vocab.py -l en --flashcard [-o out.md]
python3 dump_vocab.py -l en --check WORD
python3 dump_vocab.py -l en --flashcard --start 10 --count 5
```

## 模板

- 字卡：`templates/de_md.md`、`templates/fr_md.md`、`templates/en_md.md`
- CSV：`templates/de_csv.md`、`templates/fr_csv.md`、`templates/en_csv.md`

## old/

`old/` 目錄為封存舊腳本（`make_flashcard.py`、`make_vocab_csv.py`、`dedupe_words.py`），不再維護，僅供參考。
