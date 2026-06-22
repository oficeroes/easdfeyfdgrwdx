# -*- coding: utf-8 -*-
"""生成干净的澳门轮廓底图 + 物种观测点位叠加。

仅使用 GeoJSON 海岸线数据，不使用官方 WebMap 底图（避免建筑物纹理干扰）。
输出一张干净、学术风格的澳门地图，可叠加所有物种点位。

用法：
    python scripts/visualization/generate_clean_macau_map.py

输出：
    生态昼夜曲资料/图表/图4b_干净澳门底图_夜行点位.png
    生态昼夜曲资料/图表/图5b_干净澳门底图_入侵预警.png
    生态昼夜曲资料/图表/澳门干净轮廓底图.png  （纯底图，可选叠加）
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import numpy as np

try:
    from shapely.geometry import MultiPolygon, Polygon, shape
    from shapely.ops import unary_union

    HAS_SHAPELY = True
except ImportError:
    HAS_SHAPELY = False

ROOT = Path(__file__).resolve().parents[2]
CLEAN_DIR = ROOT / "表格数据" / "正确数据"
DATA_2026 = CLEAN_DIR / "副本2026 團隊賽數據包_Sheet1.csv"
GEOJSON_PATH = ROOT / "异常数据" / "macau_land_reference.geojson"
OUT_DIR = ROOT / "生态昼夜曲资料" / "图表"

# ===== 字体 =====
FONT_PATH = Path("C:/Windows/Fonts/msyh.ttc")
if FONT_PATH.exists():
    fm.fontManager.addfont(str(FONT_PATH))
    plt.rcParams["font.family"] = fm.FontProperties(fname=str(FONT_PATH)).get_name()
plt.rcParams["axes.unicode_minus"] = False

# ===== 配色：大地色系 + 干净海陆对比 =====
WATER = "#E8F0F2"             # 海水：极浅蓝灰
LAND = "#FAF8F5"              # 陆地：暖奶油白
COASTLINE = "#8A9B8E"         # 海岸线：柔和灰绿
LAND_EDGE_INNER = "#B5C0B8"   # 内陆边界：更浅

# 三区配色（大地色系）
ZONE_COLORS = {
    "高光区": "#ECD8B4",      # 澳门半岛：暖沙金
    "中高光区": "#E0C9A8",    # 氹仔/路氹：暖驼色
    "相对低光区": "#C5D8CC",  # 路环：淡松绿
}

# 物种点位配色
NIGHT_POINT_COLORS = {
    "Insecta": "#5C8D6F",     # 昆虫：中森林绿
    "Amphibia": "#1E3D3B",    # 两栖：深青绿
    "Mollusca": "#4DB6AC",    # 软体：teal
    "Arachnida": "#8FA889",   # 蛛形：鼠尾草绿
}
DAY_POINT_COLORS = {
    "Insecta": "#A8C5A0",
    "Amphibia": "#6B9E8A",
    "Mollusca": "#89C4BC",
    "Arachnida": "#B5CCB2",
}

# 入侵物种
INVASIVE_SPECIES = {
    "Sphagneticola trilobata": ("南美蟛蜞菊", "#C4725A"),
    "Anoplolepis gracilipes": ("长足捷蚁", "#C4725A"),
    "Solenopsis invicta": ("红火蚁", "#C4725A"),
    "Eleutherodactylus planirostris": ("温室蟾", "#C8963E"),
    "Platydemus manokwari": ("新几内亚扁虫", "#C8963E"),
}

# 澳门经纬度范围
MAP_BBOX = (113.518, 22.098, 113.603, 22.223)

# 夜间时段
NIGHT_HOURS = {19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5}

# ===== GeoJSON 分区特征名 =====
PENINSULA_FEATURES = {
    "macau_sao_lazaro", "macau_sao_lourenco", "macau_se",
    "macau_fatima", "macau_santo_antonio",
}
MID_LIGHT_FEATURES = {
    "macau_taipa_island", "macau_taipa_admin",
    "macau_cotai_island", "macau_cotai_admin", "macau_new_zone_a",
}
LOW_LIGHT_FEATURES = {
    "macau_coloane_admin", "macau_coloane_island",
}


def feature_zone(name: str) -> str | None:
    if name in PENINSULA_FEATURES:
        return "高光区"
    if name in MID_LIGHT_FEATURES:
        return "中高光区"
    if name in LOW_LIGHT_FEATURES:
        return "相对低光区"
    return None


def load_macau_zones() -> dict[str, list]:
    """从 GeoJSON 加载并按光污染梯度分组合并。"""
    zones: dict[str, list] = {"高光区": [], "中高光区": [], "相对低光区": []}
    if not GEOJSON_PATH.exists():
        print("  WARN: GeoJSON 文件未找到")
        return zones

    data = json.loads(GEOJSON_PATH.read_text(encoding="utf-8-sig"))

    if HAS_SHAPELY:
        geoms: dict[str, list] = defaultdict(list)
        for feat in data.get("features", []):
            zone = feature_zone((feat.get("properties") or {}).get("name", ""))
            if zone:
                geoms[zone].append(shape(feat["geometry"]))
        for zone, items in geoms.items():
            merged = unary_union(items)
            if merged.geom_type == "Polygon":
                zones[zone] = [list(merged.exterior.coords)]
            elif merged.geom_type == "MultiPolygon":
                zones[zone] = [list(p.exterior.coords) for p in merged.geoms]
        return zones

    # 无 Shapely 的回退
    for feat in data.get("features", []):
        zone = feature_zone((feat.get("properties") or {}).get("name", ""))
        if not zone:
            continue
        geom = feat.get("geometry", {})
        if geom.get("type") == "Polygon":
            zones[zone].append([(p[0], p[1]) for p in geom["coordinates"][0]])
        elif geom.get("type") == "MultiPolygon":
            for poly in geom["coordinates"]:
                zones[zone].append([(p[0], p[1]) for p in poly[0]])
    return zones


def load_points(path: Path) -> list[dict]:
    """加载观测点数据。"""
    points = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            try:
                lat = float((row.get("latitude") or "").strip())
                lon = float((row.get("longitude") or "").strip())
            except ValueError:
                continue
            stamp = (row.get("time_observed_at") or "").strip()
            hour = None
            if "T" in stamp:
                hh = stamp.split("T", 1)[1][:2]
                if hh.isdigit():
                    hour = int(hh)
            points.append({
                "lat": lat, "lon": lon,
                "taxon": (row.get("iconic_taxon_name") or "").strip(),
                "species": (row.get("taxon_species_name") or "").strip(),
                "is_night": hour in NIGHT_HOURS if hour is not None else False,
                "hour": hour,
            })
    return points


def draw_clean_basemap(ax, zones: dict[str, list]) -> None:
    """绘制干净的澳门轮廓底图：海水 + 陆地 + 三区底色 + 海岸线。"""
    # 海水背景
    ax.set_facecolor(WATER)

    # 三区填充（柔和底色）
    for zone, polygons in zones.items():
        color = ZONE_COLORS.get(zone, LAND)
        for poly in polygons:
            xs = [p[0] for p in poly]
            ys = [p[1] for p in poly]
            ax.fill(xs, ys, facecolor=color, alpha=0.85,
                    edgecolor="none", zorder=2)

    # 内陆边界（浅线）
    for zone, polygons in zones.items():
        for poly in polygons:
            xs = [p[0] for p in poly]
            ys = [p[1] for p in poly]
            ax.plot(xs, ys, color=LAND_EDGE_INNER, linewidth=0.5, zorder=3)

    # 合并所有区域画外轮廓（粗线 = 海岸线）
    if HAS_SHAPELY:
        all_geoms = []
        for polygons in zones.values():
            for poly in polygons:
                if len(poly) >= 3:
                    all_geoms.append(Polygon(poly))
        if all_geoms:
            merged = unary_union(all_geoms)
            if merged.geom_type == "Polygon":
                all_outlines = [list(merged.exterior.coords)]
            elif merged.geom_type == "MultiPolygon":
                all_outlines = [list(p.exterior.coords) for p in merged.geoms]
            else:
                all_outlines = []
            for outline in all_outlines:
                xs = [p[0] for p in outline]
                ys = [p[1] for p in outline]
                ax.plot(xs, ys, color=COASTLINE, linewidth=1.8, zorder=4)


def format_map(ax) -> None:
    ax.set_xlim(MAP_BBOX[0], MAP_BBOX[2])
    ax.set_ylim(MAP_BBOX[1], MAP_BBOX[3])
    ax.set_aspect("equal")
    ax.set_xticks([113.52, 113.54, 113.56, 113.58, 113.60])
    ax.set_yticks([22.10, 22.12, 22.14, 22.16, 22.18, 22.20, 22.22])
    ax.xaxis.set_major_formatter(FormatStrFormatter("%.3f"))
    ax.yaxis.set_major_formatter(FormatStrFormatter("%.3f"))
    ax.set_xlabel("经度", fontsize=9, color="#5C6B62")
    ax.set_ylabel("纬度", fontsize=9, color="#5C6B62")
    ax.tick_params(colors="#5C6B62", labelsize=8.5)
    for spine in ax.spines.values():
        spine.set_color("#B5C0B8")


# ===== 图 4b：干净底图 + 夜行点位 =====
def make_night_focus_map(points: list[dict], zones: dict[str, list]) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "图4b_干净澳门底图_夜行点位.png"

    night_focus_taxa = {"Insecta", "Amphibia", "Mollusca", "Arachnida"}

    fig, ax = plt.subplots(figsize=(10.5, 7.8), facecolor="white")
    fig.subplots_adjust(left=0.08, right=0.92, top=0.90, bottom=0.10)

    draw_clean_basemap(ax, zones)

    # 叠加夜行焦点类群点位
    for taxon, color, marker, size, label in [
        ("Insecta", NIGHT_POINT_COLORS["Insecta"], "o", 7, "昆虫"),
        ("Amphibia", NIGHT_POINT_COLORS["Amphibia"], "s", 13, "两栖类"),
        ("Mollusca", NIGHT_POINT_COLORS["Mollusca"], "D", 10, "软体动物"),
        ("Arachnida", NIGHT_POINT_COLORS["Arachnida"], "^", 10, "蛛形纲"),
    ]:
        pts = [p for p in points
               if p["taxon"] == taxon and p["is_night"]]
        if pts:
            ax.scatter([p["lon"] for p in pts], [p["lat"] for p in pts],
                       s=size, color=color, marker=marker, alpha=0.65,
                       edgecolors="white", linewidth=0.2,
                       label=f"{label} 夜间 ({len(pts)}点)", zorder=5)

    # 区域标注
    ax.text(113.547, 22.201, "澳门半岛\n高光区", ha="center", fontsize=9.5,
            color="#6B5B3E", fontweight="bold")
    ax.text(113.560, 22.155, "氹仔/路氹\n中高光区", ha="center", fontsize=9.5,
            color="#6B5B3E", fontweight="bold")
    ax.text(113.569, 22.122, "路环\n相对低光区", ha="center", fontsize=9.5,
            color="#2A4A42", fontweight="bold")

    format_map(ax)
    ax.legend(loc="lower right", frameon=True, facecolor="white",
              edgecolor="#D5DDD7", fontsize=7.5)

    fig.suptitle("澳门光污染梯度与夜行焦点类群夜间点位",
                 fontsize=15, fontweight="bold", color="#3B5245", y=0.955)
    fig.text(0.5, 0.035, "底图数据：OpenStreetMap/Nominatim 澳门陆地多边形。"
             "分区为简化光污染梯度，不等同于精确遥感灯光强度。\n"
             "点位：2026 年正确数据中夜行焦点类群（昆虫、两栖类、软体动物、蛛形纲）的夜间记录。",
             ha="center", fontsize=8, color="#8B8B8B")

    fig.savefig(out_path, dpi=300, facecolor="white")
    plt.close(fig)
    return out_path


# ===== 图 5b：干净底图 + 入侵预警 =====
def make_invasive_map(points: list[dict], zones: dict[str, list]) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "图5b_干净澳门底图_入侵预警.png"

    # 收集入侵物种记录
    invasive_records: dict[str, list] = defaultdict(list)
    for p in points:
        sp = p.get("species", "")
        if sp in INVASIVE_SPECIES:
            invasive_records[sp].append(p)

    fig, (ax_map, ax_panel) = plt.subplots(1, 2, figsize=(12, 7.5),
                                           gridspec_kw={"width_ratios": [1.35, 0.85]})
    fig.subplots_adjust(left=0.04, right=0.96, top=0.88, bottom=0.12, wspace=0.12)
    ax_panel.axis("off")

    draw_clean_basemap(ax_map, zones)

    # 入侵物种点位
    markers_risk = {"高": ("X", 38), "中": ("D", 44)}
    summary = []
    for sp, (cn_name, color) in INVASIVE_SPECIES.items():
        recs = invasive_records.get(sp, [])
        if not recs:
            continue
        risk = "高" if color == "#C4725A" else "中"
        marker, size = markers_risk[risk]
        ax_map.scatter([r["lon"] for r in recs], [r["lat"] for r in recs],
                       s=size, color=color, marker=marker,
                       edgecolors="white", linewidth=0.5, alpha=0.82, zorder=5,
                       label=f"{cn_name} ({len(recs)}条)")
        summary.append((cn_name, risk, len(recs), color))

    format_map(ax_map)
    ax_map.legend(loc="lower right", frameon=True, facecolor="white",
                  edgecolor="#D5DDD7", fontsize=7.5)

    # 右侧预警卡片
    ax_panel.text(0.02, 0.96, "预警清单", transform=ax_panel.transAxes,
                  fontsize=14, fontweight="bold", color="#C4725A", va="top")
    y = 0.83
    for name, risk, cnt, color in summary:
        rect = mpatches.FancyBboxPatch((0.02, y - 0.12), 0.95, 0.10,
                                       boxstyle="round,pad=0.015",
                                       facecolor="white", edgecolor=color,
                                       linewidth=2, transform=ax_panel.transAxes)
        ax_panel.add_patch(rect)
        ax_panel.text(0.08, y - 0.04, f"[{risk}风险]  {name}",
                      transform=ax_panel.transAxes, fontsize=10,
                      color="#3B5245", fontweight="bold", va="center")
        ax_panel.text(0.90, y - 0.04, f"{cnt} 条",
                      transform=ax_panel.transAxes, fontsize=16,
                      color=color, fontweight="bold", ha="right", va="center")
        y -= 0.18

    fig.suptitle("重点入侵或外来物种早期预警",
                 fontsize=15, fontweight="bold", color="#3B5245", y=0.935)
    fig.text(0.5, 0.035, "底图数据：OpenStreetMap/Nominatim 澳门陆地多边形。"
             "点位代表 2026 年正确数据中的观测记录，不代表分布范围或扩散速度。\n"
             "物种：南美蟛蜞菊、长足捷蚁、红火蚁、温室蟾、新几内亚扁虫。",
             ha="center", fontsize=8, color="#8B8B8B")

    fig.savefig(out_path, dpi=300, facecolor="white")
    plt.close(fig)
    return out_path


# ===== 纯底图（无点位）=====
def make_pure_basemap(zones: dict[str, list]) -> Path:
    """生成一张干净的纯轮廓底图，方便设计师后续叠加使用。"""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "澳门干净轮廓底图.png"

    fig, ax = plt.subplots(figsize=(8, 8), facecolor="white")
    fig.subplots_adjust(left=0.08, right=0.92, top=0.94, bottom=0.08)

    draw_clean_basemap(ax, zones)
    format_map(ax)

    fig.suptitle("澳门陆地轮廓（干净底图）",
                 fontsize=14, fontweight="bold", color="#3B5245", y=0.96)
    fig.text(0.5, 0.03, "数据来源：OpenStreetMap/Nominatim，仅供学术海报使用。",
             ha="center", fontsize=8, color="#8B8B8B")

    fig.savefig(out_path, dpi=300, facecolor="white")
    plt.close(fig)
    return out_path


# ===== 主函数 =====
def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("加载数据...")
    zones = load_macau_zones()
    points = load_points(DATA_2026)
    print(f"  分区: { {k: len(v) for k, v in zones.items()} }")
    print(f"  点位: {len(points)}")

    print("\n[底图] 纯轮廓底图...")
    p = make_pure_basemap(zones)
    print(f"  ✓ {p.relative_to(ROOT)}")

    print("[图4b] 夜行焦点类群点位...")
    p = make_night_focus_map(points, zones)
    print(f"  ✓ {p.relative_to(ROOT)}")

    print("[图5b] 入侵物种预警...")
    p = make_invasive_map(points, zones)
    print(f"  ✓ {p.relative_to(ROOT)}")

    print("\n✅ 全部 3 张干净底图已生成！")


if __name__ == "__main__":
    main()
