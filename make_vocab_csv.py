import argparse
import sys
import time
from pathlib import Path
from typing import Optional

import ollama


SEPARATOR = "\t"

LANGUAGE_TO_TEMPLATE = {
    "de": "de_csv.md",
    "fr": "fr_csv.md",
    "en": "en_csv.md",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Batch generate vocabulary CSV lines via local Ollama."
    )
    parser.add_argument(
        "-l",
        "--language",
        required=True,
        choices=sorted(LANGUAGE_TO_TEMPLATE.keys()),
        help="Language id: de, fr, en",
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Input filename (one word per line).",
    )
    parser.add_argument(
        "-o",
        "--output",
        help=(
            "Output filename (append mode). "
            "If omitted, use input filename with .csv extension in same directory."
        ),
    )
    parser.add_argument(
        "--model",
        default="qwen3:8b",
        help="Ollama model name. Default: qwen3:8b",
    )
    return parser.parse_args()


def load_template(language_id: str) -> str:
    template_path = Path(__file__).parent / "templates" / LANGUAGE_TO_TEMPLATE[language_id]
    return template_path.read_text(encoding="utf-8")


def load_words(input_path: Path) -> tuple[list[str], int]:
    words: list[str] = []
    seen: set[str] = set()
    total_read = 0
    for line in input_path.read_text(encoding="utf-8").splitlines():
        word = line.strip()
        if not word:
            continue
        total_read += 1
        if word not in seen:
            words.append(word)
            seen.add(word)
    return words, total_read


def resolve_output_path(input_path: Path, output_arg: Optional[str]) -> Path:
    if output_arg:
        return Path(output_arg)

    if input_path.suffix.lower() == ".csv":
        raise ValueError(
            "當省略 -o 時，輸入檔不能是 .csv；請手動指定 -o 避免與輸入檔同名。"
        )
    return input_path.with_suffix(".csv")


def render_prompt(template_text: str, word: str, separator: str) -> str:
    return template_text.replace("{{word}}", word).replace("{{separator}}", separator)


def format_elapsed(seconds: float) -> str:
    total = int(seconds)
    minutes = total // 60
    remain_seconds = total % 60
    return f"{minutes}m{remain_seconds:02d}s"


def generate_csv_lines(model: str, prompt: str) -> str:
    response = ollama.chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You generate compact Chinese translations for vocabulary CSV rows. "
                    "Output only CSV lines."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    )
    return response["message"]["content"].strip()


def normalize_csv_lines(language: str, word: str, raw: str, separator: str) -> list[str]:
    text = raw.replace("```csv", "").replace("```", "").strip()
    raw_rows = [line.strip() for line in text.splitlines() if line.strip()]
    rows: list[str] = []
    for line in raw_rows:
        cleaned = line.lstrip("-*0123456789. ").strip()
        if separator not in cleaned:
            continue
        left, right = cleaned.split(separator, 1)
        left = left.strip().strip('"')
        right = right.strip().strip('"')
        if left and right:
            rows.append(f"{left}{separator}{right}")

    if not rows:
        fallback_meaning = text.splitlines()[0].strip() if text else ""
        rows = [f"{word}{separator}{fallback_meaning}"]

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


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)

    if not input_path.exists():
        print(f"input file not found: {input_path}", file=sys.stderr)
        return 1

    try:
        output_path = resolve_output_path(input_path, args.output)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    words, total_read = load_words(input_path)
    if not words:
        print("input file has no words to process.", file=sys.stderr)
        return 1

    if total_read > len(words):
        print(f"共讀取 {total_read} 筆，去重後 {len(words)} 筆")
    else:
        print(f"共讀取 {total_read} 筆")

    template_text = load_template(args.language)
    total = len(words)
    start_time = time.time()
    failures: list[tuple[int, str, str]] = []

    with output_path.open("a", encoding="utf-8") as output:
        for index, word in enumerate(words, start=1):
            elapsed = format_elapsed(time.time() - start_time)
            print(f"正在產生 {index}/{total} 個單字，已花費 {elapsed}", flush=True)
            try:
                prompt = render_prompt(template_text, word, SEPARATOR)
                raw = generate_csv_lines(args.model, prompt)
                rows = normalize_csv_lines(args.language, word, raw, SEPARATOR)
                output.write("\n".join(rows) + "\n")
                output.flush()
            except Exception as exc:  # noqa: BLE001
                failures.append((index, word, str(exc)))
                print(f"生成失敗 #{index:03d} {word}: {exc}", file=sys.stderr, flush=True)

    if failures:
        print("\n以下單字生成失敗：", file=sys.stderr)
        for index, word, err in failures:
            print(f"- #{index:03d} {word}: {err}", file=sys.stderr)
        return 2

    print(f"完成，共 {total} 個單字。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
