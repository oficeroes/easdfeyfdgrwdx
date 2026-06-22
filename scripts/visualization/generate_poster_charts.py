# -*- coding: utf-8 -*-
"""Generate poster charts for the Macau ecological nocturne project.

All figures are computed from the cleaned datasets under 表格数据/正确数据.
Spatial figures use 异常数据/macau_land_reference.geojson as the land outline.
"""

from __future__ import annotations

import csv
import json
import math
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
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
DATA_2025 = CLEAN_DIR / "2025 團隊賽數據包_Sheet1.csv"
DATA_2026 = CLEAN_DIR / "副本2026 團隊賽數據包_Sheet1.csv"
GEOJSON_PATH = ROOT / "异常数据" / "macau_land_reference.geojson"
OUT_DIR = ROOT / "生态昼夜曲资料" / "图表"
OFFICIAL_BASEMAP = OUT_DIR / "_official_macau_wgs84_basemap.png"
OFFICIAL_BASEMAP_URL = "https://webmap.gis.gov.mo/arcgis/rest/services/WebMap/Macau_T_WGS84/MapServer/export"
MAP_BBOX = (113.518, 22.098, 113.603, 22.223)

FONT_PATH = Path("C:/Windows/Fonts/msyh.ttc")
if FONT_PATH.exists():
    fm.fontManager.addfont(str(FONT_PATH))
    plt.rcParams["font.family"] = fm.FontProperties(fname=str(FONT_PATH)).get_name()
plt.rcParams["axes.unicode_minus"] = False


GREEN_DARK = "#1f5f3b"
GREEN_MID = "#2f7d48"
GREEN_LIGHT = "#8fc95b"
TEAL = "#006b63"
ORANGE = "#e8742f"
AMBER = "#f0b44b"
RED = "#cf2f2f"
INK = "#26332d"
MUTED = "#65736c"
GRID = "#d7ded8"
LAND_EDGE = "#9ea9a2"
LAND_BASE = "#f2f4f1"

NIGHT_HOURS = {19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5}

FOCUS = [
    ("Aves", "鸟类", "日班", GREEN_LIGHT),
    ("Insecta", "昆虫", "全天", GREEN_MID),
    ("Amphibia", "两栖类", "夜班", TEAL),
]

INVASIVE_SPECIES = {
    "Sphagneticola trilobata": ("南美蟛蜞菊", "高"),
    "Anoplolepis gracilipes": ("长足捷蚁", "高"),
    "Solenopsis invicta": ("红火蚁", "高"),
    "Eleutherodactylus planirostris": ("温室蟾", "中"),
    "Platydemus manokwari": ("新几内亚扁虫", "中"),
}

ZONE_COLORS = {
    "高光区": "#f5cf64",
    "中高光区": "#f0a857",
    "相对低光区": "#2f8b78",
}
ZONE_META = {
    "高光区": {
        "label": "澳门半岛",
        "night_pct": 16.9,
        "records": 8489,
        "species": 1252,
        "xy": (113.548, 22.201),
    },
    "中高光区": {
        "label": "氹仔 / 路氹 / 新城A区",
        "night_pct": 5.3,
        "records": 5518,
        "species": 1029,
        "xy": (113.560, 22.153),
    },
    "相对低光区": {
        "label": "路环",
        "night_pct": 37.6,
        "records": 4309,
        "species": 917,
        "xy": (113.569, 22.121),
    },
}
PENINSULA_FEATURES = {
    "macau_sao_lazaro",
    "macau_sao_lourenco",
    "macau_se",
    "macau_fatima",
    "macau_santo_antonio",
}
MID_LIGHT_FEATURES = {
    "macau_taipa_island",
    "macau_taipa_admin",
    "macau_cotai_island",
    "macau_cotai_admin",
    "macau_new_zone_a",
}
LOW_LIGHT_FEATURES = {
    "macau_coloane_admin",
    "macau_coloane_island",
}


def style_axes(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#aeb8b1")
    ax.spines["bottom"].set_color("#aeb8b1")
    ax.tick_params(colors=INK, labelsize=9)


def add_title(fig, title: str, subtitle: str | None = None) -> None:
    fig.text(0.06, 0.955, title, ha="left", va="top", fontsize=18,
             fontweight="bold", color=GREEN_DARK)
    if subtitle:
        fig.text(0.06, 0.905, subtitle, ha="left", va="top", fontsize=9.5,
                 color=MUTED)


def add_note(fig, text: str) -> None:
    fig.text(0.5, 0.035, text, ha="center", va="bottom", fontsize=8.2,
             color=MUTED, linespacing=1.4)


def parse_hour(value: str | None) -> int | None:
    stamp = (value or "").strip()
    if "T" not in stamp:
        return None
    hh = stamp.split("T", 1)[1][:2]
    return int(hh) if hh.isdigit() else None


def load_hourly_counts(path: Path) -> dict[str, Counter]:
    counts: dict[str, Counter] = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            taxon = (row.get("iconic_taxon_name") or "").strip()
            hour = parse_hour(row.get("time_observed_at"))
            if taxon and hour is not None and 0 <= hour <= 23:
                counts.setdefault(taxon, Counter())[hour] += 1
    return counts


def night_percentage(counter: Counter) -> float:
    timed = sum(counter.values())
    if not timed:
        return 0.0
    night = sum(counter.get(h, 0) for h in NIGHT_HOURS)
    return round(night / timed * 100, 1)


def peak_hour(counter: Counter) -> int:
    return max(counter, key=lambda h: counter[h]) if counter else 0


def load_year_summary(path: Path) -> dict:
    records = 0
    species_counts: Counter = Counter()
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            records += 1
            sp = (row.get("taxon_species_name") or "").strip()
            if sp:
                species_counts[sp] += 1

    species = len(species_counts)
    shannon = 0.0
    for cnt in species_counts.values():
        p = cnt / records
        shannon -= p * math.log(p)
    simpson_d = sum((cnt / records) ** 2 for cnt in species_counts.values())
    pielou = shannon / math.log(species) if species > 1 else 0
    return {
        "records": records,
        "species": species,
        "shannon": round(shannon, 4),
        "simpson_1d": round(1 - simpson_d, 6),
        "pielou": round(pielou, 4),
    }


def load_taxon_counts(path: Path) -> dict[str, int]:
    counts: Counter = Counter()
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            taxon = (row.get("iconic_taxon_name") or "").strip() or "other"
            counts[taxon] += 1
    return dict(counts)


def load_coordinates(path: Path) -> list[dict]:
    points = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            try:
                lat = float((row.get("latitude") or "").strip())
                lon = float((row.get("longitude") or "").strip())
            except ValueError:
                continue
            hour = parse_hour(row.get("time_observed_at"))
            points.append({
                "lat": lat,
                "lon": lon,
                "taxon": (row.get("iconic_taxon_name") or "").strip(),
                "species": (row.get("taxon_species_name") or "").strip(),
                "is_night": hour in NIGHT_HOURS if hour is not None else False,
                "hour": hour,
            })
    return points


def load_species_set(path: Path) -> set[str]:
    species: set[str] = set()
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            sp = (row.get("taxon_species_name") or "").strip()
            if sp:
                species.add(sp)
    return species


def feature_zone(name: str) -> str | None:
    if name in PENINSULA_FEATURES:
        return "高光区"
    if name in MID_LIGHT_FEATURES:
        return "中高光区"
    if name in LOW_LIGHT_FEATURES:
        return "相对低光区"
    return None


def geometry_to_polygons(geom) -> list[list[tuple[float, float]]]:
    if geom.geom_type == "Polygon":
        return [list(geom.exterior.coords)]
    if geom.geom_type == "MultiPolygon":
        return [list(poly.exterior.coords) for poly in geom.geoms]
    return []


def load_macau_zones() -> dict[str, list[list[tuple[float, float]]]]:
    zones: dict[str, list] = {"高光区": [], "中高光区": [], "相对低光区": []}
    if not GEOJSON_PATH.exists():
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
            zones[zone] = geometry_to_polygons(merged)
        return zones

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


def draw_zone_map(ax, zones: dict[str, list], *, colored: bool = True) -> None:
    for zone, polygons in zones.items():
        color = ZONE_COLORS.get(zone, LAND_BASE) if colored else LAND_BASE
        alpha = 0.58 if colored else 1.0
        for poly in polygons:
            xs = [p[0] for p in poly]
            ys = [p[1] for p in poly]
            ax.fill(xs, ys, facecolor=color, alpha=alpha, edgecolor=LAND_EDGE,
                    linewidth=0.65, zorder=1)


def ensure_official_basemap() -> Path | None:
    """Download and cache the Macau official WGS84 map image used as basemap."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if OFFICIAL_BASEMAP.exists() and OFFICIAL_BASEMAP.stat().st_size > 10_000:
        return OFFICIAL_BASEMAP

    params = {
        "bbox": ",".join(str(v) for v in MAP_BBOX),
        "bboxSR": "4326",
        "imageSR": "4326",
        "size": "1800,2600",
        "format": "png32",
        "transparent": "false",
        "f": "image",
    }
    url = OFFICIAL_BASEMAP_URL + "?" + urllib.parse.urlencode(params)
    try:
        urllib.request.urlretrieve(url, OFFICIAL_BASEMAP)
    except Exception as exc:  # pragma: no cover - network fallback
        print(f"  WARN official basemap download failed: {exc}")
        return None
    return OFFICIAL_BASEMAP if OFFICIAL_BASEMAP.exists() else None


def draw_clean_basemap(ax, zones: dict[str, list]) -> None:
    """绘制干净的澳门轮廓底图：海水 + 三区柔和底色 + 海岸线。无建筑物纹理。"""
    ax.set_facecolor("#E8F0F2")  # 海水：极浅蓝灰
    for zone, polygons in zones.items():
        color = ZONE_COLORS.get(zone, LAND_BASE)
        for poly in polygons:
            xs = [p[0] for p in poly]
            ys = [p[1] for p in poly]
            ax.fill(xs, ys, facecolor=color, alpha=0.78, edgecolor="none", zorder=2)
            ax.plot(xs, ys, color=LAND_EDGE, linewidth=0.6, zorder=3)

    # 合并外轮廓画粗海岸线
    if HAS_SHAPELY:
        all_geoms = []
        for polygons in zones.values():
            for poly in polygons:
                if len(poly) >= 3:
                    all_geoms.append(Polygon(poly))
        if all_geoms:
            merged = unary_union(all_geoms)
            outlines = geometry_to_polygons(merged)
            for outline in outlines:
                xs = [p[0] for p in outline]
                ys = [p[1] for p in outline]
                ax.plot(xs, ys, color="#8A9B8E", linewidth=1.5, zorder=4)


def draw_official_basemap(ax) -> bool:
    basemap = ensure_official_basemap()
    if not basemap:
        return False
    ax.patch.set_alpha(0)
    image = plt.imread(basemap)
    if image.shape[-1] == 3:
        rgb = image[..., :3].copy()
        alpha = np.ones(rgb.shape[:2])
    else:
        rgb = image[..., :3].copy()
        alpha = image[..., 3].copy()

    # The official map service uses very thin pale lines. Strengthen non-white
    # pixels so coastlines and roads remain visible after poster scaling.
    darkness = 1 - rgb.mean(axis=2)
    mask = darkness > 0.025
    rgb[mask] = rgb[mask] * 0.45
    alpha = np.where(mask, np.maximum(alpha, 0.72), 1.0)
    enhanced = np.dstack([rgb, alpha])
    extent = (MAP_BBOX[0], MAP_BBOX[2], MAP_BBOX[1], MAP_BBOX[3])
    ax.imshow(enhanced, extent=extent, origin="upper", zorder=1,
              interpolation="nearest", aspect="auto")
    return True


def format_map_axis(ax) -> None:
    ax.set_xlim(MAP_BBOX[0], MAP_BBOX[2])
    ax.set_ylim(MAP_BBOX[1], MAP_BBOX[3])
    ax.set_aspect("equal")
    ax.set_xticks([113.52, 113.54, 113.56, 113.58, 113.60])
    ax.set_yticks([22.10, 22.12, 22.14, 22.16, 22.18, 22.20, 22.22])
    ax.xaxis.set_major_formatter(FormatStrFormatter("%.3f"))
    ax.yaxis.set_major_formatter(FormatStrFormatter("%.3f"))
    ax.grid(False)
    ax.set_xlabel("经度", fontsize=9, color=INK)
    ax.set_ylabel("纬度", fontsize=9, color=INK)
    style_axes(ax)


def draw_year_comparison(summary_2025: dict, summary_2026: dict) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "图1_年度指标总览.png"

    cards = [
        ("正确记录", "records", "条", "{:,}", "记录规模下降", "-45.2%"),
        ("物种数", "species", "种", "{:,}", "记录物种减少", "-32.6%"),
        ("Shannon H'", "shannon", "", "{:.2f}", "多样性仍高", "-0.30"),
        ("Pielou J'", "pielou", "", "{:.4f}", "均匀度略高", "+0.0045"),
    ]

    fig = plt.figure(figsize=(8.6, 5.5), facecolor="white")
    add_title(fig, "图 1  年度指标总览", "不同量纲分开呈现，避免把记录数、指数值压在同一坐标轴上。")
    gs = fig.add_gridspec(2, 2, left=0.06, right=0.94, top=0.82, bottom=0.15,
                          hspace=0.24, wspace=0.18)

    for i, (label, key, unit, fmt, caption, delta) in enumerate(cards):
        ax = fig.add_subplot(gs[i // 2, i % 2])
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        bg = mpatches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.025",
                                     facecolor="#f7faf6", edgecolor="#d6e0d7",
                                     linewidth=1.2)
        ax.add_patch(bg)

        v25 = summary_2025[key]
        v26 = summary_2026[key]
        ax.text(0.07, 0.82, label, fontsize=12, fontweight="bold", color=INK)
        ax.text(0.07, 0.55, f"2025  {fmt.format(v25)}{unit}",
                fontsize=12, color=ORANGE, fontweight="bold")
        ax.text(0.07, 0.34, f"2026  {fmt.format(v26)}{unit}",
                fontsize=12, color=GREEN_DARK, fontweight="bold")
        ax.text(0.88, 0.55, "→", fontsize=18, color="#9aa79f", ha="center",
                va="center")
        ax.text(0.88, 0.28, delta, fontsize=16, color=GREEN_DARK,
                fontweight="bold", ha="center")
        ax.text(0.07, 0.12, caption, fontsize=8.5, color=MUTED)

    add_note(fig, "数据口径：剔除坐标异常后的正确数据。指数只描述记录组成，不等同于真实生态质量升降。")
    fig.savefig(out_path, dpi=300, facecolor="white")
    plt.close(fig)
    return out_path


TAXON_GROUPS = [
    ("Plantae", "植物", "#c4dfbd"),
    ("Insecta", "昆虫", "#44a154"),
    ("Aves", "鸟类", "#8fc95b"),
    ("Animalia", "其他动物", "#86bdb0"),
    ("Amphibia", "两栖类", "#006b63"),
    ("Mollusca", "软体动物", "#58b7ac"),
    ("Reptilia", "爬行类", "#6baa74"),
    ("Arachnida", "蛛形纲", "#a2c986"),
    ("Actinopterygii", "鱼类", "#4b8f74"),
    ("Fungi", "真菌", "#b9b3d9"),
    ("Mammalia", "哺乳类", "#6d8f4f"),
]


def draw_taxon_structure(t25: dict[str, int], t26: dict[str, int]) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "图2_类群结构变化.png"

    total_25 = sum(t25.values())
    total_26 = sum(t26.values())
    rows = []
    known = {taxon for taxon, _, _ in TAXON_GROUPS}
    for taxon, label, color in TAXON_GROUPS:
        rows.append((taxon, label, color, t25.get(taxon, 0), t26.get(taxon, 0)))
    rows.append((
        "other",
        "其他",
        "#c7c7c7",
        sum(v for k, v in t25.items() if k not in known),
        sum(v for k, v in t26.items() if k not in known),
    ))

    fig, ax = plt.subplots(figsize=(9.2, 6.1), facecolor="white")
    fig.subplots_adjust(left=0.18, right=0.78, top=0.80, bottom=0.27)
    add_title(fig, "图 2  类群结构变化", "2026 年动物相关类群占比更高，为昼夜节律分析提供基础。")

    left_25 = 0
    left_26 = 0
    legend = []
    for _, label, color, c25, c26 in rows:
        p25 = c25 / total_25 * 100
        p26 = c26 / total_26 * 100
        ax.barh(1, p25, left=left_25, color=color, edgecolor="white", height=0.34)
        ax.barh(0, p26, left=left_26, color=color, edgecolor="white", height=0.34)
        if label in {"植物", "昆虫", "鸟类"}:
            if p25 > 5:
                ax.text(left_25 + p25 / 2, 1, f"{label}\n{p25:.1f}%",
                        ha="center", va="center", fontsize=9, color=INK,
                        fontweight="bold")
            if p26 > 5:
                ax.text(left_26 + p26 / 2, 0, f"{label}\n{p26:.1f}%",
                        ha="center", va="center", fontsize=9, color=INK,
                        fontweight="bold")
        left_25 += p25
        left_26 += p26
        if c25 or c26:
            legend.append(mpatches.Patch(color=color, label=label))

    ax.set_yticks([1, 0])
    ax.set_yticklabels([f"2025 年  {total_25:,} 条", f"2026 年  {total_26:,} 条"],
                       fontsize=11, color=INK)
    ax.set_xlim(0, 100)
    ax.set_xlabel("记录占比 (%)", fontsize=10, color=INK)
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    style_axes(ax)
    ax.legend(handles=legend, loc="center left", bbox_to_anchor=(1.01, 0.5),
              frameon=False, fontsize=8.5, ncol=1)
    fig.text(0.18, 0.135,
             "重点变化：植物 76.0% -> 53.0%；昆虫 8.7% -> 20.0%；鸟类 9.5% -> 16.4%。",
             fontsize=9.3, color=GREEN_DARK, fontweight="bold", ha="left")
    fig.text(0.5, 0.055,
             "所有类群合计为 100%。小类群不强行写入条内，避免文字挤压和误读。",
             ha="center", va="bottom", fontsize=8.2, color=MUTED)
    fig.savefig(out_path, dpi=300, facecolor="white")
    plt.close(fig)
    return out_path


def draw_circadian_ring(counts: dict[str, Counter]) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "图3_24小时昼夜节律环.png"

    hours = list(range(24))
    theta = np.deg2rad([h * 15 for h in hours])
    theta_closed = np.append(theta, theta[0])

    fig, ax = plt.subplots(figsize=(8.4, 8.8), subplot_kw={"projection": "polar"},
                           facecolor="white")
    fig.subplots_adjust(top=0.84, bottom=0.20, left=0.08, right=0.92)
    add_title(fig, "图 3  焦点类群的 24 小时记录节律", "0:00 在正上方，顺时针读图；曲线按各自峰值归一化。")

    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    for h in NIGHT_HOURS:
        ax.bar(np.deg2rad(h * 15), 1.18, width=np.deg2rad(15),
               color="#dfe8e0", edgecolor="none", zorder=0)
    ax.text(np.deg2rad(0), 1.28, "夜", ha="center", va="center",
            fontsize=13, color="#91a79a", fontweight="bold")
    ax.text(np.deg2rad(180), 1.28, "昼", ha="center", va="center",
            fontsize=13, color="#bd9827", fontweight="bold")

    summary = []
    for taxon, label, tag, color in FOCUS:
        counter = counts.get(taxon, Counter())
        raw = np.array([counter.get(h, 0) for h in hours], dtype=float)
        norm = raw / raw.max() if raw.max() else raw
        peak = peak_hour(counter)
        ax.plot(theta_closed, np.append(norm, norm[0]), color=color, linewidth=2.7,
                zorder=4, solid_joinstyle="round")
        ax.fill(theta_closed, np.append(norm, norm[0]), color=color, alpha=0.14,
                zorder=2)
        ax.plot(np.deg2rad(peak * 15), norm[peak], "o", color=color, markersize=8,
                markeredgecolor="white", markeredgewidth=1.3, zorder=5)
        summary.append((label, tag, color, peak, night_percentage(counter), int(raw.sum())))

    ax.set_xticks(np.deg2rad([h * 15 for h in range(0, 24, 3)]))
    ax.set_xticklabels([f"{h}:00" for h in range(0, 24, 3)], fontsize=9)
    ax.set_yticks([0.5, 1.0])
    ax.set_yticklabels(["50%", "峰值"], fontsize=8, color="#7a8680")
    ax.set_ylim(0, 1.30)
    ax.grid(color="#cad5ce", linewidth=0.6)
    ax.spines["polar"].set_visible(False)

    handles = [
        Line2D([0], [0], color=c, linewidth=3,
               label=f"{lab}（{tag}）  峰值 {pk:02d}:00  夜间 {ng}%  n={n}")
        for lab, tag, c, pk, ng, n in summary
    ]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.095),
               frameon=False, fontsize=9.5, ncol=1, handlelength=2.0)
    add_note(fig, "灰绿底纹为夜间 19:00-05:59。数据口径：2026 年正确数据，已剔除坐标异常，仅统计含时间记录。")

    fig.savefig(out_path, dpi=300, facecolor="white")
    plt.close(fig)
    return out_path


def draw_light_pollution_map(points: list[dict], zones: dict[str, list]) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "图4_光污染梯度地图.png"

    night_focus = {"Insecta", "Amphibia", "Mollusca", "Arachnida"}
    taxa_style = {
        "Insecta": ("昆虫", GREEN_MID, "o", 8),
        "Amphibia": ("两栖类", TEAL, "s", 12),
        "Mollusca": ("软体动物", "#4db6ac", "D", 10),
        "Arachnida": ("蛛形纲", "#9ccc65", "^", 10),
    }

    fig = plt.figure(figsize=(10.8, 7.2), facecolor="white")
    add_title(fig, "图 4  简化光污染梯度与夜行点位", "底图使用 OpenStreetMap 澳门陆地轮廓；右侧展示简化梯度统计。")
    gs = fig.add_gridspec(1, 2, left=0.04, right=0.96, top=0.84, bottom=0.14,
                          width_ratios=[1.42, 0.78], wspace=0.10)
    ax = fig.add_subplot(gs[0, 0])
    ax_panel = fig.add_subplot(gs[0, 1])
    ax_panel.axis("off")

    draw_clean_basemap(ax, zones)
    for taxon, (label, color, marker, size) in taxa_style.items():
        pts = [p for p in points if p["taxon"] == taxon and p["is_night"]]
        ax.scatter([p["lon"] for p in pts], [p["lat"] for p in pts],
                   s=size, color=color, marker=marker, alpha=0.72,
                   edgecolors="white", linewidth=0.25, label=f"{label} 夜间",
                   zorder=3)
    format_map_axis(ax)
    ax.legend(loc="lower right", frameon=True, facecolor="white",
              edgecolor="#d5ddd7", fontsize=8)

    for zone, meta in ZONE_META.items():
        ax.annotate(meta["label"], xy=meta["xy"], xytext=(meta["xy"][0], meta["xy"][1] + 0.006),
                    ha="center", fontsize=8.5, color=INK, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.18", facecolor="white",
                              edgecolor="#d8dfda", alpha=0.82))

    y = 0.86
    for zone in ["高光区", "中高光区", "相对低光区"]:
        meta = ZONE_META[zone]
        color = ZONE_COLORS[zone]
        rect = mpatches.FancyBboxPatch((0.02, y - 0.18), 0.94, 0.16,
                                       boxstyle="round,pad=0.015",
                                       facecolor="#fbfcfa", edgecolor=color,
                                       linewidth=1.8, transform=ax_panel.transAxes)
        ax_panel.add_patch(rect)
        ax_panel.text(0.07, y - 0.06, f"{meta['label']}\n{zone}",
                      transform=ax_panel.transAxes, fontsize=10.5,
                      fontweight="bold", color=INK, va="center")
        ax_panel.text(0.92, y - 0.06, f"{meta['night_pct']:.1f}%",
                      transform=ax_panel.transAxes, fontsize=19,
                      fontweight="bold", color=color, ha="right", va="center")
        ax_panel.text(0.92, y - 0.135, f"{meta['records']:,} 条 / {meta['species']:,} 种",
                      transform=ax_panel.transAxes, fontsize=8.5,
                      color=MUTED, ha="right", va="center")
        y -= 0.24
    ax_panel.text(0.02, 0.10, "夜行焦点类群 = 昆虫、两栖类、软体动物、蛛形纲。\n比例为夜间记录占该区域含时间焦点记录的比例。",
                  transform=ax_panel.transAxes, fontsize=8.7, color=MUTED,
                  linespacing=1.45)

    add_note(fig, "底图：OpenStreetMap/Nominatim 澳门陆地参考多边形；分区是简化光污染梯度，不等同于精确遥感灯光强度。数据口径：2026 年正确数据，已剔除坐标异常。")
    fig.savefig(out_path, dpi=300, facecolor="white")
    plt.close(fig)
    return out_path


def draw_invasive_species(points: list[dict], zones: dict[str, list]) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "图5_入侵物种预警点位.png"

    invasive_records: dict[str, list[dict]] = defaultdict(list)
    for p in points:
        if p["species"] in INVASIVE_SPECIES:
            invasive_records[p["species"]].append(p)

    fig = plt.figure(figsize=(11.2, 7.0), facecolor="white")
    add_title(fig, "图 5  重点入侵或外来物种早期预警", "点位代表观测记录，不代表完整分布范围或扩散速度。")
    gs = fig.add_gridspec(1, 2, left=0.04, right=0.96, top=0.84, bottom=0.14,
                          width_ratios=[1.35, 0.95], wspace=0.14)
    ax = fig.add_subplot(gs[0, 0])
    ax_cards = fig.add_subplot(gs[0, 1])
    ax_cards.axis("off")

    draw_clean_basemap(ax, zones)
    risk_colors = {"高": RED, "中": "#f07c18"}
    risk_markers = {"高": "X", "中": "D"}
    summary = []
    for sp, (cn_name, risk) in INVASIVE_SPECIES.items():
        recs = invasive_records.get(sp, [])
        color = risk_colors[risk]
        marker = risk_markers[risk]
        if recs:
            ax.scatter([r["lon"] for r in recs], [r["lat"] for r in recs],
                       s=28 if risk == "高" else 34, color=color, marker=marker,
                       edgecolors="white", linewidth=0.55, alpha=0.78, zorder=3,
                       label=f"{cn_name} ({len(recs)}条)")
        summary.append((cn_name, risk, len(recs), color))
    format_map_axis(ax)
    ax.legend(loc="lower right", frameon=True, facecolor="white",
              edgecolor="#d5ddd7", fontsize=7.6)

    ax_cards.text(0.02, 0.96, "预警清单", transform=ax_cards.transAxes,
                  fontsize=14, fontweight="bold", color=RED, va="top")
    y = 0.86
    for name, risk, cnt, color in summary:
        rect = mpatches.FancyBboxPatch((0.02, y - 0.13), 0.95, 0.115,
                                       boxstyle="round,pad=0.018",
                                       facecolor="#fffdfb", edgecolor=color,
                                       linewidth=1.8, transform=ax_cards.transAxes)
        ax_cards.add_patch(rect)
        ax_cards.text(0.07, y - 0.045, f"{risk}风险", transform=ax_cards.transAxes,
                      fontsize=8.5, color=color, fontweight="bold", va="center")
        ax_cards.text(0.07, y - 0.095, name, transform=ax_cards.transAxes,
                      fontsize=11.5, color=INK, fontweight="bold", va="center")
        ax_cards.text(0.90, y - 0.070, f"{cnt} 条", transform=ax_cards.transAxes,
                      fontsize=17, color=color, fontweight="bold", ha="right",
                      va="center")
        y -= 0.16

    add_note(fig, "底图：OpenStreetMap/Nominatim 澳门陆地参考多边形。清单物种：南美蟛蜞菊、长足捷蚁、红火蚁、温室蟾、新几内亚扁虫。数据口径：2026 年正确数据。")
    fig.savefig(out_path, dpi=300, facecolor="white")
    plt.close(fig)
    return out_path


def draw_venn(sp_2025: set[str], sp_2026: set[str]) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "图6_物种更替维恩图.png"

    shared = sp_2025 & sp_2026
    only_2025 = sp_2025 - sp_2026
    only_2026 = sp_2026 - sp_2025
    jaccard = len(shared) / len(sp_2025 | sp_2026) * 100

    fig, ax = plt.subplots(figsize=(7.4, 5.6), facecolor="white")
    fig.subplots_adjust(left=0.04, right=0.96, top=0.82, bottom=0.15)
    add_title(fig, "图 6  2025-2026 年物种更替", "“独有”仅表示该物种在当年数据中被记录，不代表真实出现或消失。")

    ax.set_xlim(-3.1, 3.1)
    ax.set_ylim(-2.1, 2.0)
    ax.set_aspect("equal")
    ax.axis("off")
    left = plt.Circle((-0.78, 0), 1.55, facecolor="#f4b663", alpha=0.42,
                      edgecolor=ORANGE, linewidth=2.2)
    right = plt.Circle((0.78, 0), 1.55, facecolor="#98c49d", alpha=0.50,
                       edgecolor=GREEN_MID, linewidth=2.2)
    ax.add_patch(left)
    ax.add_patch(right)
    ax.text(-1.48, 0.42, f"仅 2025\n{len(only_2025):,} 种", ha="center",
            fontsize=12.5, color="#c95212", fontweight="bold")
    ax.text(1.48, 0.42, f"仅 2026\n{len(only_2026):,} 种", ha="center",
            fontsize=12.5, color=GREEN_DARK, fontweight="bold")
    ax.text(0, -0.04, f"共有\n{len(shared):,} 种", ha="center",
            fontsize=14.5, color=INK, fontweight="bold")
    ax.text(0, -1.62, f"Jaccard 相似度  {jaccard:.1f}%", ha="center",
            fontsize=13, color=INK, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.35", facecolor="white",
                      edgecolor="#cdd5cf", linewidth=1.2))

    add_note(fig, "两年共有 1,399 种，Jaccard 相似度 39.0%。该图反映记录组成更替，不用于证明物种真实消失。")
    fig.savefig(out_path, dpi=300, facecolor="white")
    plt.close(fig)
    return out_path


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("正在加载数据...")
    summary_2025 = load_year_summary(DATA_2025)
    summary_2026 = load_year_summary(DATA_2026)
    t25 = load_taxon_counts(DATA_2025)
    t26 = load_taxon_counts(DATA_2026)
    counts_2026 = load_hourly_counts(DATA_2026)
    points_2026 = load_coordinates(DATA_2026)
    sp_2025 = load_species_set(DATA_2025)
    sp_2026 = load_species_set(DATA_2026)
    zones = load_macau_zones()

    print(f"  2025: {summary_2025['records']:,} 条, {summary_2025['species']:,} 种")
    print(f"  2026: {summary_2026['records']:,} 条, {summary_2026['species']:,} 种")
    print(f"  2026 坐标点: {len(points_2026)}")

    print("\n[图 1] 年度指标总览...")
    print(f"  OK {draw_year_comparison(summary_2025, summary_2026).relative_to(ROOT)}")

    print("[图 2] 类群结构变化...")
    print(f"  OK {draw_taxon_structure(t25, t26).relative_to(ROOT)}")

    print("[图 3] 24 小时昼夜节律环...")
    for taxon, label, _, _ in FOCUS:
        counter = counts_2026.get(taxon, Counter())
        print(f"  自检 {label}: 含时间记录={sum(counter.values())} "
              f"峰值={peak_hour(counter):02d}:00 夜间比例={night_percentage(counter)}%")
    print(f"  OK {draw_circadian_ring(counts_2026).relative_to(ROOT)}")

    print("[图 4] 光污染梯度地图...")
    print(f"  OK {draw_light_pollution_map(points_2026, zones).relative_to(ROOT)}")

    print("[图 5] 入侵物种预警...")
    print(f"  OK {draw_invasive_species(points_2026, zones).relative_to(ROOT)}")

    print("[图 6] 物种更替维恩图...")
    shared = len(sp_2025 & sp_2026)
    jaccard = shared / len(sp_2025 | sp_2026) * 100
    print(f"  共有物种: {shared:,}, Jaccard: {jaccard:.1f}%")
    print(f"  OK {draw_venn(sp_2025, sp_2026).relative_to(ROOT)}")

    print("\n全部 6 张图表已生成。")


if __name__ == "__main__":
    main()
