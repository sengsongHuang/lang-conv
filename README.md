# lang-conv

這個專案提供三個工具：

- [`make_flashcard.py`](#1-make_flashcardpy)：把單字清單轉成 Markdown 單字卡
- [`make_vocab_csv.py`](#2-make_vocab_csvpy)：把單字清單轉成 CSV（單字 + 繁體中文解釋）
- [`dedupe_words.py`](#3-dedupe_wordspy)：清理 txt 重複詞（保留首次出現，順序不變）

## 需求

- Python 3
- 已安裝並啟動 Ollama
- 可用模型（預設 `qwen3:8b`）

## 輸入格式

兩個程式都使用同一種輸入：

- `txt` 檔
- 每行一個單字或片語
- 空行會忽略
- 重複詞只保留第一次出現

## 1) make_flashcard.py

用途：依語言模板產生單字卡（`de/fr/en`）。

### 指令

```bash
python3 make_flashcard.py -l <de|fr|en> -i <input.txt> [-o output.md] [--model qwen3:8b] [--start-index 1]
```

### 參數

- `-l`：語言代碼（`de`、`fr`、`en`）
- `-i`：輸入 txt 檔
- `-o`：輸出 md 檔（可省略）
- `--model`：Ollama 模型名稱
- `--start-index`：卡片編號起始值

### 輸出規則

- 若省略 `-o`，會輸出到「同目錄同檔名但副檔名 `.md`」
- 若省略 `-o` 且輸入已是 `.md`，程式會報錯（避免同檔覆寫）
- 卡片之間使用 `---` 分隔
- 進度列印範例：`正在產生 7/103 個單字，已花費 2m18s`

## 2) make_vocab_csv.py

用途：依語言模板產生 CSV 行（預設分隔字元為 tab）。

### 指令

```bash
python3 make_vocab_csv.py -l <de|fr|en> -i <input.txt> [-o output.csv] [--model qwen3:8b]
```

### 參數

- `-l`：語言代碼（`de`、`fr`、`en`）
- `-i`：輸入 txt 檔
- `-o`：輸出 csv 檔（可省略）
- `--model`：Ollama 模型名稱

### 輸出規則

- 若省略 `-o`，會輸出到「同目錄同檔名但副檔名 `.csv`」
- 若省略 `-o` 且輸入已是 `.csv`，程式會報錯（避免同檔覆寫）
- 程式內分隔字元常數在檔案前段：`SEPARATOR = "\t"`
- 中文解釋要求為繁體中文
- 德文名詞可輸出單複數兩行（依模板規則）
- 法文、英文預設單行輸出

## 範例

```bash
# 產生德文單字卡
python3 make_flashcard.py -l de -i samples/words_de.txt -o samples/cards_de.md

# 產生德文 CSV
python3 make_vocab_csv.py -l de -i samples/words_de.txt -o samples/vocab_de.csv

# 清理重複詞（直接覆寫原檔，並備份成 .old）
python3 dedupe_words.py samples/words_de.txt
```

## 3) dedupe_words.py

用途：移除輸入 txt 的重複詞，只保留第一個出現，順序不變。

### 指令

```bash
python3 dedupe_words.py <text_file_name>
```

### 行為

- 每行視為一筆資料（空白行忽略）
- 大小寫視為同一字（例如 `Apple` 與 `apple` 視為重複）
- 若有重複：
  - 備份原檔為同名 `.old`（例如 `words.txt.old`）
  - 覆寫原檔為去重後內容
  - 顯示：`已讀取 n 筆資料，已刪除 m 筆重複資料，已儲存 k 筆資料`
- 若沒有重複：
  - 不改檔案
  - 顯示：`已讀取 n 筆資料，沒有重複`

## 模板位置

- 單字卡模板：`templates/de_md.md`、`templates/fr_md.md`、`templates/en_md.md`
- CSV 模板：`templates/de_csv.md`、`templates/fr_csv.md`、`templates/en_csv.md`
