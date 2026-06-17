# -*- coding: utf-8 -*-
"""验证报告中使用的核心统计数值是否与正确数据一致。

用法：
    python scripts/validation/verify_reports.py

输出：
    报告文档/数值验证报告.json
"""

from __future__ import annotations

import csv
import json
import math
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CLEAN_DIR = ROOT / "表格数据" / "正确数据"
REPORT_DIR = ROOT / "报告文档"

DATA_FILES = {
    "2025": CLEAN_DIR / "2025 團隊賽數據包_Sheet1.csv",
    "2026": CLEAN_DIR / "副本2026 團隊賽數據包_Sheet1.csv",
}

EXPECTED = {
    "2025": {
        "records": 33486,
        "species": 2979,
        "families": 605,
        "genera": 1869,
        "shannon": 6.7060,
        "simpson_d": 0.002623,
        "pielou": 0.8383,
    },
    "2026": {
        "records": 18367,
        "species": 2009,
        "families": 517,
        "genera": 1473,
        "shannon": 6.4099,
        "simpson_d": 0.004212,
        "pielou": 0.8428,
    },
}

EXPECTED_2026_TAXON_COUNTS = {
    "Plantae": 9736,
    "Insecta": 3673,
    "Aves": 3007,
    "Animalia": 536,
    "Amphibia": 303,
    "Mollusca": 273,
    "Reptilia": 239,
    "Arachnida": 212,
    "Actinopterygii": 177,
    "Fungi": 152,
    "Mammalia": 54,
    "Protozoa": 4,
}

EXPECTED_TOP20_2026 = [
    ("Spilopelia chinensis", 484),
    ("Passer montanus", 435),
    ("Oxalis debilis", 324),
    ("Pycnonotus jocosus", 246),
    ("Copsychus saularis", 236),
    ("Trigoniulus corallinus", 230),
    ("Pycnonotus sinensis", 198),
    ("Sphagneticola trilobata", 183),
    ("Acridotheres cristatellus", 162),
    ("Egretta garzetta", 162),
    ("Helicorthomorpha holstii", 161),
    ("Ficus microcarpa", 149),
    ("Duttaphrynus melanostictus", 142),
    ("Apis cerana", 137),
    ("Pilea microphylla", 137),
    ("Gallinula chloropus", 135),
    ("Hyophila involuta", 133),
    ("Gracupica nigricollis", 127),
    ("Oxalis corniculata", 112),
    ("Columba livia", 108),
]


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def unique_values(rows: list[dict[str, str]], field: str) -> set[str]:
    return {row.get(field, "").strip() for row in rows if row.get(field, "").strip()}


def count_by_field(rows: list[dict[str, str]], field: str) -> Counter[str]:
    return Counter(row.get(field, "").strip() for row in rows if row.get(field, "").strip())


def species_frequency(rows: list[dict[str, str]]) -> Counter[str]:
    return count_by_field(rows, "taxon_species_name")


def shannon_index(species_counts: Counter[str], total: int) -> float:
    value = 0.0
    for count in species_counts.values():
        if count > 0:
            p = count / total
            value -= p * math.log(p)
    return value


def simpson_index(species_counts: Counter[str], total: int) -> float:
    if total <= 1:
        return 1.0
    return sum(count * (count - 1) for count in species_counts.values()) / (total * (total - 1))


def pielou_evenness(shannon: float, species_count: int) -> float:
    if species_count <= 1:
        return 1.0
    return shannon / math.log(species_count)


def check(results: list[dict[str, Any]], name: str, expected: Any, actual: Any, tolerance: float = 0.0) -> None:
    if isinstance(expected, float) or tolerance:
        passed = abs(float(expected) - float(actual)) <= tolerance
    else:
        passed = expected == actual
    results.append(
        {
            "name": name,
            "expected": expected,
            "actual": actual,
            "tolerance": tolerance,
            "passed": passed,
        }
    )
    status = "通过" if passed else "未通过"
    print(f"{status} - {name}: expected={expected}, actual={actual}")


def summarize_year(year: str, rows: list[dict[str, str]]) -> dict[str, Any]:
    species_counts = species_frequency(rows)
    total = len(rows)
    species_count = len(species_counts)
    shannon = shannon_index(species_counts, total)
    simpson_d = simpson_index(species_counts, total)
    return {
        "records": total,
        "species": species_count,
        "families": len(unique_values(rows, "taxon_family_name")),
        "genera": len(unique_values(rows, "taxon_genus_name")),
        "shannon": shannon,
        "simpson_d": simpson_d,
        "simpson_1_minus_d": 1 - simpson_d,
        "inverse_simpson": 1 / simpson_d if simpson_d else None,
        "pielou": pielou_evenness(shannon, species_count),
        "taxon_counts": dict(count_by_field(rows, "iconic_taxon_name")),
        "species_counts": species_counts,
    }


def main() -> None:
    rows_by_year = {year: load_csv(path) for year, path in DATA_FILES.items()}
    summaries = {year: summarize_year(year, rows) for year, rows in rows_by_year.items()}

    checks: list[dict[str, Any]] = []
    for year, expected_values in EXPECTED.items():
        summary = summaries[year]
        check(checks, f"{year} 总记录数", expected_values["records"], summary["records"])
        check(checks, f"{year} 物种数", expected_values["species"], summary["species"])
        check(checks, f"{year} 科数", expected_values["families"], summary["families"])
        check(checks, f"{year} 属数", expected_values["genera"], summary["genera"])
        check(checks, f"{year} Shannon H", expected_values["shannon"], round(summary["shannon"], 4), 0.001)
        check(checks, f"{year} Simpson D", expected_values["simpson_d"], round(summary["simpson_d"], 6), 0.0001)
        check(checks, f"{year} Pielou J", expected_values["pielou"], round(summary["pielou"], 4), 0.001)

    taxon_counts_2026 = summaries["2026"]["taxon_counts"]
    for taxon, expected_count in EXPECTED_2026_TAXON_COUNTS.items():
        check(checks, f"2026 {taxon} 记录数", expected_count, taxon_counts_2026.get(taxon, 0))

    species_counts_2026: Counter[str] = summaries["2026"]["species_counts"]
    for species_name, expected_count in EXPECTED_TOP20_2026:
        check(checks, f"2026 Top 物种 {species_name}", expected_count, species_counts_2026.get(species_name, 0))

    species_2025 = set(summaries["2025"]["species_counts"])
    species_2026 = set(summaries["2026"]["species_counts"])
    shared = species_2025 & species_2026
    check(checks, "2025/2026 共有物种数", 1399, len(shared))
    check(checks, "仅 2025 出现物种数", 1580, len(species_2025 - species_2026))
    check(checks, "仅 2026 出现物种数", 610, len(species_2026 - species_2025))

    passed = sum(1 for item in checks if item["passed"])
    failed = len(checks) - passed
    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "total_checks": len(checks),
        "passed": passed,
        "failed": failed,
        "pass_rate": f"{passed / len(checks) * 100:.1f}%" if checks else "0.0%",
        "summaries": {
            year: {
                key: value
                for key, value in summary.items()
                if key not in {"species_counts"}
            }
            for year, summary in summaries.items()
        },
        "checks": checks,
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / "数值验证报告.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("=" * 70)
    print(f"验证完成：通过 {passed}/{len(checks)}，未通过 {failed}")
    print(f"报告已保存：{report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
