# -*- coding: utf-8 -*-
"""读取表格数据中的 2025 / 2026 CSV，提取经纬度与物种类别，生成供网页热点图使用的 热点图数据.js"""
import csv, json, os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "表格数据")

# 数据集配置：注意两年的经纬度列顺序不同
DATASETS = {
    "2025": {"file": "2025 團隊賽數據包_Sheet1.csv", "lat": 5, "lng": 4},
    "2026": {"file": "副本2026 團隊賽數據包_Sheet1.csv", "lat": 4, "lng": 5},
}

# iconic_taxon_name -> 中文名（用于图例 / 筛选）
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

# 固定类别顺序（保证两年索引一致）
CATEGORIES = list(CAT_LABELS.keys())
CAT_INDEX = {c: i for i, c in enumerate(CATEGORIES)}


def load(cfg):
    points = []
    counts = {}
    path = os.path.join(DATA_DIR, cfg["file"])
    with open(path, encoding="utf-8-sig") as fh:
        r = csv.reader(fh)
        next(r)  # 跳过表头
        for row in r:
            try:
                lat = round(float(row[cfg["lat"]]), 5)
                lng = round(float(row[cfg["lng"]]), 5)
            except (ValueError, IndexError):
                continue
            cat = row[6] if len(row) > 6 else ""
            if cat not in CAT_INDEX:
                cat = ""
            ci = CAT_INDEX[cat]
            points.append([lat, lng, ci])
            counts[cat] = counts.get(cat, 0) + 1
    return points, counts


def main():
    out = {
        "categories": [{"key": c, "label": CAT_LABELS[c], "index": i}
                       for i, c in enumerate(CATEGORIES)],
        "years": {},
    }
    for year, cfg in DATASETS.items():
        pts, counts = load(cfg)
        out["years"][year] = {
            "points": pts,
            "total": len(pts),
            "counts": {CAT_INDEX[k]: v for k, v in counts.items()},
        }
        print(f"{year}: {len(pts)} 条有效记录")

    js = "// 自动生成，请勿手动编辑。运行 生成热点图数据.py 重新生成。\n"
    js += "window.HEATMAP_DATA = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n"
    out_path = os.path.join(BASE, "热点图数据.js")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(js)
    size = os.path.getsize(out_path) / 1024 / 1024
    print(f"已生成 {out_path}（{size:.2f} MB）")


if __name__ == "__main__":
    main()
