import shutil
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("用法：python3 dedupe_words.py <text_file_name>", file=sys.stderr)
        return 1

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"找不到檔案：{file_path}", file=sys.stderr)
        return 1
    if not file_path.is_file():
        print(f"不是一般檔案：{file_path}", file=sys.stderr)
        return 1

    lines = file_path.read_text(encoding="utf-8").splitlines()
    seen: set[str] = set()
    kept: list[str] = []

    for line in lines:
        word = line.strip()
        if not word:
            continue
        normalized = word.casefold()
        if normalized not in seen:
            seen.add(normalized)
            kept.append(word)

    total = len([line for line in lines if line.strip()])
    deleted = total - len(kept)

    if deleted == 0:
        print(f"已讀取 {total} 筆資料，沒有重複")
        return 0

    backup_path = file_path.with_suffix(file_path.suffix + ".old")
    shutil.copy2(file_path, backup_path)

    file_path.write_text("\n".join(kept) + "\n", encoding="utf-8")
    print(f"已讀取 {total} 筆資料，已刪除 {deleted} 筆重複資料，已儲存 {len(kept)} 筆資料")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
