# -*- coding: utf-8 -*-
"""生成「澳门生态昼夜曲」A0 海报使用的主图。

本脚本只使用清理后的正确数据（`表格数据/正确数据/`），所有数值实算，
不引入任何手工填写的数字，避免海报出现「虚构」数据。

用法：
    python scripts/visualization/generate_poster_charts.py

当前已实现：
    图 3：焦点类群 24 小时昼夜节律环  ->  生态昼夜曲资料/图表/图3_24小时昼夜节律环.png

预留（待样图风格确认后补齐）：
    图 1 年度指标总览 / 图 2 类群结构 / 图 4 光污染梯度地图 / 图 5 入侵预警点位 / 维恩图
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
CLEAN_DIR = ROOT / "表格数据" / "正确数据"
DATA_2026 = CLEAN_DIR / "副本2026 團隊賽數據包_Sheet1.csv"
OUT_DIR = ROOT / "生态昼夜曲资料" / "图表"

# ----- 中文字体（微软雅黑），避免图中出现方块 -----
FONT_PATH = Path("C:/Windows/Fonts/msyh.ttc")
if FONT_PATH.exists():
    fm.fontManager.addfont(str(FONT_PATH))
    plt.rcParams["font.family"] = fm.FontProperties(fname=str(FONT_PATH)).get_name()
plt.rcParams["axes.unicode_minus"] = False

# ----- 主题配色：生物多样性 = 绿色系（植物绿）。三类群用可区分的三种绿 -----
GREEN_DARK = "#1b5e20"    # 主题深绿（标题、强调）
NIGHT_FILL = "#dfe7e0"    # 夜间扇区底纹：淡灰绿（不抢主体）
NIGHT_EDGE = "#9fb3a4"

# 三类群配色：嫩绿（日）→ 森林绿（全天）→ 深青绿（夜），都在绿色家族内
TAXON_COLORS = {
    "Aves": "#8bc34a",       # 鸟类：嫩绿/黄绿，呼应白天
    "Insecta": "#2e7d32",    # 昆虫：森林绿，全天主角
    "Amphibia": "#00695c",   # 两栖类：深青绿，呼应夜间
}

# 时间分箱口径（与 02_数据证据表 / 05_答辩 一致）
NIGHT_HOURS = {19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5}
DAWN_HOURS = {6, 7, 8}
DAY_HOURS = {9, 10, 11, 12, 13, 14, 15, 16}
DUSK_HOURS = {17, 18}

# 焦点类群：鸟类（日班）/ 昆虫（全天有回声）/ 两栖类（夜班）
FOCUS = [
    ("Aves", "鸟类", "日班"),
    ("Insecta", "昆虫", "全天"),
    ("Amphibia", "两栖类", "夜班"),
]


def load_hourly_counts(path: Path) -> dict[str, Counter]:
    """读取正确数据，返回 {iconic_taxon: Counter(hour -> 记录数)}。"""
    counts: dict[str, Counter] = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            taxon = (row.get("iconic_taxon_name") or "").strip()
            stamp = (row.get("time_observed_at") or "").strip()
            if not taxon or "T" not in stamp:
                continue
            hh = stamp.split("T", 1)[1][:2]
            if not hh.isdigit():
                continue
            hour = int(hh)
            if not 0 <= hour <= 23:
                continue
            counts.setdefault(taxon, Counter())[hour] += 1
    return counts


def night_percentage(counter: Counter) -> float:
    timed = sum(counter.values())
    if not timed:
        return 0.0
    night = sum(c for h, c in counter.items() if h in NIGHT_HOURS)
    return round(night / timed * 100, 1)


def peak_hour(counter: Counter) -> int:
    return max(counter, key=lambda h: counter[h]) if counter else 0


def draw_circadian_ring(counts: dict[str, Counter]) -> Path:
    """三类群叠加在同一个 24 小时环里：各类群按自身峰值归一化，
    便于在一张图上比较「活动时段」（鸟类日班 / 昆虫全天 / 两栖夜班）。"""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "图3_24小时昼夜节律环.png"

    # 24 个整点 + 闭合点；0:00 在正上方，顺时针（由 theta_zero=N + direction=-1 决定）
    hours = list(range(24))
    theta = np.deg2rad([h * 15 for h in hours])
    theta_closed = np.append(theta, theta[0])

    fig, ax = plt.subplots(figsize=(8.6, 9.4), subplot_kw={"projection": "polar"})
    fig.subplots_adjust(top=0.90, bottom=0.17)
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)

    # --- 夜间扇区底纹（19:00–05:59），标出「不夜城里的黑夜」---
    for h in NIGHT_HOURS:
        ax.bar(np.deg2rad(h * 15), 1.18, width=np.deg2rad(15),
               bottom=0, color=NIGHT_FILL, edgecolor="none", zorder=0)
    # 夜 / 昼 文字标记（0:00 在顶 = 夜；12:00 在底 = 昼）
    ax.text(np.deg2rad(0 * 15), 1.32, "夜", ha="center", va="center",
            fontsize=13, color=NIGHT_EDGE, fontweight="bold")
    ax.text(np.deg2rad(12 * 15), 1.32, "昼", ha="center", va="center",
            fontsize=13, color="#c9a227", fontweight="bold")

    # --- 三类群归一化节律曲线 + 填充 ---
    summary = []
    for taxon, label, tag in FOCUS:
        counter = counts.get(taxon, Counter())
        raw = np.array([counter.get(h, 0) for h in hours], dtype=float)
        peak = peak_hour(counter)
        night_pct = night_percentage(counter)
        norm = raw / raw.max() if raw.max() else raw
        norm_closed = np.append(norm, norm[0])
        color = TAXON_COLORS[taxon]

        ax.plot(theta_closed, norm_closed, color=color, linewidth=2.4,
                zorder=4, solid_joinstyle="round")
        ax.fill(theta_closed, norm_closed, color=color, alpha=0.18, zorder=2)
        # 峰值点标记
        ax.plot(np.deg2rad(peak * 15), norm[peak], "o", color=color,
                markersize=8, markeredgecolor="white", markeredgewidth=1.2, zorder=5)
        summary.append((label, tag, color, peak, night_pct, int(raw.sum())))

    # --- 坐标轴样式 ---
    ax.set_xticks(np.deg2rad([h * 15 for h in range(0, 24, 3)]))
    ax.set_xticklabels([f"{h}:00" for h in range(0, 24, 3)], fontsize=9.5)
    ax.set_yticks([0.5, 1.0])
    ax.set_yticklabels(["50%", "峰值"], fontsize=7.5, color="#888888")
    ax.set_ylim(0, 1.32)
    ax.grid(color="#cfd8cf", linewidth=0.6)
    ax.spines["polar"].set_visible(False)

    fig.suptitle("图 3　澳门生态昼夜曲：焦点类群的 24 小时记录节律",
                 fontsize=15.5, fontweight="bold", color=GREEN_DARK, y=0.95)

    # --- 图例（图形坐标，置于环下方，与脚注分开避免重叠）---
    handles = [
        plt.Line2D([0], [0], color=c, linewidth=3,
                   label=f"{lab}（{tag}）　峰值 {pk:02d}:00 ｜ 夜间 {ng}%　n={n}")
        for lab, tag, c, pk, ng, n in summary
    ]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.075),
               frameon=False, fontsize=10, handlelength=1.6, labelspacing=0.6)

    fig.text(0.5, 0.025,
             "各类群按自身峰值归一化，以便在同一张图比较活动时段（非记录绝对数量）；"
             "灰绿底纹为夜间 19:00–05:59。\n"
             "数据口径：2026 年澳门正确观测数据，已剔除坐标异常，仅统计含时间记录。",
             ha="center", fontsize=8, color="#555555")

    fig.savefig(out_path, dpi=300, facecolor="white")
    plt.close(fig)
    return out_path


def main() -> None:
    counts = load_hourly_counts(DATA_2026)

    # 自检：峰值小时与夜间比例应复现 02_数据证据表
    print("=== 图 3 自检（应与 02_数据证据表一致）===")
    for taxon, label, _ in FOCUS:
        counter = counts.get(taxon, Counter())
        print(
            f"  {label}: 含时间记录={sum(counter.values())} "
            f"峰值={peak_hour(counter):02d}:00 夜间比例={night_percentage(counter)}%"
        )

    out_path = draw_circadian_ring(counts)
    print(f"\n已生成：{out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
