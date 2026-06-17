# -*- coding: utf-8 -*-
"""根据“原始数据 - 正确数据”重新生成异常数据。

如果更新过 表格数据/正确数据，可以运行本脚本同步
表格数据/原始对比异常数据。

用法：
    python scripts/data_cleaning/update_abnormal_from_clean.py
"""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TABLE_DIR = ROOT / "表格数据"
CLEAN_DIR = TABLE_DIR / "正确数据"
ABNORMAL_DIR = TABLE_DIR / "原始对比异常数据"

DATASETS = [
    {
        "year": "2025",
        "source": TABLE_DIR / "2025 團隊賽數據包_Sheet1.csv",
        "clean": CLEAN_DIR / "2025 團隊賽數據包_Sheet1.csv",
        "output": ABNORMAL_DIR / "异常数据_2025_由原始减正确.csv",
    },
    {
        "year": "2026",
        "source": TABLE_DIR / "副本2026 團隊賽數據包_Sheet1.csv",
        "clean": CLEAN_DIR / "副本2026 團隊賽數據包_Sheet1.csv",
        "output": ABNORMAL_DIR / "异常数据_2026_由原始减正确.csv",
    },
]


def detect_encoding(path: Path) -> str:
    with path.open("rb") as file:
        return "utf-8-sig" if file.read(3) == b"\xef\xbb\xbf" else "utf-8"


def read_header_and_rows(path: Path) -> tuple[list[str], list[list[str]]]:
    with path.open("r", encoding=detect_encoding(path), newline="") as file:
        reader = csv.reader(file)
        try:
            header = next(reader)
        except StopIteration as exc:
            raise ValueError(f"CSV 文件为空：{path}") from exc
        return header, list(reader)


def id_index(header: list[str], path: Path) -> int:
    try:
        return header.index("id")
    except ValueError as exc:
        raise ValueError(f"CSV 文件缺少 id 列：{path}") from exc


def row_id(row: list[str], index: int) -> str:
    return row[index].strip() if index < len(row) else ""


def build_clean_id_set(clean_path: Path) -> tuple[set[str], int]:
    header, rows = read_header_and_rows(clean_path)
    index = id_index(header, clean_path)
    ids = {row_id(row, index) for row in rows if row_id(row, index)}
    return ids, len(rows)


def export_difference(dataset: dict[str, Path | str]) -> dict[str, object]:
    source_path = Path(dataset["source"])
    clean_path = Path(dataset["clean"])
    output_path = Path(dataset["output"])

    source_header, source_rows = read_header_and_rows(source_path)
    source_id_index = id_index(source_header, source_path)
    clean_ids, clean_rows_count = build_clean_id_set(clean_path)

    abnormal_rows: list[list[str]] = []
    duplicate_source_ids = 0
    seen_source_ids: set[str] = set()

    for row in source_rows:
        current_id = row_id(row, source_id_index)
        if current_id in seen_source_ids:
            duplicate_source_ids += 1
        if current_id:
            seen_source_ids.add(current_id)
        if current_id not in clean_ids:
            abnormal_rows.append(row)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(source_header)
        writer.writerows(abnormal_rows)

    expected_abnormal_rows = len(source_rows) - clean_rows_count
    return {
        "year": dataset["year"],
        "source_file": str(source_path.relative_to(ROOT)),
        "clean_file": str(clean_path.relative_to(ROOT)),
        "output_file": str(output_path.relative_to(ROOT)),
        "source_rows": len(source_rows),
        "clean_rows": clean_rows_count,
        "abnormal_rows": len(abnormal_rows),
        "expected_abnormal_rows": expected_abnormal_rows,
        "matches_expected_count": len(abnormal_rows) == expected_abnormal_rows,
        "source_unique_ids": len(seen_source_ids),
        "clean_unique_ids": len(clean_ids),
        "duplicate_source_ids": duplicate_source_ids,
    }


def main() -> None:
    report: dict[str, object] = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "rule": "按 id 对比：异常数据 = 原始表格数据中存在、正确数据中不存在的整行记录。",
        "output_dir": str(ABNORMAL_DIR.relative_to(ROOT)),
        "datasets": [],
    }

    for dataset in DATASETS:
        report["datasets"].append(export_difference(dataset))

    report_path = ABNORMAL_DIR / "原始对比异常数据报告.json"
    with report_path.open("w", encoding="utf-8", newline="") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
