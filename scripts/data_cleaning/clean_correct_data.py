# -*- coding: utf-8 -*-
"""根据坐标异常清单生成“正确数据”。

用法：
    python scripts/data_cleaning/clean_correct_data.py

输入：
    表格数据/*.csv
    异常数据/坐标异常数据_*.csv

输出：
    表格数据/正确数据/*.csv
    表格数据/正确数据/清理报告.json
"""

from __future__ import annotations

import csv
import json
import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TABLE_DIR = ROOT / "表格数据"
ANOMALY_DIR = ROOT / "异常数据"
OUTPUT_DIR = TABLE_DIR / "正确数据"

DATASETS = [
    {
        "year": "2025",
        "source": TABLE_DIR / "2025 團隊賽數據包_Sheet1.csv",
        "anomaly": ANOMALY_DIR / "坐标异常数据_2025.csv",
        "anomaly_detail": ANOMALY_DIR / "坐标异常数据_2025_详细版.csv",
    },
    {
        "year": "2026",
        "source": TABLE_DIR / "副本2026 團隊賽數據包_Sheet1.csv",
        "anomaly": ANOMALY_DIR / "坐标异常数据_2026.csv",
        "anomaly_detail": ANOMALY_DIR / "坐标异常数据_2026_详细版.csv",
    },
]


def detect_encoding(path: Path) -> str:
    with path.open("rb") as file:
        return "utf-8-sig" if file.read(3) == b"\xef\xbb\xbf" else "utf-8"


def load_anomaly_ids(path: Path) -> tuple[set[str], int]:
    anomaly_ids: set[str] = set()
    total_rows = 0
    with path.open("r", encoding=detect_encoding(path), newline="") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames or "id" not in reader.fieldnames:
            raise ValueError(f"异常文件缺少 id 列：{path}")
        for row in reader:
            total_rows += 1
            record_id = (row.get("id") or "").strip()
            if record_id:
                anomaly_ids.add(record_id)
    return anomaly_ids, total_rows


def remove_anomalies_from_copy(source: Path, target: Path, anomaly_ids: set[str]) -> dict[str, int | str]:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)

    encoding = detect_encoding(target)
    temp_target = target.with_suffix(target.suffix + ".tmp")
    total_rows = 0
    removed_rows = 0
    remaining_anomaly_rows = 0

    with target.open("r", encoding=encoding, newline="") as input_file, temp_target.open(
        "w", encoding=encoding, newline=""
    ) as output_file:
        reader = csv.reader(input_file)
        writer = csv.writer(output_file)

        try:
            header = next(reader)
        except StopIteration as exc:
            raise ValueError(f"源文件为空：{source}") from exc

        if "id" not in header:
            raise ValueError(f"源文件缺少 id 列：{source}")

        id_index = header.index("id")
        writer.writerow(header)

        for row in reader:
            total_rows += 1
            record_id = row[id_index].strip() if id_index < len(row) else ""
            if record_id in anomaly_ids:
                removed_rows += 1
                continue
            writer.writerow(row)

    temp_target.replace(target)

    with target.open("r", encoding=detect_encoding(target), newline="") as file:
        reader = csv.reader(file)
        header = next(reader)
        id_index = header.index("id")
        for row in reader:
            record_id = row[id_index].strip() if id_index < len(row) else ""
            if record_id in anomaly_ids:
                remaining_anomaly_rows += 1

    return {
        "source_file": str(source.relative_to(ROOT)),
        "output_file": str(target.relative_to(ROOT)),
        "source_rows": total_rows,
        "removed_rows": removed_rows,
        "output_rows": total_rows - removed_rows,
        "remaining_anomaly_rows": remaining_anomaly_rows,
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    report: dict[str, object] = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "rule": "按异常数据 CSV 中的 id 删除原始表格的对应整行，原始表格数据不修改。",
        "output_dir": str(OUTPUT_DIR.relative_to(ROOT)),
        "datasets": [],
    }

    for dataset in DATASETS:
        anomaly_ids, anomaly_rows = load_anomaly_ids(dataset["anomaly"])
        detail_ids, detail_rows = load_anomaly_ids(dataset["anomaly_detail"])
        target = OUTPUT_DIR / dataset["source"].name
        result = remove_anomalies_from_copy(dataset["source"], target, anomaly_ids)
        unmatched_ids = len(anomaly_ids) - int(result["removed_rows"])

        report["datasets"].append(
            {
                "year": dataset["year"],
                "anomaly_file": str(dataset["anomaly"].relative_to(ROOT)),
                "anomaly_rows": anomaly_rows,
                "unique_anomaly_ids": len(anomaly_ids),
                "detail_file": str(dataset["anomaly_detail"].relative_to(ROOT)),
                "detail_rows": detail_rows,
                "detail_ids_match_simple_file": anomaly_ids == detail_ids,
                "unmatched_anomaly_ids": max(unmatched_ids, 0),
                **result,
            }
        )

    report_path = OUTPUT_DIR / "清理报告.json"
    with report_path.open("w", encoding="utf-8", newline="") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
