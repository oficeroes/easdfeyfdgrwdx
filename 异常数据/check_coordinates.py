# -*- coding: utf-8 -*-
"""
澳门生物多样性数据坐标验证脚本
检测数据包中动植物记录的经纬度是否落在澳门陆地区域内，
找出落在海上（不合理）的坐标记录。
"""

import csv
import os
import json

# ============================================================
# 1. 定义澳门陆地边界多边形
# ============================================================
# 澳门由澳门半岛、氹仔、路环、路氹城（填海区）等组成
# 以下多边形坐标基于实际地理信息，考虑了填海扩展区域
# 坐标格式: [(lng, lat), (lng, lat), ...]

# --- 澳门半岛 (Macau Peninsula) ---
# 包括青洲、筷子基、新口岸、外港、港珠澳大桥人工岛等填海区
# 采用较宽松的边界以涵盖所有填海区域
MACAU_PENINSULA = [
    (113.5300, 22.2180),  # 西北角（跨境工业区/茂盛围）
    (113.5550, 22.2170),  # 北侧（关闸/边境）
    (113.5650, 22.2140),  # 东北（港珠澳大桥人工岛/新城A区）
    (113.5680, 22.2080),  # 东侧（友谊大桥起点）
    (113.5680, 22.2030),  # 东侧（外港填海区）
    (113.5680, 22.2000),  # 东南（新口岸/文化中心）
    (113.5650, 22.1950),  # 南侧（南湾湖）
    (113.5600, 22.1910),  # 南侧（西湾湖/妈阁）
    (113.5540, 22.1880),  # 南端（旅游塔附近）
    (113.5480, 22.1860),  # 西南（内港码头）
    (113.5400, 22.1860),  # 西侧
    (113.5350, 22.1880),  # 西侧
    (113.5310, 22.1920),  # 西侧
    (113.5290, 22.1970),  # 西侧（跨境工业区）
    (113.5290, 22.2050),  # 西侧
    (113.5300, 22.2120),  # 西北
    (113.5300, 22.2180),  # 闭合
]

# --- 氹仔 (Taipa) ---
# 包括机场、北安码头等填海区
TAIPA = [
    (113.5700, 22.1720),  # 东北（友谊大桥氹仔端）
    (113.5800, 22.1700),  # 东侧（机场/北安）
    (113.5820, 22.1650),  # 机场跑道
    (113.5800, 22.1580),  # 东南（机场南端）
    (113.5730, 22.1550),  # 南侧（路氹城边界/威尼斯人）
    (113.5650, 22.1540),  # 西南（路氹城/银河）
    (113.5600, 22.1550),  # 西侧
    (113.5530, 22.1570),  # 西北（嘉乐庇总督大桥）
    (113.5500, 22.1600),  # 西侧（海洋花园）
    (113.5500, 22.1650),  # 北侧
    (113.5540, 22.1690),  # 北侧
    (113.5600, 22.1710),  # 东北
    (113.5700, 22.1720),  # 闭合
]

# --- 路环 (Coloane) ---
# 包括九澳、黑沙、竹湾等
COLOANE = [
    (113.5730, 22.1420),  # 东北角
    (113.5850, 22.1400),  # 东侧（九澳）
    (113.5870, 22.1350),  # 东南（黑沙海滩）
    (113.5830, 22.1260),  # 南侧
    (113.5780, 22.1180),  # 西南（竹湾）
    (113.5700, 22.1140),  # 西南端
    (113.5600, 22.1140),  # 西侧
    (113.5540, 22.1180),  # 西侧
    (113.5520, 22.1240),  # 西北
    (113.5550, 22.1300),  # 北侧（路氹城边界）
    (113.5600, 22.1360),  # 北侧
    (113.5670, 22.1410),  # 东北
    (113.5730, 22.1420),  # 闭合
]

# --- 路氹城 (Cotai) 填海区 ---
# 连接氹仔和路环的大型填海区（赌场度假村集中区）
COTAI = [
    (113.5730, 22.1550),  # 北侧（氹仔边界/威尼斯人）
    (113.5780, 22.1530),  # 东北
    (113.5800, 22.1480),  # 东侧
    (113.5770, 22.1430),  # 东南
    (113.5700, 22.1410),  # 南侧（路环边界）
    (113.5620, 22.1400),  # 西南
    (113.5560, 22.1410),  # 西侧
    (113.5530, 22.1460),  # 西北
    (113.5550, 22.1520),  # 北侧
    (113.5620, 22.1540),  # 北侧
    (113.5730, 22.1550),  # 闭合
]

# --- 横琴澳大校区 (Hengqin UM Campus) ---
# 澳门大学横琴校区（通过河底隧道连接）
UM_CAMPUS = [
    (113.5400, 22.1330),
    (113.5530, 22.1330),
    (113.5530, 22.1220),
    (113.5400, 22.1220),
    (113.5400, 22.1330),
]

# 合并所有澳门陆地区域
MACAU_LAND_POLYGONS = [
    ("澳门半岛", MACAU_PENINSULA),
    ("氹仔", TAIPA),
    ("路环", COLOANE),
    ("路氹城", COTAI),
    ("横琴澳大校区", UM_CAMPUS),
]

# GPS 精度容差（约 200 米 ≈ 0.002 度）
# 考虑 GPS 误差以及澳门广泛的填海造地，给予较大容差
GPS_TOLERANCE = 0.002  # 约 200 米


# ============================================================
# 2. 射线法判断点是否在多边形内
# ============================================================
def point_in_polygon(lng, lat, polygon):
    """
    使用射线法（Ray Casting）判断点是否在多边形内部
    返回 True 表示点在多边形内
    """
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        # 检查射线是否与边相交
        if ((yi > lat) != (yj > lat)) and (lng < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def point_near_polygon(lng, lat, polygon, tolerance=GPS_TOLERANCE):
    """
    判断点是否在多边形内部或边缘容差范围内
    """
    # 先检查是否在多边形内
    if point_in_polygon(lng, lat, polygon):
        return True
    
    # 再检查是否在容差范围内的边缘附近
    n = len(polygon)
    for i in range(n):
        j = (i + 1) % n
        x1, y1 = polygon[i]
        x2, y2 = polygon[j]
        # 计算点到线段的最短距离
        dist = point_to_segment_distance(lng, lat, x1, y1, x2, y2)
        if dist <= tolerance:
            return True
    
    return False


def point_to_segment_distance(px, py, x1, y1, x2, y2):
    """计算点到线段的最短距离（单位：度）"""
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        # 线段退化为点
        return ((px - x1) ** 2 + (py - y1) ** 2) ** 0.5
    
    # 计算投影参数 t
    t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    # 投影点
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy
    return ((px - proj_x) ** 2 + (py - proj_y) ** 2) ** 0.5


def is_on_macau_land(lng, lat):
    """
    判断给定经纬度是否在澳门陆地区域内
    """
    for name, polygon in MACAU_LAND_POLYGONS:
        if point_near_polygon(lng, lat, polygon):
            return True, name
    return False, None


# ============================================================
# 3. 数据分析
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "表格数据")
OUTPUT_DIR = BASE_DIR

# 注意：2025年数据列顺序为 longitude, latitude（索引4,5）
# 2026年数据列顺序为 latitude, longitude（索引4,5）
DATASETS = {
    "2025": {
        "file": "2025 團隊賽數據包_Sheet1.csv",
        "lng_col": 4,
        "lat_col": 5,
    },
    "2026": {
        "file": "副本2026 團隊賽數據包_Sheet1.csv",
        "lng_col": 5,
        "lat_col": 4,
    },
}


def analyze_dataset(year, cfg):
    """分析单年数据集"""
    filepath = os.path.join(DATA_DIR, cfg["file"])
    lng_col = cfg["lng_col"]
    lat_col = cfg["lat_col"]
    
    total = 0
    on_land = 0
    on_sea = 0
    error_records = []
    
    # 用于统计每个区域的数量
    area_counts = {}
    
    # 用于统计海上点的分类
    sea_by_taxon = {}
    
    with open(filepath, encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)  # 跳过表头
        
        for row in reader:
            total += 1
            try:
                lng = float(row[lng_col])
                lat = float(row[lat_col])
            except (ValueError, IndexError):
                continue
            
            on_land_flag, area_name = is_on_macau_land(lng, lat)
            
            if on_land_flag:
                on_land += 1
                area_counts[area_name] = area_counts.get(area_name, 0) + 1
            else:
                on_sea += 1
                taxon = row[6] if len(row) > 6 else "未知"
                sea_by_taxon[taxon] = sea_by_taxon.get(taxon, 0) + 1
                
                error_records.append({
                    "id": row[0],
                    "observed_on": row[1],
                    "longitude": lng,
                    "latitude": lat,
                    "iconic_taxon_name": taxon,
                    "taxon_species_name": row[13] if len(row) > 13 else "",
                    "taxon_genus_name": row[12] if len(row) > 12 else "",
                    "captive_cultivated": row[3] if len(row) > 3 else "",
                    "full_data": row,
                })
    
    return {
        "total": total,
        "on_land": on_land,
        "on_sea": on_sea,
        "on_sea_pct": round(on_sea / total * 100, 2) if total > 0 else 0,
        "area_counts": area_counts,
        "sea_by_taxon": sea_by_taxon,
        "error_records": error_records,
    }


def export_errors_to_csv(year, error_records, header):
    """将错误记录导出为CSV"""
    output_path = os.path.join(OUTPUT_DIR, f"坐标异常数据_{year}.csv")
    
    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        # 写入表头
        writer.writerow([
            "id", "observed_on", "longitude", "latitude",
            "iconic_taxon_name", "taxon_species_name", "taxon_genus_name",
            "captive_cultivated", "问题说明"
        ])
        
        for rec in error_records:
            writer.writerow([
                rec["id"],
                rec["observed_on"],
                rec["longitude"],
                rec["latitude"],
                rec["iconic_taxon_name"],
                rec["taxon_species_name"],
                rec["taxon_genus_name"],
                rec["captive_cultivated"],
                f"坐标({rec['longitude']}, {rec['latitude']})不在澳门陆地区域内，疑似位于海上"
            ])
    
    return output_path


def export_detailed_errors_to_csv(year, error_records):
    """导出包含完整数据的详细错误CSV"""
    output_path = os.path.join(OUTPUT_DIR, f"坐标异常数据_{year}_详细版.csv")
    
    # 完整列名（基于2025年的列结构）
    columns = [
        "id", "observed_on", "time_observed_at", "captive_cultivated",
        "longitude", "latitude", "iconic_taxon_name",
        "taxon_kingdom_name", "taxon_phylum_name", "taxon_class_name",
        "taxon_order_name", "taxon_family_name", "taxon_genus_name",
        "taxon_species_name", "taxon_subspecies_name", "问题说明"
    ]
    
    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        
        for rec in error_records:
            row_data = rec["full_data"]
            # 确保经纬度使用正确的值
            out_row = list(row_data[:15])  # 取前15列
            # 补全可能缺失的列
            while len(out_row) < 15:
                out_row.append("")
            out_row.append(f"坐标({rec['longitude']}, {rec['latitude']})不在澳门陆地区域内，疑似位于海上")
            writer.writerow(out_row)
    
    return output_path


def main():
    print("=" * 60)
    print("澳门生物多样性数据 - 坐标合理性验证")
    print("=" * 60)
    print()
    
    # 打印澳门边界信息
    print("澳门陆地区域定义：")
    for name, polygon in MACAU_LAND_POLYGONS:
        lngs = [p[0] for p in polygon]
        lats = [p[1] for p in polygon]
        print(f"  {name}:")
        print(f"    经度范围: {min(lngs):.4f}° ~ {max(lngs):.4f}°")
        print(f"    纬度范围: {min(lats):.4f}° ~ {max(lats):.4f}°")
        print(f"    顶点数: {len(polygon)}")
    print(f"  GPS容差: ±{GPS_TOLERANCE}° (约 {GPS_TOLERANCE*111000:.0f} 米)")
    print()
    
    # 读取2025年数据表头以获取完整列名
    filepath_2025 = os.path.join(DATA_DIR, DATASETS["2025"]["file"])
    with open(filepath_2025, encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header_2025 = next(reader)
    
    all_results = {}
    
    for year in ["2025", "2026"]:
        print(f"\n{'=' * 60}")
        print(f"分析 {year} 年数据...")
        print(f"{'=' * 60}")
        
        cfg = DATASETS[year]
        result = analyze_dataset(year, cfg)
        all_results[year] = result
        
        print(f"  总记录数: {result['total']}")
        print(f"  陆地区域内: {result['on_land']} ({100 - result['on_sea_pct']:.2f}%)")
        print(f"  疑似海上（异常）: {result['on_sea']} ({result['on_sea_pct']:.2f}%)")
        print()
        print(f"  各区域记录分布:")
        for area, count in sorted(result['area_counts'].items(), key=lambda x: -x[1]):
            print(f"    {area}: {count} 条")
        print()
        print(f"  异常坐标按物种类型分布:")
        for taxon, count in sorted(result['sea_by_taxon'].items(), key=lambda x: -x[1]):
            print(f"    {taxon}: {count} 条")
        
        # 导出错误数据
        if result['error_records']:
            # 导出简洁版
            simple_path = export_errors_to_csv(year, result['error_records'], header_2025)
            print(f"\n  简洁版错误数据已导出: {simple_path}")
            
            # 导出详细版
            detailed_path = export_detailed_errors_to_csv(year, result['error_records'])
            print(f"  详细版错误数据已导出: {detailed_path}")
        
        # 显示前几条异常数据示例
        if result['error_records']:
            print(f"\n  前10条异常数据示例:")
            print(f"  {'ID':<12} {'经度':<12} {'纬度':<12} {'物种类型':<18} {'物种名'}")
            print(f"  {'-'*70}")
            for rec in result['error_records'][:10]:
                print(f"  {rec['id']:<12} {rec['longitude']:<12.5f} {rec['latitude']:<12.5f} {rec['iconic_taxon_name']:<18} {rec['taxon_species_name']}")
    
    # 生成汇总报告
    print(f"\n\n{'=' * 60}")
    print("汇总报告")
    print(f"{'=' * 60}")
    for year in ["2025", "2026"]:
        r = all_results[year]
        print(f"\n{year} 年:")
        print(f"  总计: {r['total']} | 正常: {r['on_land']} | 异常: {r['on_sea']} ({r['on_sea_pct']}%)")
    
    total_abnormal = sum(all_results[y]['on_sea'] for y in ["2025", "2026"])
    total_all = sum(all_results[y]['total'] for y in ["2025", "2026"])
    print(f"\n两年合计: {total_all} 条记录, 其中 {total_abnormal} 条异常 ({round(total_abnormal/total_all*100, 2)}%)")
    
    # 保存分析摘要JSON
    summary = {}
    for year in ["2025", "2026"]:
        r = all_results[year]
        summary[year] = {
            "总记录数": r["total"],
            "陆地区域内": r["on_land"],
            "异常记录数": r["on_sea"],
            "异常比例": f"{r['on_sea_pct']}%",
            "区域分布": r["area_counts"],
            "异常类型分布": r["sea_by_taxon"],
        }
    
    summary_path = os.path.join(OUTPUT_DIR, "坐标验证报告.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\n分析报告已保存: {summary_path}")


if __name__ == "__main__":
    main()
