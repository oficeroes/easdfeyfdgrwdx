# -*- coding: utf-8 -*-
"""生成“澳门生态昼夜曲”专题分析结果和研究大纲。

用法：
    python scripts/analysis/generate_ecological_nocturne.py

输出：
    表格数据/生态昼夜曲/年度类群变化.csv
    表格数据/生态昼夜曲/昼夜节律摘要.csv
    表格数据/生态昼夜曲/光污染梯度摘要.csv
    表格数据/生态昼夜曲/入侵物种预警点位.csv
    报告文档/生态昼夜曲专题分析.json
    报告文档/澳门生态昼夜曲研究大纲.md
"""

from __future__ import annotations

import csv
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from scripts.validation.check_coordinates import GEOMETRY_SOURCE, point_status
except ImportError as exc:
    raise SystemExit(
        "无法导入坐标区域判定工具。请从项目根目录运行本脚本，并先安装 requirements.txt。"
    ) from exc


CLEAN_DIR = ROOT / "表格数据" / "正确数据"
CHINESE_NAME_FILE = ROOT / "表格数据" / "中文名数据" / "中文名数据包.csv"
OUTPUT_TABLE_DIR = ROOT / "表格数据" / "生态昼夜曲"
REPORT_DIR = ROOT / "报告文档"

DATA_FILES = {
    "2025": CLEAN_DIR / "2025 團隊賽數據包_Sheet1.csv",
    "2026": CLEAN_DIR / "副本2026 團隊賽數據包_Sheet1.csv",
}

TAXON_LABELS = {
    "Plantae": "植物",
    "Insecta": "昆虫",
    "Aves": "鸟类",
    "Animalia": "其他动物",
    "Amphibia": "两栖类",
    "Mollusca": "软体动物",
    "Reptilia": "爬行类",
    "Arachnida": "蛛形纲",
    "Actinopterygii": "鱼类",
    "Fungi": "真菌",
    "Mammalia": "哺乳类",
    "Protozoa": "原生动物",
    "": "未分类",
}

TIME_BIN_ORDER = ["夜间", "晨间", "白天", "黄昏"]
FOCUS_TAXA = ["Aves", "Insecta", "Amphibia", "Mollusca", "Arachnida"]

GRADIENT_ORDER = ["高光区", "中高光区", "相对低光区", "补充样本", "未归类"]
AREA_ORDER = ["澳门半岛", "氹仔", "路氹城", "路环", "新城A区", "横琴澳大校区", "澳门陆地区域外"]

INVASIVE_SPECIES = {
    "Sphagneticola trilobata": {
        "chinese_name": "南美蟛蜞菊",
        "type": "入侵植物",
        "concern": "高",
        "risk": "形成密集地被，挤压本土草本植物生境",
    },
    "Anoplolepis gracilipes": {
        "chinese_name": "长足捷蚁",
        "type": "入侵昆虫",
        "concern": "高",
        "risk": "干扰本土无脊椎动物群落，可能改变蚂蚁竞争关系",
    },
    "Solenopsis invicta": {
        "chinese_name": "红火蚁",
        "type": "入侵昆虫",
        "concern": "高",
        "risk": "攻击性强，对本土蚂蚁、小型动物和公众活动空间均有风险",
    },
    "Eleutherodactylus planirostris": {
        "chinese_name": "温室蟾",
        "type": "外来两栖类",
        "concern": "中",
        "risk": "可能与本土蛙类竞争食物和微栖息地",
    },
    "Platydemus manokwari": {
        "chinese_name": "新几内亚扁虫",
        "type": "入侵扁形动物",
        "concern": "中",
        "risk": "捕食本土蜗牛，提示软体动物多样性风险",
    },
}


def clean_text(value: str | None) -> str:
    return (value or "").strip()


def load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def load_chinese_names() -> dict[str, str]:
    if not CHINESE_NAME_FILE.exists():
        return {}
    names: dict[str, str] = {}
    with CHINESE_NAME_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            scientific = clean_text(row.get("scientific_name"))
            chinese = clean_text(row.get("chinese_name"))
            if scientific and chinese:
                names[scientific] = chinese
    for scientific, info in INVASIVE_SPECIES.items():
        names[scientific] = info["chinese_name"]
    return names


def species_name(row: dict[str, str]) -> str:
    return clean_text(row.get("taxon_species_name"))


def taxon_name(row: dict[str, str]) -> str:
    return clean_text(row.get("iconic_taxon_name"))


def unique_values(rows: list[dict[str, str]], field: str) -> set[str]:
    return {clean_text(row.get(field)) for row in rows if clean_text(row.get(field))}


def count_by_field(rows: list[dict[str, str]], field: str) -> Counter[str]:
    return Counter(clean_text(row.get(field)) for row in rows if clean_text(row.get(field)))


def shannon_index(species_counts: Counter[str], total: int) -> float:
    value = 0.0
    for count in species_counts.values():
        if count:
            p = count / total
            value -= p * math.log(p)
    return value


def simpson_d(species_counts: Counter[str], total: int) -> float:
    if total <= 1:
        return 1.0
    return sum(count * (count - 1) for count in species_counts.values()) / (total * (total - 1))


def pielou_evenness(shannon: float, species_count: int) -> float:
    if species_count <= 1:
        return 1.0
    return shannon / math.log(species_count)


def pct(part: int | float, whole: int | float, digits: int = 1) -> float:
    if not whole:
        return 0.0
    return round(float(part) / float(whole) * 100, digits)


def fmt_pct(value: int | float, digits: int = 1) -> str:
    return f"{float(value):.{digits}f}%"


def fmt_signed(value: int | float, digits: int = 1, suffix: str = "") -> str:
    sign = "+" if value > 0 else ""
    if isinstance(value, int):
        return f"{sign}{value:,}{suffix}"
    return f"{sign}{value:.{digits}f}{suffix}"


def summarize_year(rows: list[dict[str, str]], chinese_names: dict[str, str]) -> dict[str, Any]:
    total = len(rows)
    species_counts = Counter(species_name(row) for row in rows if species_name(row))
    species_count = len(species_counts)
    shannon = shannon_index(species_counts, total)
    simpson = simpson_d(species_counts, total)

    taxon_counts = count_by_field(rows, "iconic_taxon_name")
    kingdom_counts = count_by_field(rows, "taxon_kingdom_name")
    captive_counts = count_by_field(rows, "captive_cultivated")

    taxon_species: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        taxon = taxon_name(row)
        species = species_name(row)
        if taxon and species:
            taxon_species[taxon].add(species)

    top_species = []
    for scientific, count in species_counts.most_common(20):
        top_species.append(
            {
                "scientific_name": scientific,
                "chinese_name": chinese_names.get(scientific, ""),
                "count": count,
                "percentage": pct(count, total, 2),
                "taxon": next((taxon_name(row) for row in rows if species_name(row) == scientific), ""),
            }
        )

    singleton_count = sum(1 for count in species_counts.values() if count == 1)
    doubleton_count = sum(1 for count in species_counts.values() if count == 2)
    low_frequency_count = sum(1 for count in species_counts.values() if count <= 5)

    return {
        "records": total,
        "species": species_count,
        "families": len(unique_values(rows, "taxon_family_name")),
        "genera": len(unique_values(rows, "taxon_genus_name")),
        "shannon": round(shannon, 4),
        "simpson_d": round(simpson, 6),
        "simpson_1_minus_d": round(1 - simpson, 6),
        "pielou": round(pielou_evenness(shannon, species_count), 4),
        "taxon_counts": dict(taxon_counts),
        "taxon_species_counts": {taxon: len(species) for taxon, species in taxon_species.items()},
        "kingdom_counts": dict(kingdom_counts),
        "captive_counts": dict(captive_counts),
        "top_species": top_species,
        "singleton_species": singleton_count,
        "doubleton_species": doubleton_count,
        "low_frequency_species_le_5": low_frequency_count,
        "species_counts": dict(species_counts),
    }


def taxon_shift_rows(summaries: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    counts_2025 = summaries["2025"]["taxon_counts"]
    counts_2026 = summaries["2026"]["taxon_counts"]
    species_2025 = summaries["2025"]["taxon_species_counts"]
    species_2026 = summaries["2026"]["taxon_species_counts"]
    total_2025 = summaries["2025"]["records"]
    total_2026 = summaries["2026"]["records"]

    taxa = sorted(set(counts_2025) | set(counts_2026), key=lambda item: counts_2026.get(item, 0), reverse=True)
    rows: list[dict[str, Any]] = []
    for taxon in taxa:
        count_2025 = counts_2025.get(taxon, 0)
        count_2026 = counts_2026.get(taxon, 0)
        pct_2025 = pct(count_2025, total_2025)
        pct_2026 = pct(count_2026, total_2026)
        rows.append(
            {
                "taxon": taxon,
                "taxon_label": TAXON_LABELS.get(taxon, taxon or "未分类"),
                "records_2025": count_2025,
                "records_2026": count_2026,
                "record_delta": count_2026 - count_2025,
                "percentage_2025": pct_2025,
                "percentage_2026": pct_2026,
                "percentage_point_delta": round(pct_2026 - pct_2025, 1),
                "species_2025": species_2025.get(taxon, 0),
                "species_2026": species_2026.get(taxon, 0),
            }
        )
    return rows


def parse_hour(value: str | None) -> int | None:
    text = clean_text(value)
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).hour
    except ValueError:
        return None


def time_bin(hour: int) -> str:
    if hour >= 19 or hour < 6:
        return "夜间"
    if 6 <= hour < 9:
        return "晨间"
    if 9 <= hour < 17:
        return "白天"
    return "黄昏"


def is_night_hour(hour: int | None) -> bool:
    return hour is not None and (hour >= 19 or hour < 6)


def time_summary(rows: list[dict[str, str]], chinese_names: dict[str, str]) -> dict[str, Any]:
    summaries: dict[str, Any] = {}
    for taxon in FOCUS_TAXA:
        subset = [row for row in rows if taxon_name(row) == taxon]
        hour_counts: Counter[int] = Counter()
        bin_counts: Counter[str] = Counter()
        night_species_counts: Counter[str] = Counter()
        missing_time = 0

        for row in subset:
            hour = parse_hour(row.get("time_observed_at"))
            if hour is None:
                missing_time += 1
                continue
            hour_counts[hour] += 1
            current_bin = time_bin(hour)
            bin_counts[current_bin] += 1
            if is_night_hour(hour):
                scientific = species_name(row)
                if scientific:
                    night_species_counts[scientific] += 1

        timed_records = sum(hour_counts.values())
        night_records = bin_counts["夜间"]
        top_night_species = [
            {
                "scientific_name": scientific,
                "chinese_name": chinese_names.get(scientific, ""),
                "count": count,
            }
            for scientific, count in night_species_counts.most_common(5)
        ]
        peak_hour = None
        peak_hour_records = 0
        if hour_counts:
            peak_hour, peak_hour_records = hour_counts.most_common(1)[0]

        summaries[taxon] = {
            "taxon_label": TAXON_LABELS.get(taxon, taxon),
            "total_records": len(subset),
            "timed_records": timed_records,
            "missing_time": missing_time,
            "night_records": night_records,
            "night_percentage": pct(night_records, timed_records),
            "time_bins": {name: bin_counts.get(name, 0) for name in TIME_BIN_ORDER},
            "hourly_counts": {str(hour): hour_counts.get(hour, 0) for hour in range(24)},
            "peak_hour": peak_hour,
            "peak_hour_records": peak_hour_records,
            "top_night_species": top_night_species,
        }
    return summaries


def normalize_area(area: str | None) -> str:
    if not area:
        return "澳门陆地区域外"
    return area.replace("边界容差内", "")


def row_area(row: dict[str, str]) -> str:
    try:
        longitude = float(clean_text(row.get("longitude")))
        latitude = float(clean_text(row.get("latitude")))
    except ValueError:
        return "澳门陆地区域外"

    is_normal, area, _distance = point_status(longitude, latitude)
    if not is_normal:
        return "澳门陆地区域外"
    return normalize_area(area)


def light_gradient(area: str) -> str:
    if area == "澳门半岛":
        return "高光区"
    if area in {"氹仔", "路氹城", "新城A区"}:
        return "中高光区"
    if area == "路环":
        return "相对低光区"
    if area == "横琴澳大校区":
        return "补充样本"
    return "未归类"


def summarize_record_group(rows: list[dict[str, str]]) -> dict[str, Any]:
    species = {species_name(row) for row in rows if species_name(row)}
    taxon_counts = Counter(taxon_name(row) for row in rows if taxon_name(row))
    night_focus_rows = [
        row
        for row in rows
        if taxon_name(row) in {"Insecta", "Amphibia", "Mollusca", "Arachnida"}
        and parse_hour(row.get("time_observed_at")) is not None
    ]
    night_focus_records = sum(1 for row in night_focus_rows if is_night_hour(parse_hour(row.get("time_observed_at"))))
    bird_timed = [row for row in rows if taxon_name(row) == "Aves" and parse_hour(row.get("time_observed_at")) is not None]
    bird_night = sum(1 for row in bird_timed if is_night_hour(parse_hour(row.get("time_observed_at"))))
    insect_timed = [row for row in rows if taxon_name(row) == "Insecta" and parse_hour(row.get("time_observed_at")) is not None]
    insect_night = sum(1 for row in insect_timed if is_night_hour(parse_hour(row.get("time_observed_at"))))

    return {
        "records": len(rows),
        "species": len(species),
        "plant_records": taxon_counts.get("Plantae", 0),
        "insect_records": taxon_counts.get("Insecta", 0),
        "bird_records": taxon_counts.get("Aves", 0),
        "amphibia_records": taxon_counts.get("Amphibia", 0),
        "night_focus_timed_records": len(night_focus_rows),
        "night_focus_records": night_focus_records,
        "night_focus_percentage": pct(night_focus_records, len(night_focus_rows)),
        "bird_night_percentage": pct(bird_night, len(bird_timed)),
        "insect_night_percentage": pct(insect_night, len(insect_timed)),
    }


def spatial_summary(rows: list[dict[str, str]]) -> dict[str, Any]:
    area_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    gradient_rows: dict[str, list[dict[str, str]]] = defaultdict(list)

    for row in rows:
        area = row_area(row)
        gradient = light_gradient(area)
        area_rows[area].append(row)
        gradient_rows[gradient].append(row)

    area_summary = {
        area: summarize_record_group(area_rows[area])
        for area in sorted(area_rows, key=lambda name: AREA_ORDER.index(name) if name in AREA_ORDER else len(AREA_ORDER))
    }
    gradient_summary_data = {
        gradient: summarize_record_group(gradient_rows[gradient])
        for gradient in sorted(
            gradient_rows,
            key=lambda name: GRADIENT_ORDER.index(name) if name in GRADIENT_ORDER else len(GRADIENT_ORDER),
        )
    }
    return {
        "geometry_source": GEOMETRY_SOURCE,
        "area_summary": area_summary,
        "gradient_summary": gradient_summary_data,
    }


def invasive_warning(rows: list[dict[str, str]]) -> dict[str, Any]:
    points: list[dict[str, Any]] = []
    summary: dict[str, Any] = {}

    for row in rows:
        scientific = species_name(row)
        if scientific not in INVASIVE_SPECIES:
            continue
        area = row_area(row)
        gradient = light_gradient(area)
        info = INVASIVE_SPECIES[scientific]
        points.append(
            {
                "id": clean_text(row.get("id")),
                "scientific_name": scientific,
                "chinese_name": info["chinese_name"],
                "type": info["type"],
                "concern": info["concern"],
                "observed_on": clean_text(row.get("observed_on")),
                "time_observed_at": clean_text(row.get("time_observed_at")),
                "latitude": clean_text(row.get("latitude")),
                "longitude": clean_text(row.get("longitude")),
                "area": area,
                "light_gradient": gradient,
            }
        )

    for scientific, info in INVASIVE_SPECIES.items():
        species_points = [point for point in points if point["scientific_name"] == scientific]
        area_counts = Counter(point["area"] for point in species_points)
        gradient_counts = Counter(point["light_gradient"] for point in species_points)
        summary[scientific] = {
            **info,
            "scientific_name": scientific,
            "records": len(species_points),
            "areas": dict(area_counts),
            "light_gradients": dict(gradient_counts),
            "main_area": area_counts.most_common(1)[0][0] if area_counts else "",
            "main_light_gradient": gradient_counts.most_common(1)[0][0] if gradient_counts else "",
        }

    return {"summary": summary, "points": points}


def annual_turnover(summaries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    species_2025 = set(summaries["2025"]["species_counts"])
    species_2026 = set(summaries["2026"]["species_counts"])
    shared = species_2025 & species_2026
    union = species_2025 | species_2026
    return {
        "shared_species": len(shared),
        "only_2025_species": len(species_2025 - species_2026),
        "only_2026_species": len(species_2026 - species_2025),
        "jaccard_similarity": round(len(shared) / len(union) * 100, 1) if union else 0.0,
        "shared_of_2025_percentage": pct(len(shared), len(species_2025)),
        "shared_of_2026_percentage": pct(len(shared), len(species_2026)),
    }


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_outputs(results: dict[str, Any]) -> dict[str, str]:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    taxon_csv = OUTPUT_TABLE_DIR / "年度类群变化.csv"
    rhythm_csv = OUTPUT_TABLE_DIR / "昼夜节律摘要.csv"
    gradient_csv = OUTPUT_TABLE_DIR / "光污染梯度摘要.csv"
    invasive_csv = OUTPUT_TABLE_DIR / "入侵物种预警点位.csv"
    json_path = REPORT_DIR / "生态昼夜曲专题分析.json"
    report_path = REPORT_DIR / "澳门生态昼夜曲研究大纲.md"

    outputs = {
        "taxon_csv": str(taxon_csv.relative_to(ROOT)),
        "rhythm_csv": str(rhythm_csv.relative_to(ROOT)),
        "gradient_csv": str(gradient_csv.relative_to(ROOT)),
        "invasive_csv": str(invasive_csv.relative_to(ROOT)),
        "json": str(json_path.relative_to(ROOT)),
        "report": str(report_path.relative_to(ROOT)),
    }
    results["outputs"] = outputs

    write_csv(
        taxon_csv,
        results["taxon_shift"],
        [
            "taxon",
            "taxon_label",
            "records_2025",
            "records_2026",
            "record_delta",
            "percentage_2025",
            "percentage_2026",
            "percentage_point_delta",
            "species_2025",
            "species_2026",
        ],
    )

    rhythm_rows: list[dict[str, Any]] = []
    for taxon, summary in results["time_summary_2026"].items():
        row = {
            "taxon": taxon,
            "taxon_label": summary["taxon_label"],
            "total_records": summary["total_records"],
            "timed_records": summary["timed_records"],
            "missing_time": summary["missing_time"],
            "night_records": summary["night_records"],
            "night_percentage": summary["night_percentage"],
            "peak_hour": summary["peak_hour"],
            "peak_hour_records": summary["peak_hour_records"],
        }
        for bin_name in TIME_BIN_ORDER:
            row[bin_name] = summary["time_bins"].get(bin_name, 0)
        rhythm_rows.append(row)
    write_csv(
        rhythm_csv,
        rhythm_rows,
        [
            "taxon",
            "taxon_label",
            "total_records",
            "timed_records",
            "missing_time",
            "夜间",
            "晨间",
            "白天",
            "黄昏",
            "night_records",
            "night_percentage",
            "peak_hour",
            "peak_hour_records",
        ],
    )

    gradient_rows = []
    for gradient, summary in results["spatial_summary_2026"]["gradient_summary"].items():
        gradient_rows.append({"light_gradient": gradient, **summary})
    write_csv(
        gradient_csv,
        gradient_rows,
        [
            "light_gradient",
            "records",
            "species",
            "plant_records",
            "insect_records",
            "bird_records",
            "amphibia_records",
            "night_focus_timed_records",
            "night_focus_records",
            "night_focus_percentage",
            "bird_night_percentage",
            "insect_night_percentage",
        ],
    )

    write_csv(
        invasive_csv,
        results["invasive_warning_2026"]["points"],
        [
            "id",
            "scientific_name",
            "chinese_name",
            "type",
            "concern",
            "observed_on",
            "time_observed_at",
            "latitude",
            "longitude",
            "area",
            "light_gradient",
        ],
    )

    json_ready = json.loads(json.dumps(results, ensure_ascii=False))
    json_path.write_text(json.dumps(json_ready, ensure_ascii=False, indent=2), encoding="utf-8")

    report_path.write_text(generate_markdown(results), encoding="utf-8")

    return outputs


def top_species_text(items: list[dict[str, Any]], count: int = 5) -> str:
    pieces = []
    for item in items[:count]:
        chinese = f"（{item['chinese_name']}）" if item.get("chinese_name") else ""
        pieces.append(f"*{item['scientific_name']}*{chinese} {item['count']} 条")
    return "；".join(pieces)


def generate_markdown(results: dict[str, Any]) -> str:
    summaries = results["summaries"]
    turnover = results["annual_turnover"]
    taxon_shift = {row["taxon"]: row for row in results["taxon_shift"]}
    time_summary_2026 = results["time_summary_2026"]
    gradient_summary = results["spatial_summary_2026"]["gradient_summary"]
    invasive_summary = results["invasive_warning_2026"]["summary"]
    outputs = results["outputs"]

    insect_shift = taxon_shift["Insecta"]
    bird_shift = taxon_shift["Aves"]
    plant_shift = taxon_shift["Plantae"]
    animal_2025 = summaries["2025"]["kingdom_counts"].get("Animalia", 0)
    animal_2026 = summaries["2026"]["kingdom_counts"].get("Animalia", 0)

    lines = [
        "# 澳门生态昼夜曲：年度变迁下的不夜城与生物多样性",
        "",
        f"> **生成日期：** {results['generated_at'][:10]}  ",
        "> **定位：** A0 学术海报 + 5 分钟科普短片双用研究大纲  ",
        "> **数据来源：** `表格数据/正确数据/` 中 2025、2026 年澳门生物多样性正确数据  ",
        f"> **区域口径：** 复用坐标验证脚本的澳门陆地区域判定；边界来源：`{results['spatial_summary_2026']['geometry_source']}`",
        "",
        "---",
        "",
        "## 一、核心叙事与研究问题",
        "",
        "本项目以 **2025-2026 年澳门生物多样性年度变迁** 为主背景，以澳门“不夜城”的简化光污染梯度为副背景，讲述城市生态从白天到夜晚、从鸟类到昆虫、从普通记录到入侵物种预警的变化故事。",
        "",
        "**核心问题：** 两年物种记录变化背后，哪些更可能来自采样差异，哪些可能提示城市生态压力？",
        "",
        "**主线表达：**",
        "",
        "- 昆虫记录像城市里的“生态乐声”，呈现 2026 年动物记录增强和夜间活动信号。",
        "- 鸟类分成“日班”和少量“晨昏/夜间班”，展示城市生态节律。",
        "- 入侵物种作为结尾点题：城市变化不仅改变观察记录，也带来真实管理风险。",
        "",
        "---",
        "",
        "## 二、年度变迁总览",
        "",
        "| 指标 | 2025 年 | 2026 年 | 变化 |",
        "|---|---:|---:|---:|",
        f"| 正确记录数 | {summaries['2025']['records']:,} | {summaries['2026']['records']:,} | {fmt_signed(summaries['2026']['records'] - summaries['2025']['records'])} |",
        f"| 物种数 | {summaries['2025']['species']:,} | {summaries['2026']['species']:,} | {fmt_signed(summaries['2026']['species'] - summaries['2025']['species'])} |",
        f"| Shannon H' | {summaries['2025']['shannon']:.4f} | {summaries['2026']['shannon']:.4f} | {fmt_signed(summaries['2026']['shannon'] - summaries['2025']['shannon'], 4)} |",
        f"| Simpson 1-D | {summaries['2025']['simpson_1_minus_d']:.6f} | {summaries['2026']['simpson_1_minus_d']:.6f} | {fmt_signed(summaries['2026']['simpson_1_minus_d'] - summaries['2025']['simpson_1_minus_d'], 6)} |",
        f"| Pielou J' | {summaries['2025']['pielou']:.4f} | {summaries['2026']['pielou']:.4f} | {fmt_signed(summaries['2026']['pielou'] - summaries['2025']['pielou'], 4)} |",
        f"| 动物界记录 | {animal_2025:,} | {animal_2026:,} | {fmt_signed(animal_2026 - animal_2025)} |",
        "",
        f"两年共有物种 **{turnover['shared_species']:,} 种**，2025 独有记录物种 **{turnover['only_2025_species']:,} 种**，2026 独有记录物种 **{turnover['only_2026_species']:,} 种**，Jaccard 物种相似度为 **{fmt_pct(turnover['jaccard_similarity'])}**。",
        "",
        "| 类群 | 2025 记录占比 | 2026 记录占比 | 百分点变化 | 解释方向 |",
        "|---|---:|---:|---:|---|",
        f"| 植物 | {fmt_pct(plant_shift['percentage_2025'])} | {fmt_pct(plant_shift['percentage_2026'])} | {fmt_signed(plant_shift['percentage_point_delta'], 1, 'pp')} | 2025 受植物和圈养/栽培记录影响更强 |",
        f"| 昆虫 | {fmt_pct(insect_shift['percentage_2025'])} | {fmt_pct(insect_shift['percentage_2026'])} | {fmt_signed(insect_shift['percentage_point_delta'], 1, 'pp')} | 2026 动物观察信号增强，是“生态乐声”主角 |",
        f"| 鸟类 | {fmt_pct(bird_shift['percentage_2025'])} | {fmt_pct(bird_shift['percentage_2026'])} | {fmt_signed(bird_shift['percentage_point_delta'], 1, 'pp')} | 样本稳定，适合做日班/晨昏节律 |",
        "",
        "**必须保留的科学边界：** 年际差异可能同时来自采样力度、采样地点、观察重点和真实生态变化；“未再记录”不能写成“消失”。",
        "",
        "---",
        "",
        "## 三、昆虫记录“生态乐声”",
        "",
        f"昆虫记录从 2025 年 **{insect_shift['records_2025']:,} 条** 增至 2026 年 **{insect_shift['records_2026']:,} 条**，占比由 **{fmt_pct(insect_shift['percentage_2025'])}** 升至 **{fmt_pct(insect_shift['percentage_2026'])}**。虽然不能直接说澳门昆虫真实增加，但可以把它作为 2026 年观测重点转向动物类群的重要证据。",
        "",
        "| 类群 | 有时间记录 | 夜间记录 | 夜间比例 | 活动高峰小时 |",
        "|---|---:|---:|---:|---:|",
    ]

    for taxon in ["Insecta", "Amphibia", "Mollusca", "Arachnida"]:
        summary = time_summary_2026[taxon]
        lines.append(
            f"| {summary['taxon_label']} | {summary['timed_records']:,} | {summary['night_records']:,} | {fmt_pct(summary['night_percentage'])} | {summary['peak_hour']}:00 |"
        )

    insect_night = time_summary_2026["Insecta"]
    lines.extend(
        [
            "",
            f"2026 年昆虫有时间记录 **{insect_night['timed_records']:,} 条**，其中夜间记录 **{insect_night['night_records']:,} 条**，夜间比例 **{fmt_pct(insect_night['night_percentage'])}**。海报中建议用“24 小时节律环”或“音轨式柱状图”表达昆虫记录的节奏。",
            "",
            "---",
            "",
            "## 四、鸟类“日班、晨昏班与少量夜班”",
            "",
        ]
    )

    bird_time = time_summary_2026["Aves"]
    bird_bins = bird_time["time_bins"]
    lines.extend(
        [
            f"2026 年鸟类共有 **{summaries['2026']['taxon_counts'].get('Aves', 0):,} 条**记录，其中 **{bird_time['timed_records']:,} 条**有具体时间。鸟类夜间记录比例仅 **{fmt_pct(bird_time['night_percentage'])}**，因此标题和旁白应使用“日班/晨昏班”，不要夸大为大量夜行鸟类。",
            "",
            "| 时间段 | 鸟类记录数 | 画面表达 |",
            "|---|---:|---|",
            f"| 夜间（19:00-05:59） | {bird_bins['夜间']:,} | 少量夜间或清晨前记录，谨慎称为夜班 |",
            f"| 晨间（06:00-08:59） | {bird_bins['晨间']:,} | 清晨鸟声、湿地和城市绿地开场 |",
            f"| 白天（09:00-16:59） | {bird_bins['白天']:,} | 主体“日班”鸟类活动 |",
            f"| 黄昏（17:00-18:59） | {bird_bins['黄昏']:,} | 城市灯光亮起前后的转换镜头 |",
            "",
            f"2026 年鸟类优势种可以作为城市日班代表：{top_species_text([item for item in summaries['2026']['top_species'] if item['taxon'] == 'Aves'], 5)}。",
            "",
            "---",
            "",
            "## 五、不夜城光污染梯度",
            "",
            "本专题采用简化光污染梯度，不引入额外卫星夜间灯光数据：澳门半岛为高光区，氹仔/路氹城/新城 A 区为中高光区，路环为相对低光区。该口径适合高中团队完成，也能支撑短片中的明暗对比。",
            "",
            "| 梯度 | 记录数 | 物种数 | 昆虫记录 | 鸟类记录 | 夜行焦点类群夜间比例 |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )

    for gradient in GRADIENT_ORDER:
        summary = gradient_summary.get(gradient)
        if not summary:
            continue
        lines.append(
            f"| {gradient} | {summary['records']:,} | {summary['species']:,} | {summary['insect_records']:,} | {summary['bird_records']:,} | {fmt_pct(summary['night_focus_percentage'])} |"
        )

    lines.extend(
        [
            "",
            "图表建议：用一张澳门分区地图标出高光区、中高光区和相对低光区，再叠加昆虫、两栖类、软体动物和蛛形纲的夜间记录点。结论应表述为“分区梯度下的初步比较”，不要写成精确光照强度模型。",
            "",
            "---",
            "",
            "## 六、入侵物种结尾点题",
            "",
            "入侵物种不抢主线，而是在结尾说明：城市生态压力不只是记录变化，也会转化为需要管理的具体风险。",
            "",
            "| 物种 | 类型 | 记录数 | 主要区域 | 关注等级 | 点题意义 |",
            "|---|---|---:|---|---|---|",
        ]
    )

    for scientific, info in invasive_summary.items():
        lines.append(
            f"| *{scientific}*（{info['chinese_name']}） | {info['type']} | {info['records']} | {info['main_area'] or '暂无记录'} | {info['concern']} | {info['risk']} |"
        )

    lines.extend(
        [
            "",
            "建议输出“红黄绿早期预警图”：高关注入侵种标红，中关注标黄；低记录种只作为预警点，不做扩散预测。",
            "",
            "---",
            "",
            "## 七、A0 海报结构",
            "",
            "1. **研究问题**：澳门越夜越亮，生物多样性记录是否也在改变？",
            "2. **数据与方法**：2025/2026 正确数据、Shannon/Simpson/Jaccard、时间分箱、简化光污染分区、入侵物种清单。",
            "3. **年度变迁总览**：总记录下降、动物界记录上升、昆虫和鸟类占比提升。",
            "4. **昆虫生态乐声**：昆虫年际跃升、夜间比例、空间热点。",
            "5. **鸟类日班/晨昏班**：24 小时节律图、城市鸟和湿地鸟案例。",
            "6. **入侵物种点题**：重点入侵种卡片和早期预警点位。",
            "7. **保护建议**：暗夜友好照明、路环/湿地暗夜避难区、入侵物种监测、低频物种复查。",
            "",
            "---",
            "",
            "## 八、5 分钟科普短片脚本骨架",
            "",
            "| 时间 | 内容 | 画面/素材 |",
            "|---|---|---|",
            "| 0:00-0:40 | 澳门从白天到夜晚，提出“城市越亮，生态是否也改变？” | 清晨鸟声、夜晚街灯、城市天际线 |",
            "| 0:40-1:40 | 年度变迁：2025 与 2026 数据差异 | 年度总览图、类群比例变化动画 |",
            "| 1:40-2:40 | 昆虫记录“乐声”：昆虫占比上升和夜间活动 | 昆虫点位、节律音轨式柱状图 |",
            "| 2:40-3:35 | 鸟类日班/晨昏班：城市鸟类时间节律 | 鸟类 24 小时时钟图、清晨和黄昏镜头 |",
            "| 3:35-4:25 | 入侵物种：城市生态压力的具体警报 | 入侵物种卡片、预警地图 |",
            "| 4:25-5:00 | 保护建议与结尾口号 | 暗夜友好照明、湿地/路环保护、团队镜头 |",
            "",
            "**结尾口号建议：** 让城市继续明亮，也给夜晚的生命留一点黑暗。",
            "",
            "---",
            "",
            "## 九、补拍素材清单",
            "",
            "- 清晨：鸟声、湿地或公园中鸟类活动、城市刚醒来的环境。",
            "- 白天：绿地、湿地、水边、昆虫或传粉昆虫近景。",
            "- 黄昏：街灯亮起、鸟类归巢或城市光线转换。",
            "- 夜晚：明亮街区与较暗绿地/路环环境对比，注意安全和合法拍摄。",
            "- 入侵物种：南美蟛蜞菊等容易辨认对象，作为结尾风险画面。",
            "",
            "---",
            "",
            "## 十、比赛要求对照与风险控制",
            "",
            "- **生物多样性指数**：已包含 Shannon、Simpson 1-D、Pielou J'。",
            f"- **优势物种**：2026 Top 物种包括 {top_species_text(summaries['2026']['top_species'], 5)}。",
            f"- **稀有物种**：2026 年 singleton 物种 {summaries['2026']['singleton_species']:,} 种，doubleton 物种 {summaries['2026']['doubleton_species']:,} 种，≤5 次记录物种 {summaries['2026']['low_frequency_species_le_5']:,} 种。",
            "- **生态指示物种**：湿地鸟类、两栖类、入侵物种均可作为正向或负向指示信号。",
            "- **空间分布图**：建议使用光污染梯度分区图、夜间物种叠加图、入侵物种预警点位图。",
            "- **保护建议**：暗夜友好照明、湿地和路环暗夜避难区、入侵物种重点监测、公民科学复查低频物种。",
            "- **AI 使用声明**：海报和短片需按比赛要求标注使用 AI 工具。",
            "",
            "**措辞红线：** 不把“未再记录”写成“消失”；不把光污染分区说成精确遥感测量；不把入侵物种点位说成扩散预测；不把昆虫“乐声”写成真实声学研究。",
            "",
            "---",
            "",
            "## 十一、已生成数据文件",
            "",
            f"- `{outputs['taxon_csv']}`",
            f"- `{outputs['rhythm_csv']}`",
            f"- `{outputs['gradient_csv']}`",
            f"- `{outputs['invasive_csv']}`",
            f"- `{outputs['json']}`",
            f"- `{outputs['report']}`",
            "",
            "*本报告由 `scripts/analysis/generate_ecological_nocturne.py` 根据清理后的正确数据自动生成。*",
            "",
        ]
    )

    return "\n".join(lines)


def main() -> None:
    chinese_names = load_chinese_names()
    rows_by_year = {year: load_csv(path) for year, path in DATA_FILES.items()}
    summaries = {year: summarize_year(rows, chinese_names) for year, rows in rows_by_year.items()}

    results: dict[str, Any] = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "data_files": {year: str(path.relative_to(ROOT)) for year, path in DATA_FILES.items()},
        "definitions": {
            "night": "19:00-05:59",
            "morning": "06:00-08:59",
            "day": "09:00-16:59",
            "dusk": "17:00-18:59",
            "light_gradient": {
                "高光区": ["澳门半岛"],
                "中高光区": ["氹仔", "路氹城", "新城A区"],
                "相对低光区": ["路环"],
                "补充样本": ["横琴澳大校区"],
            },
        },
        "summaries": summaries,
        "annual_turnover": annual_turnover(summaries),
        "taxon_shift": taxon_shift_rows(summaries),
        "time_summary_2026": time_summary(rows_by_year["2026"], chinese_names),
        "spatial_summary_2026": spatial_summary(rows_by_year["2026"]),
        "invasive_warning_2026": invasive_warning(rows_by_year["2026"]),
    }

    outputs = write_outputs(results)

    print("澳门生态昼夜曲专题分析已生成：")
    for label, path in outputs.items():
        print(f"- {label}: {path}")


if __name__ == "__main__":
    main()
