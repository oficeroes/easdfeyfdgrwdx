# -*- coding: utf-8 -*-
"""检查观测点坐标是否落在澳门陆地区域附近。

用法：
    python scripts/validation/check_coordinates.py

输入：
    表格数据/2025 團隊賽數據包_Sheet1.csv
    表格数据/副本2026 團隊賽數據包_Sheet1.csv
    异常数据/macau_land_reference.geojson

输出：
    异常数据/坐标异常数据_2025.csv
    异常数据/坐标异常数据_2025_详细版.csv
    异常数据/坐标异常数据_2026.csv
    异常数据/坐标异常数据_2026_详细版.csv
    异常数据/坐标验证报告.json
"""

from __future__ import annotations

import csv
import json
import math
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from shapely.geometry import Point, Polygon, shape
    from shapely.ops import unary_union
except ImportError as exc:
    raise SystemExit(
        "缺少 shapely。请先运行：pip install -r requirements.txt\n"
        "shapely 用于判断点是否落在澳门陆地多边形内。"
    ) from exc


ROOT = Path(__file__).resolve().parents[2]
TABLE_DIR = ROOT / "表格数据"
OUTPUT_DIR = ROOT / "异常数据"
REFERENCE_GEOJSON = OUTPUT_DIR / "macau_land_reference.geojson"

# 约 70 米，用于吸收 GPS 浮动、岸线步道和湿地边缘的小范围地图误差。
GPS_TOLERANCE_DEGREES = 0.00065

REQUIRED_COLUMNS = [
    "id",
    "observed_on",
    "time_observed_at",
    "captive_cultivated",
    "longitude",
    "latitude",
    "iconic_taxon_name",
    "taxon_kingdom_name",
    "taxon_phylum_name",
    "taxon_class_name",
    "taxon_order_name",
    "taxon_family_name",
    "taxon_genus_name",
    "taxon_species_name",
    "taxon_subspecies_name",
]

DATASETS = {
    "2025": {"file": "2025 團隊賽數據包_Sheet1.csv"},
    "2026": {"file": "副本2026 團隊賽數據包_Sheet1.csv"},
}

FALLBACK_POLYGONS = {
    "澳门半岛": [
        (113.5282, 22.2171),
        (113.5637, 22.2170),
        (113.5639, 22.2044),
        (113.5608, 22.1985),
        (113.5545, 22.1882),
        (113.5400, 22.1813),
        (113.5282, 22.1813),
        (113.5282, 22.2171),
    ],
    "氹仔": [
        (113.5389, 22.1715),
        (113.5984, 22.1715),
        (113.5984, 22.1206),
        (113.5389, 22.1206),
        (113.5389, 22.1715),
    ],
    "路氹城": [
        (113.5508, 22.1555),
        (113.5889, 22.1555),
        (113.5889, 22.1283),
        (113.5508, 22.1283),
        (113.5508, 22.1555),
    ],
    "路环": [
        (113.5491, 22.1431),
        (113.5926, 22.1431),
        (113.5926, 22.1098),
        (113.5491, 22.1098),
        (113.5491, 22.1431),
    ],
    "横琴澳大校区": [
        (113.5400, 22.1363),
        (113.5536, 22.1363),
        (113.5536, 22.1205),
        (113.5400, 22.1205),
        (113.5400, 22.1363),
    ],
}

OSM_AREA_GROUPS = {
    "澳门半岛": {
        "macau_se",
        "macau_fatima",
        "macau_santo_antonio",
        "macau_sao_lazaro",
        "macau_sao_lourenco",
    },
    "氹仔": {"macau_taipa_island"},
    "路氹城": {"macau_cotai_island"},
    "路环": {"macau_coloane_island"},
    "新城A区": {"macau_new_zone_a"},
}


def detect_encoding(path: Path) -> str:
    with path.open("rb") as file:
        return "utf-8-sig" if file.read(3) == b"\xef\xbb\xbf" else "utf-8"


def normalize_header(header: list[str]) -> list[str]:
    normalized: list[str] = []
    empty_count = 0
    for name in header:
        clean = (name or "").strip()
        if clean:
            normalized.append(clean)
        else:
            empty_count += 1
            normalized.append(f"_empty_{empty_count}")
    return normalized


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding=detect_encoding(path), newline="") as file:
        reader = csv.reader(file)
        raw_header = next(reader)
        header = normalize_header(raw_header)
        rows = [{name: row[i] if i < len(row) else "" for i, name in enumerate(header)} for row in reader]
    return header, rows


def build_polygon(points: list[tuple[float, float]]) -> Polygon:
    polygon = Polygon(points)
    return polygon if polygon.is_valid else polygon.buffer(0)


def load_reference_geometries() -> tuple[dict[str, Any], str]:
    if REFERENCE_GEOJSON.exists():
        with REFERENCE_GEOJSON.open("r", encoding=detect_encoding(REFERENCE_GEOJSON)) as file:
            feature_collection = json.load(file)

        features_by_name: dict[str, list[Any]] = {}
        for feature in feature_collection.get("features", []):
            name = feature.get("properties", {}).get("name")
            geometry = feature.get("geometry")
            if name and geometry:
                features_by_name.setdefault(name, []).append(shape(geometry))

        grouped: dict[str, Any] = {}
        for area_name, source_names in OSM_AREA_GROUPS.items():
            geometries = [
                geometry
                for source_name in source_names
                for geometry in features_by_name.get(source_name, [])
            ]
            if geometries:
                grouped[area_name] = unary_union(geometries)

        grouped["横琴澳大校区"] = build_polygon(FALLBACK_POLYGONS["横琴澳大校区"])
        if grouped:
            return grouped, str(REFERENCE_GEOJSON.relative_to(ROOT))

    return {name: build_polygon(points) for name, points in FALLBACK_POLYGONS.items()}, "内置简化多边形"


AREA_GEOMETRIES, GEOMETRY_SOURCE = load_reference_geometries()


def meters_from_degrees(distance_degrees: float, latitude: float) -> float:
    scale = 111_320 * max(math.cos(math.radians(latitude)), 0.01)
    return distance_degrees * scale


def point_status(longitude: float, latitude: float) -> tuple[bool, str | None, float]:
    point = Point(longitude, latitude)
    for area_name, geometry in AREA_GEOMETRIES.items():
        if geometry.covers(point):
            return True, area_name, 0.0

    nearest_area: str | None = None
    nearest_distance = float("inf")
    for area_name, geometry in AREA_GEOMETRIES.items():
        distance = geometry.distance(point)
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_area = area_name

    if nearest_distance <= GPS_TOLERANCE_DEGREES:
        return True, f"{nearest_area}边界容差内", nearest_distance
    return False, nearest_area, nearest_distance


def get_float(record: dict[str, str], column: str) -> float:
    value = record.get(column, "").strip()
    if not value:
        raise ValueError(f"{column} 为空")
    return float(value)


def issue_text(longitude: float, latitude: float, nearest_area: str | None, distance_degrees: float) -> str:
    distance_meters = round(meters_from_degrees(distance_degrees, latitude))
    nearest = nearest_area or "澳门陆地区域"
    return (
        f"坐标({longitude}, {latitude})不在澳门陆地区域内，"
        f"距离最近区域“{nearest}”约{distance_meters}米，疑似位于海上或超出正常陆地范围。"
    )


def analyze_dataset(year: str, cfg: dict[str, str]) -> dict[str, Any]:
    path = TABLE_DIR / cfg["file"]
    header, rows = read_csv_rows(path)
    missing = [column for column in ("id", "longitude", "latitude") if column not in header]
    if missing:
        raise ValueError(f"{path} 缺少必要列：{', '.join(missing)}")

    area_counts: Counter[str] = Counter()
    abnormal_by_taxon: Counter[str] = Counter()
    invalid_coordinate_records: list[dict[str, Any]] = []
    abnormal_records: list[dict[str, Any]] = []
    normal_count = 0

    for record in rows:
        try:
            longitude = get_float(record, "longitude")
            latitude = get_float(record, "latitude")
        except ValueError as exc:
            invalid_coordinate_records.append(
                {
                    "record": record,
                    "longitude": record.get("longitude", ""),
                    "latitude": record.get("latitude", ""),
                    "issue": str(exc),
                }
            )
            continue

        is_normal, area_name, distance_degrees = point_status(longitude, latitude)
        if is_normal:
            normal_count += 1
            area_counts[area_name or "澳门陆地区域"] += 1
            continue

        taxon = record.get("iconic_taxon_name", "") or "未知"
        abnormal_by_taxon[taxon] += 1
        abnormal_records.append(
            {
                "record": record,
                "longitude": longitude,
                "latitude": latitude,
                "nearest_area": area_name,
                "distance_degrees": distance_degrees,
                "issue": issue_text(longitude, latitude, area_name, distance_degrees),
            }
        )

    abnormal_total = len(abnormal_records) + len(invalid_coordinate_records)
    total = len(rows)
    return {
        "year": year,
        "path": path,
        "header": header,
        "total": total,
        "normal_count": normal_count,
        "abnormal_count": abnormal_total,
        "abnormal_pct": round(abnormal_total / total * 100, 2) if total else 0.0,
        "area_counts": dict(area_counts),
        "abnormal_by_taxon": dict(abnormal_by_taxon),
        "abnormal_records": abnormal_records,
        "invalid_coordinate_records": invalid_coordinate_records,
    }


def export_simple_errors(year: str, result: dict[str, Any]) -> Path:
    output_path = OUTPUT_DIR / f"坐标异常数据_{year}.csv"
    fieldnames = [
        "id",
        "observed_on",
        "longitude",
        "latitude",
        "iconic_taxon_name",
        "taxon_species_name",
        "taxon_genus_name",
        "captive_cultivated",
        "nearest_area",
        "distance_to_land_m",
        "问题说明",
    ]

    with output_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(fieldnames)
        for item in result["abnormal_records"]:
            record = item["record"]
            writer.writerow(
                [
                    record.get("id", ""),
                    record.get("observed_on", ""),
                    item["longitude"],
                    item["latitude"],
                    record.get("iconic_taxon_name", ""),
                    record.get("taxon_species_name", ""),
                    record.get("taxon_genus_name", ""),
                    record.get("captive_cultivated", ""),
                    item.get("nearest_area") or "",
                    round(meters_from_degrees(item["distance_degrees"], item["latitude"])),
                    item["issue"],
                ]
            )
        for item in result["invalid_coordinate_records"]:
            record = item["record"]
            writer.writerow(
                [
                    record.get("id", ""),
                    record.get("observed_on", ""),
                    item["longitude"],
                    item["latitude"],
                    record.get("iconic_taxon_name", ""),
                    record.get("taxon_species_name", ""),
                    record.get("taxon_genus_name", ""),
                    record.get("captive_cultivated", ""),
                    "",
                    "",
                    item["issue"],
                ]
            )
    return output_path


def export_detailed_errors(year: str, result: dict[str, Any]) -> Path:
    output_path = OUTPUT_DIR / f"坐标异常数据_{year}_详细版.csv"
    fieldnames = REQUIRED_COLUMNS + ["nearest_area", "distance_to_land_m", "问题说明"]

    with output_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for item in result["abnormal_records"]:
            record = item["record"].copy()
            row = {column: record.get(column, "") for column in REQUIRED_COLUMNS}
            row["nearest_area"] = item.get("nearest_area") or ""
            row["distance_to_land_m"] = round(meters_from_degrees(item["distance_degrees"], item["latitude"]))
            row["问题说明"] = item["issue"]
            writer.writerow(row)
        for item in result["invalid_coordinate_records"]:
            record = item["record"].copy()
            row = {column: record.get(column, "") for column in REQUIRED_COLUMNS}
            row["nearest_area"] = ""
            row["distance_to_land_m"] = ""
            row["问题说明"] = item["issue"]
            writer.writerow(row)
    return output_path


def geometry_summary() -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    for area_name, geometry in AREA_GEOMETRIES.items():
        min_lng, min_lat, max_lng, max_lat = geometry.bounds
        part_count = len(geometry.geoms) if hasattr(geometry, "geoms") else 1
        vertex_count = 0
        polygons = geometry.geoms if hasattr(geometry, "geoms") else [geometry]
        for polygon in polygons:
            vertex_count += len(polygon.exterior.coords)
            vertex_count += sum(len(interior.coords) for interior in polygon.interiors)
        summary.append(
            {
                "区域": area_name,
                "几何块数": part_count,
                "顶点数": vertex_count,
                "经度范围": [round(min_lng, 7), round(max_lng, 7)],
                "纬度范围": [round(min_lat, 7), round(max_lat, 7)],
            }
        )
    return summary


def export_summary(results: dict[str, dict[str, Any]]) -> Path:
    output_path = OUTPUT_DIR / "坐标验证报告.json"
    report: dict[str, Any] = {
        "生成时间": datetime.now().isoformat(timespec="seconds"),
        "判定规则": "观测点落在澳门陆地参考多边形内，或距离边界不超过 GPS 容差时视为正常；否则标注为疑似海上或超出陆地范围。",
        "边界来源": GEOMETRY_SOURCE,
        "GPS容差_度": GPS_TOLERANCE_DEGREES,
        "GPS容差_约米": round(GPS_TOLERANCE_DEGREES * 111_320),
        "陆地区域定义": geometry_summary(),
        "数据集": {},
    }

    for year, result in results.items():
        report["数据集"][year] = {
            "源文件": str(result["path"].relative_to(ROOT)),
            "总记录数": result["total"],
            "正常记录数": result["normal_count"],
            "异常记录数": result["abnormal_count"],
            "异常比例": f"{result['abnormal_pct']}%",
            "区域分布": result["area_counts"],
            "异常类型分布": result["abnormal_by_taxon"],
            "坐标格式错误数": len(result["invalid_coordinate_records"]),
            "异常文件": [
                str((OUTPUT_DIR / f"坐标异常数据_{year}.csv").relative_to(ROOT)),
                str((OUTPUT_DIR / f"坐标异常数据_{year}_详细版.csv").relative_to(ROOT)),
            ],
        }

    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def print_result(result: dict[str, Any]) -> None:
    print(f"\n分析 {result['year']} 年数据")
    print("-" * 60)
    print(f"源文件：{result['path'].relative_to(ROOT)}")
    print(f"总记录数：{result['total']}")
    print(f"正常记录数：{result['normal_count']}")
    print(f"异常记录数：{result['abnormal_count']} ({result['abnormal_pct']}%)")

    print("\n正常记录区域分布：")
    for area, count in sorted(result["area_counts"].items(), key=lambda item: -item[1]):
        print(f"  {area}: {count}")

    print("\n异常记录类型分布：")
    for taxon, count in sorted(result["abnormal_by_taxon"].items(), key=lambda item: -item[1]):
        print(f"  {taxon}: {count}")

    if result["abnormal_records"]:
        print("\n前 8 条异常记录：")
        for item in result["abnormal_records"][:8]:
            record = item["record"]
            distance_m = round(meters_from_degrees(item["distance_degrees"], item["latitude"]))
            print(
                f"  {record.get('id', '')}: "
                f"({item['longitude']}, {item['latitude']}) "
                f"{record.get('iconic_taxon_name', '')} "
                f"距 {item.get('nearest_area') or '陆地'} 约 {distance_m} 米"
            )


def main() -> None:
    print("=" * 60)
    print("澳门生物多样性数据 - 坐标合理性验证")
    print("=" * 60)
    print(f"边界来源：{GEOMETRY_SOURCE}")
    print(f"GPS 容差：±{GPS_TOLERANCE_DEGREES} 度（约 {round(GPS_TOLERANCE_DEGREES * 111_320)} 米）")

    results: dict[str, dict[str, Any]] = {}
    for year, cfg in DATASETS.items():
        result = analyze_dataset(year, cfg)
        results[year] = result
        print_result(result)
        simple_path = export_simple_errors(year, result)
        detailed_path = export_detailed_errors(year, result)
        print(f"\n已导出：{simple_path.relative_to(ROOT)}")
        print(f"已导出：{detailed_path.relative_to(ROOT)}")

    summary_path = export_summary(results)
    print(f"\n汇总报告已保存：{summary_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
