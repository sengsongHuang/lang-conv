import sqlite3
import time
from pathlib import Path
from typing import Optional

import ollama

OLLAMA_MODEL = "qwen3:8b"

SEPARATOR = "\t"

CSV_TEMPLATES = {
    "de": "de_csv.md",
    "fr": "fr_csv.md",
    "en": "en_csv.md",
}

MD_TEMPLATES = {
    "de": "de_md.md",
    "fr": "fr_md.md",
    "en": "en_md.md",
}


def load_template(filename: str) -> str:
    template_path = Path(__file__).parent / "templates" / filename
    return template_path.read_text(encoding="utf-8")


def render_csv_prompt(language: str, word: str) -> str:
    template = load_template(CSV_TEMPLATES[language])
    return template.replace("{{word}}", word).replace("{{separator}}", SEPARATOR)


def render_md_prompt(language: str, word: str, index: int) -> str:
    template = load_template(MD_TEMPLATES[language])
    return template.replace("{{word}}", word).replace("{{index}}", f"{index:03d}")


def call_ollama(model: str, system: str, prompt: str) -> str:
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    )
    return response["message"]["content"].strip()


def generate_csv_raw(model: str, language: str, word: str) -> str:
    prompt = render_csv_prompt(language, word)
    return call_ollama(
        model,
        "You generate compact Traditional Chinese translations for vocabulary CSV rows. "
        "Output only CSV lines.",
        prompt,
    )


def generate_flashcard_raw(model: str, language: str, word: str, serial_no: int) -> str:
    prompt = render_md_prompt(language, word, serial_no)
    return call_ollama(
        model,
        "You generate high-quality vocabulary flashcards in Traditional Chinese. "
        "Output only the requested markdown card.",
        prompt,
    )


def normalize_csv_lines(language: str, word: str, raw: str) -> list[str]:
    text = raw.replace("```csv", "").replace("```", "").strip()
    raw_rows = [line.strip() for line in text.splitlines() if line.strip()]
    rows: list[str] = []
    for line in raw_rows:
        cleaned = line.lstrip("-*0123456789. ").strip()
        if SEPARATOR not in cleaned:
            continue
        left, right = cleaned.split(SEPARATOR, 1)
        left = left.strip().strip('"')
        right = right.strip().strip('"')
        if left and right:
            rows.append(f"{left}{SEPARATOR}{right}")

    if not rows:
        fallback = text.splitlines()[0].strip() if text else ""
        rows = [f"{word}{SEPARATOR}{fallback}"]

    if language in {"en", "fr"}:
        return [rows[0]]

    single_rows = [row for row in rows if "單數" in row]
    plural_rows = [row for row in rows if "複數" in row]
    if single_rows or plural_rows:
        ordered: list[str] = []
        if single_rows:
            ordered.append(single_rows[0])
        if plural_rows:
            ordered.append(plural_rows[0])
        return ordered

    return [rows[0]]


def extract_zh_meaning(language: str, word: str, raw: str) -> str:
    rows = normalize_csv_lines(language, word, raw)
    meanings: list[str] = []
    for row in rows:
        _, right = row.split(SEPARATOR, 1)
        meanings.append(right.strip())
    return "\n".join(meanings)


def format_duration(seconds: float) -> str:
    if seconds >= 60:
        minutes = int(seconds // 60)
        remain = seconds - minutes * 60
        return f"{minutes}m{remain:.1f}s"
    return f"{seconds:.1f}s"


def fill_pending_words(
    conn: sqlite3.Connection,
    language: str,
    model: str,
    limit: Optional[int] = None,
) -> int:
    from vocab_db import fetch_pending_words, update_word_content

    pending = fetch_pending_words(conn, language)
    total = len(pending)
    if total == 0:
        print("沒有待補單字。")
        return 0

    filled = 0
    cumulative = 0.0
    for idx, row in enumerate(pending, start=1):
        if limit is not None and filled >= limit:
            break

        word = row["單字"]
        serial_no = row["serial_no"]
        print(f"正在產生 {word} [{idx}/{total}] ...")

        start = time.perf_counter()
        csv_raw = generate_csv_raw(model, language, word)
        zh_meaning = extract_zh_meaning(language, word, csv_raw)
        flashcard = generate_flashcard_raw(model, language, word, serial_no)
        elapsed = time.perf_counter() - start
        cumulative += elapsed

        update_word_content(conn, language, serial_no, zh_meaning, flashcard)
        filled += 1
        print(
            f"已完成 {word} [{idx}/{total}]，本次 {format_duration(elapsed)}，"
            f"累計 {format_duration(cumulative)}"
        )

    if limit is not None and filled >= limit and idx < total:
        print(f"已製作 {filled} 筆，達上限 {limit}，停止。")

    return filled
