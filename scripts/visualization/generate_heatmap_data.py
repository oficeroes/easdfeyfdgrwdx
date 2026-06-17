# -*- coding: utf-8 -*-
"""生成供热点图和点位详情图使用的 JavaScript 数据。

用法：
    python scripts/visualization/generate_heatmap_data.py

输出：
    热点图展示/热点图数据.js
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TABLE_DIR = ROOT / "表格数据"
CLEAN_DIR = TABLE_DIR / "正确数据"
ABNORMAL_DIR = TABLE_DIR / "原始对比异常数据"
WEB_DIR = ROOT / "热点图展示"
OUT_FILE = WEB_DIR / "热点图数据.js"

DATASETS = {
    "2025": {
        "clean": CLEAN_DIR / "2025 團隊賽數據包_Sheet1.csv",
        "abnormal": ABNORMAL_DIR / "异常数据_2025_由原始减正确.csv",
    },
    "2026": {
        "clean": CLEAN_DIR / "副本2026 團隊賽數據包_Sheet1.csv",
        "abnormal": ABNORMAL_DIR / "异常数据_2026_由原始减正确.csv",
    },
}

CAT_LABELS = {
    "Plantae": "植物",
    "Aves": "鸟类",
    "Insecta": "昆虫",
    "Animalia": "其他动物",
    "Actinopterygii": "辐鳍鱼类",
    "Mollusca": "软体动物",
    "Reptilia": "爬行动物",
    "Fungi": "真菌",
    "Amphibia": "两栖动物",
    "Arachnida": "蛛形纲",
    "Mammalia": "哺乳动物",
    "Protozoa": "原生动物",
    "": "未分类",
}

CATEGORIES = list(CAT_LABELS.keys())
CAT_INDEX = {category: index for index, category in enumerate(CATEGORIES)}


def clean_text(value: str | None) -> str:
    return (value or "").strip()


def parse_float(row: dict[str, str], field: str) -> float:
    value = clean_text(row.get(field))
    return float(value)


def compact_record(row: dict[str, str], year: str, status: str, lat: float, lng: float, cat_index: int) -> dict[str, Any]:
    return {
        "id": clean_text(row.get("id")),
        "year": year,
        "status": status,
        "lat": round(lat, 6),
        "lng": round(lng, 6),
        "cat": cat_index,
        "observed_on": clean_text(row.get("observed_on")),
        "time_observed_at": clean_text(row.get("time_observed_at")),
        "captive_cultivated": clean_text(row.get("captive_cultivated")),
        "iconic_taxon_name": clean_text(row.get("iconic_taxon_name")),
        "taxon_kingdom_name": clean_text(row.get("taxon_kingdom_name")),
        "taxon_phylum_name": clean_text(row.get("taxon_phylum_name")),
        "taxon_class_name": clean_text(row.get("taxon_class_name")),
        "taxon_order_name": clean_text(row.get("taxon_order_name")),
        "taxon_family_name": clean_text(row.get("taxon_family_name")),
        "taxon_genus_name": clean_text(row.get("taxon_genus_name")),
        "taxon_species_name": clean_text(row.get("taxon_species_name")),
        "taxon_subspecies_name": clean_text(row.get("taxon_subspecies_name")),
    }


def load_csv(path: Path, year: str, status: str) -> tuple[list[list[float | int]], list[dict[str, Any]], Counter[str], int]:
    points: list[list[float | int]] = []
    records: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    skipped = 0

    if not path.exists():
        raise FileNotFoundError(path)

    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        required = {"id", "latitude", "longitude", "iconic_taxon_name"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} 缺少必要字段：{', '.join(sorted(missing))}")

        for row in reader:
            try:
                lat = parse_float(row, "latitude")
                lng = parse_float(row, "longitude")
            except ValueError:
                skipped += 1
                continue

            category = clean_text(row.get("iconic_taxon_name"))
            if category not in CAT_INDEX:
                category = ""
            cat_index = CAT_INDEX[category]

            points.append([round(lat, 5), round(lng, 5), cat_index])
            records.append(compact_record(row, year, status, lat, lng, cat_index))
            counts[category] += 1

    return points, records, counts, skipped


def counts_by_index(counts: Counter[str]) -> dict[int, int]:
    return {CAT_INDEX[category]: count for category, count in counts.items()}


def main() -> None:
    payload: dict[str, Any] = {
        "categories": [
            {"key": category, "label": CAT_LABELS[category], "index": index}
            for index, category in enumerate(CATEGORIES)
        ],
        "statuses": [
            {"key": "clean", "label": "正确数据"},
            {"key": "abnormal", "label": "异常数据"},
        ],
        "years": {},
    }

    for year, paths in DATASETS.items():
        year_data = {}
        for status, path in paths.items():
            points, records, counts, skipped = load_csv(path, year, status)
            year_data[status] = {
                "points": points,
                "records": records,
                "total": len(points),
                "counts": counts_by_index(counts),
            }
            message = f"{year} {status}: {len(points)} 条有效记录"
            if skipped:
                message += f"，跳过 {skipped} 条经纬度缺失或无效记录"
            print(message)
        payload["years"][year] = year_data

    WEB_DIR.mkdir(parents=True, exist_ok=True)
    js = "// 自动生成，请勿手动编辑。运行 scripts/visualization/generate_heatmap_data.py 重新生成。\n"
    js += "window.HEATMAP_DATA = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n"
    OUT_FILE.write_text(js, encoding="utf-8")

    size = OUT_FILE.stat().st_size / 1024 / 1024
    print(f"已生成 {OUT_FILE.relative_to(ROOT)} ({size:.2f} MB)")


if __name__ == "__main__":
    main()
