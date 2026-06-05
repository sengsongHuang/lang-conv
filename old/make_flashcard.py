import argparse
import sys
import time
from pathlib import Path
from typing import Optional

import ollama


LANGUAGE_TO_TEMPLATE = {
    "de": "de_md.md",
    "fr": "fr_md.md",
    "en": "en_md.md",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Batch generate flashcards via local Ollama."
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
            "If omitted, use input filename with .md extension in same directory."
        ),
    )
    parser.add_argument(
        "--model",
        default="qwen3:8b",
        help="Ollama model name. Default: qwen3:8b",
    )
    parser.add_argument(
        "--start-index",
        type=int,
        default=1,
        help="Card start index. Default: 1",
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


def render_prompt(template_text: str, word: str, index: int) -> str:
    return template_text.replace("{{word}}", word).replace("{{index}}", f"{index:03d}")


def resolve_output_path(input_path: Path, output_arg: Optional[str]) -> Path:
    if output_arg:
        return Path(output_arg)

    if input_path.suffix.lower() == ".md":
        raise ValueError(
            "當省略 -o 時，輸入檔不能是 .md；請手動指定 -o 避免與輸入檔同名。"
        )

    return input_path.with_suffix(".md")


def format_elapsed(seconds: float) -> str:
    total = int(seconds)
    minutes = total // 60
    remain_seconds = total % 60
    return f"{minutes}m{remain_seconds:02d}s"


def generate_flashcard(model: str, prompt: str) -> str:
    response = ollama.chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You generate high-quality vocabulary flashcards in Traditional Chinese. "
                    "Output only the requested markdown card."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    )
    return response["message"]["content"].strip()


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

    output_has_existing_content = (
        output_path.exists() and output_path.read_text(encoding="utf-8").strip() != ""
    )
    wrote_any_card = False

    with output_path.open("a", encoding="utf-8") as output:
        for index, word in enumerate(words, start=args.start_index):
            processed = index - args.start_index + 1
            elapsed = format_elapsed(time.time() - start_time)
            print(f"正在產生 {processed}/{total} 個單字，已花費 {elapsed}", flush=True)
            try:
                prompt = render_prompt(template_text, word, index)
                card = generate_flashcard(args.model, prompt)
                if output_has_existing_content or wrote_any_card:
                    output.write("\n---\n\n")
                output.write(card.rstrip() + "\n")
                wrote_any_card = True
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