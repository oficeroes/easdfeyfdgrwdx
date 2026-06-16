#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告数值验证脚本
验证「报告文档」中所有报告的关键数值是否与「正确数据」一致
"""

import csv
import json
import math
import os
from collections import Counter, defaultdict
from pathlib import Path

BASE_DIR = Path(r"d:\UserData\Desktop\生物多样性的比赛\Biodiversity_competition")

# ============================================================
# 1. 加载数据
# ============================================================

def load_csv(filepath):
    """加载CSV文件，返回行列表"""
    rows = []
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

print("=" * 70)
print("加载数据文件...")
print("=" * 70)

data_2025 = load_csv(BASE_DIR / "表格数据" / "正确数据" / "2025 團隊賽數據包_Sheet1.csv")
data_2026 = load_csv(BASE_DIR / "表格数据" / "正确数据" / "副本2026 團隊賽數據包_Sheet1.csv")

print(f"2025年正确数据: {len(data_2025)} 条")
print(f"2026年正确数据: {len(data_2026)} 条")

# ============================================================
# 2. 辅助函数
# ============================================================

def safe_float(v):
    try:
        return float(v) if v and v.strip() else None
    except (ValueError, TypeError):
        return None

def safe_int(v):
    try:
        return int(v) if v and v.strip() else None
    except (ValueError, TypeError):
        return None

def get_unique_species(rows):
    """获取独特物种学名集合"""
    species_set = set()
    for r in rows:
        sp = r.get('taxon_species_name', '').strip()
        if sp:
            species_set.add(sp)
    return species_set

def get_unique_values(rows, field):
    """获取某字段的唯一值集合"""
    return set(r.get(field, '').strip() for r in rows if r.get(field, '').strip())

def count_by_field(rows, field):
    """按字段统计记录数"""
    cnt = Counter()
    for r in rows:
        val = r.get(field, '').strip()
        if val:
            cnt[val] += 1
    return cnt

def species_frequency(rows):
    """计算物种频率分布"""
    species_counts = Counter()
    for r in rows:
        sp = r.get('taxon_species_name', '').strip()
        if sp:
            species_counts[sp] += 1
    return species_counts

def shannon_index(species_counts, N):
    """香农-维纳指数"""
    H = 0.0
    for n in species_counts.values():
        if n > 0:
            p = n / N
            H -= p * math.log(p)
    return H

def simpson_index(species_counts, N):
    """辛普森指数 D = sum(n_i*(n_i-1)) / (N*(N-1))"""
    if N <= 1:
        return 1.0
    sum_n = sum(n * (n - 1) for n in species_counts.values())
    D = sum_n / (N * (N - 1))
    return D

def pielou_evenness(H, S):
    """Pielou均匀度 J' = H' / ln(S)"""
    if S <= 1:
        return 1.0
    return H / math.log(S)

# ============================================================
# 3. 验证函数
# ============================================================

results = []  # 存储所有验证结果

def check(name, expected, actual, tolerance=0.01, is_float=False):
    """检查值是否匹配"""
    if is_float:
        match = abs(expected - actual) < tolerance
    else:
        match = (expected == actual)
    
    status = "✅" if match else "❌"
    if not match:
        detail = f"  期望={expected}  实际={actual}"
    else:
        detail = f"  = {actual}"
    
    results.append({
        'name': name, 'expected': expected, 'actual': actual,
        'match': match, 'source': ''
    })
    print(f"  {status} {name}: {detail}")
    return match

def check_approx(name, expected, actual, tolerance=0.01):
    """检查浮点数是否近似匹配"""
    return check(name, expected, actual, tolerance, is_float=True)

def check_in_range(name, expected, actual, margin=0.05):
    """检查百分比是否在容差范围内"""
    if expected == 0:
        match = actual == 0
    else:
        match = abs(actual - expected) / abs(expected) < margin
    status = "✅" if match else "❌"
    detail = f"  期望≈{expected}  实际={actual}" if not match else f"  期望≈{expected}  实际={actual}"
    results.append({
        'name': name, 'expected': expected, 'actual': actual,
        'match': match, 'source': ''
    })
    print(f"  {status} {name}: {detail}")
    return match

# ============================================================
# 4. 开始逐项验证
# ============================================================

print("\n")
print("=" * 70)
print("📊 验证：数据综合分析报告 & 生物多样性指数分析报告")
print("=" * 70)

# --- 2025年基本统计 ---
print("\n--- 2025年基本统计 ---")
N2025 = len(data_2025)
S2025 = len(get_unique_species(data_2025))
families_2025 = len(get_unique_values(data_2025, 'taxon_family_name'))
genera_2025 = len(get_unique_values(data_2025, 'taxon_genus_name'))

check("2025 总记录数 N", 33486, N2025)
check("2025 物种种数 S", 2979, S2025)
check("2025 科的数目", 605, families_2025)
check("2025 属的数目", 1869, genera_2025)

# 圈养/栽培
captive_2025 = sum(1 for r in data_2025 if r.get('captive_cultivated', '').strip().lower() == 'true')
wild_2025 = N2025 - captive_2025
check("2025 圈养/栽培记录", 5679, captive_2025)
check("2025 野生/自然记录", 27807, wild_2025)

# --- 2026年基本统计 ---
print("\n--- 2026年基本统计 ---")
N2026 = len(data_2026)
S2026 = len(get_unique_species(data_2026))
families_2026 = len(get_unique_values(data_2026, 'taxon_family_name'))
genera_2026 = len(get_unique_values(data_2026, 'taxon_genus_name'))

check("2026 总记录数 N", 18367, N2026)
check("2026 物种种数 S", 2009, S2026)
check("2026 科的数目", 517, families_2026)
check("2026 属的数目", 1473, genera_2026)

captive_2026 = sum(1 for r in data_2026 if r.get('captive_cultivated', '').strip().lower() == 'true')
check("2026 圈养/栽培记录", 0, captive_2026)

# 观测时间跨度
dates_2025 = [r.get('observed_on', '') for r in data_2025 if r.get('observed_on')]
dates_2026 = [r.get('observed_on', '') for r in data_2026 if r.get('observed_on')]
print(f"  2025观测日期范围: {min(dates_2025) if dates_2025 else 'N/A'} ~ {max(dates_2025) if dates_2025 else 'N/A'}")
print(f"  2026观测日期范围: {min(dates_2026) if dates_2026 else 'N/A'} ~ {max(dates_2026) if dates_2026 else 'N/A'}")

# --- 2025年类群分布 ---
print("\n--- 2025年 iconic_taxon_name 分布 ---")
taxon_counts_2025 = count_by_field(data_2025, 'iconic_taxon_name')
report_2025_taxon = {
    'Plantae': 25441, 'Aves': 3167, 'Insecta': 2929, 'Animalia': 380,
    'Actinopterygii': 324, 'Mollusca': 274, 'Reptilia': 252, 'Fungi': 246,
    'Amphibia': 206, 'Arachnida': 187, 'Mammalia': 73, 'Protozoa': 3
}
for taxon, expected in sorted(report_2025_taxon.items(), key=lambda x: -x[1]):
    actual = taxon_counts_2025.get(taxon, 0)
    check(f"2025 {taxon} 记录数", expected, actual)

# --- 2026年类群分布 ---
print("\n--- 2026年 iconic_taxon_name 分布 ---")
taxon_counts_2026 = count_by_field(data_2026, 'iconic_taxon_name')
report_2026_taxon = {
    'Plantae': 9736, 'Insecta': 3673, 'Aves': 3007, 'Animalia': 536,
    'Amphibia': 303, 'Mollusca': 273, 'Reptilia': 239, 'Arachnida': 212,
    'Actinopterygii': 177, 'Fungi': 152, 'Mammalia': 54, 'Protozoa': 4
}
for taxon, expected in sorted(report_2026_taxon.items(), key=lambda x: -x[1]):
    actual = taxon_counts_2026.get(taxon, 0)
    check(f"2026 {taxon} 记录数", expected, actual)

# 未分类
unclassified_2026 = sum(1 for r in data_2026 if not r.get('iconic_taxon_name', '').strip())
print(f"  2026 未分类记录数: {unclassified_2026}")

# --- 2026 各分类群百分比 ---
print("\n--- 2026年 各类群占比验证 ---")
pct_checks = [
    ('Plantae', 53.0), ('Insecta', 20.0), ('Aves', 16.4), ('Animalia', 2.9),
    ('Amphibia', 1.6), ('Mollusca', 1.5), ('Reptilia', 1.3), ('Arachnida', 1.2),
    ('Actinopterygii', 1.0), ('Fungi', 0.8), ('Mammalia', 0.3), ('Protozoa', '<0.1')
]
for taxon, expected_pct in pct_checks:
    actual_pct = (taxon_counts_2026.get(taxon, 0) / N2026) * 100
    if isinstance(expected_pct, str):
        print(f"  2026 {taxon} 占比: {actual_pct:.1f}% (报告: {expected_pct})")
    else:
        check_approx(f"2026 {taxon} 占比%", expected_pct, actual_pct, tolerance=0.2)

# --- 2025年界级别分布 ---
print("\n--- 2025年 界级别分布 ---")
kingdom_counts_2025 = count_by_field(data_2025, 'taxon_kingdom_name')
check("2025 Plantae 记录数", 25441, kingdom_counts_2025.get('Plantae', 0))
animalia_2025 = sum(v for k, v in kingdom_counts_2025.items() if k == 'Animalia')
check("2025 Animalia 记录数", 7792, animalia_2025)
check("2025 Fungi 记录数", 246, kingdom_counts_2025.get('Fungi', 0))

# --- 2026年界级别分布 ---
print("\n--- 2026年 界级别分布 ---")
kingdom_counts_2026 = count_by_field(data_2026, 'taxon_kingdom_name')
check("2026 Plantae 记录数", 9736, kingdom_counts_2026.get('Plantae', 0))
animalia_2026 = sum(v for k, v in kingdom_counts_2026.items() if k == 'Animalia')
check("2026 Animalia 记录数", 8474, animalia_2026)
check("2026 Fungi 记录数", 152, kingdom_counts_2026.get('Fungi', 0))
check("2026 Protozoa 记录数", 4, kingdom_counts_2026.get('Protozoa', 0))
check("2026 Bacteria 记录数", 1, kingdom_counts_2026.get('Bacteria', 0))

# ============================================================
# 5. 生物多样性指数验证
# ============================================================

print("\n")
print("=" * 70)
print("📊 验证：生物多样性指数 (Shannon, Simpson, Pielou)")
print("=" * 70)

sp_freq_2025 = species_frequency(data_2025)
sp_freq_2026 = species_frequency(data_2026)

# 2025
H_2025 = shannon_index(sp_freq_2025, N2025)
D_2025 = simpson_index(sp_freq_2025, N2025)
J_2025 = pielou_evenness(H_2025, S2025)
inv_D_2025 = 1.0 / D_2025 if D_2025 > 0 else float('inf')

print("\n--- 2025年指数 ---")
check_approx("2025 Shannon H' (报告: 6.7060)", 6.7060, H_2025, tolerance=0.001)
check_approx("2025 Simpson D (报告: 0.002623)", 0.002623, D_2025, tolerance=0.0001)
check_approx("2025 Simpson 1-D (报告: 0.997377)", 0.997377, 1-D_2025, tolerance=0.0001)
check_approx("2025 逆Simpson 1/D (报告: 381.19)", 381.19, inv_D_2025, tolerance=1.0)
check_approx("2025 Pielou J' (报告: 0.8383)", 0.8383, J_2025, tolerance=0.001)
check_approx("2025 H'max = ln(S) (报告: 7.9993)", 7.9993, math.log(S2025), tolerance=0.001)

# 2026
H_2026 = shannon_index(sp_freq_2026, N2026)
D_2026 = simpson_index(sp_freq_2026, N2026)
J_2026 = pielou_evenness(H_2026, S2026)
inv_D_2026 = 1.0 / D_2026 if D_2026 > 0 else float('inf')

print("\n--- 2026年指数 ---")
check_approx("2026 Shannon H' (报告: 6.4099)", 6.4099, H_2026, tolerance=0.001)
check_approx("2026 Simpson D (报告: 0.004212)", 0.004212, D_2026, tolerance=0.0001)
check_approx("2026 Simpson 1-D (报告: 0.995788)", 0.995788, 1-D_2026, tolerance=0.0001)
check_approx("2026 逆Simpson 1/D (报告: 237.42)", 237.42, inv_D_2026, tolerance=1.0)
check_approx("2026 Pielou J' (报告: 0.8428)", 0.8428, J_2026, tolerance=0.001)
check_approx("2026 H'max = ln(S) (报告: 7.6054)", 7.6054, math.log(S2026), tolerance=0.001)

# ============================================================
# 6. 2026年各分类群生物多样性指数
# ============================================================

print("\n")
print("=" * 70)
print("📊 验证：2026年各分类群生物多样性指数")
print("=" * 70)

# 报告中给出的各分类群指数
report_taxon_indices = {
    'Plantae':        {'records': 9736, 'S': 1074, 'H': 5.9835, 'D1': 0.9949, 'J': 0.8573},
    'Insecta':        {'records': 3673, 'S': 574,  'H': 5.4723, 'D1': 0.9923, 'J': 0.8614},
    'Aves':           {'records': 3007, 'S': 95,   'H': 3.0875, 'D1': 0.9234, 'J': 0.6780},
    'Fungi':          {'records': 152,  'S': 63,   'H': 3.6594, 'D1': 0.9621, 'J': 0.8832},
    'Arachnida':      {'records': 212,  'S': 58,   'H': 3.3136, 'D1': 0.9349, 'J': 0.8161},
    'Animalia':       {'records': 536,  'S': 38,   'H': 1.8609, 'D1': 0.7202, 'J': 0.5116},
    'Actinopterygii': {'records': 177,  'S': 38,   'H': 2.7101, 'D1': 0.8820, 'J': 0.7450},
    'Mollusca':       {'records': 273,  'S': 28,   'H': 2.2548, 'D1': 0.8380, 'J': 0.6767},
    'Reptilia':       {'records': 239,  'S': 20,   'H': 2.0944, 'D1': 0.8320, 'J': 0.6991},
    'Mammalia':       {'records': 54,   'S': 10,   'H': 1.7124, 'D1': 0.7470, 'J': 0.7437},
    'Amphibia':       {'records': 303,  'S': 7,    'H': 1.4224, 'D1': 0.6985, 'J': 0.7310},
    'Protozoa':       {'records': 4,    'S': 3,    'H': 1.0397, 'D1': 0.8333, 'J': 0.9464},
}

for taxon, expected_indices in report_taxon_indices.items():
    # 筛选该分类群的记录
    taxon_rows = [r for r in data_2026 if r.get('iconic_taxon_name', '').strip() == taxon]
    if not taxon_rows:
        print(f"  ⚠️ {taxon}: 无记录")
        continue
    
    n_taxon = len(taxon_rows)
    sp_taxon = len(get_unique_species(taxon_rows))
    sp_freq_taxon = species_frequency(taxon_rows)
    H_taxon = shannon_index(sp_freq_taxon, n_taxon)
    D_taxon = simpson_index(sp_freq_taxon, n_taxon)
    J_taxon = pielou_evenness(H_taxon, sp_taxon)
    
    print(f"\n  --- {taxon} ---")
    check(f"  {taxon} 记录数", expected_indices['records'], n_taxon)
    check(f"  {taxon} 物种数 S", expected_indices['S'], sp_taxon)
    check_approx(f"  {taxon} Shannon H'", expected_indices['H'], H_taxon, tolerance=0.001)
    check_approx(f"  {taxon} Simpson 1-D", expected_indices['D1'], 1-D_taxon, tolerance=0.001)
    check_approx(f"  {taxon} Pielou J'", expected_indices['J'], J_taxon, tolerance=0.001)

# ============================================================
# 7. 优势物种分析报告验证
# ============================================================

print("\n")
print("=" * 70)
print("📊 验证：优势物种分析报告")
print("=" * 70)

# Top 20 验证
sp_freq_2026_sorted = sp_freq_2026.most_common()

# 需要中文名对照
taxon_species_to_info = {}
for r in data_2026:
    sp = r.get('taxon_species_name', '').strip()
    if sp and sp not in taxon_species_to_info:
        taxon_species_to_info[sp] = {
            'iconic_taxon_name': r.get('iconic_taxon_name', '').strip(),
        }

print("\n--- Top 20 物种记录数验证 ---")
report_top20 = [
    ('Spilopelia chinensis', 484, 2.64), ('Passer montanus', 435, 2.37),
    ('Oxalis debilis', 324, 1.76), ('Pycnonotus jocosus', 246, 1.34),
    ('Copsychus saularis', 236, 1.28), ('Trigoniulus corallinus', 230, 1.25),
    ('Pycnonotus sinensis', 198, 1.08), ('Sphagneticola trilobata', 183, 1.00),
    ('Acridotheres cristatellus', 162, 0.88), ('Egretta garzetta', 162, 0.88),
    ('Helicorthomorpha holstii', 161, 0.88), ('Ficus microcarpa', 149, 0.81),
    ('Duttaphrynus melanostictus', 142, 0.77), ('Apis cerana', 137, 0.75),
    ('Pilea microphylla', 137, 0.75), ('Gallinula chloropus', 135, 0.74),
    ('Hyophila involuta', 133, 0.72), ('Gracupica nigricollis', 127, 0.69),
    ('Oxalis corniculata', 112, 0.61), ('Columba livia', 108, 0.59),
]

for sp_name, expected_count, expected_pct in report_top20:
    actual_count = sp_freq_2026.get(sp_name, 0)
    actual_pct = (actual_count / N2026) * 100
    check(f"Top20 {sp_name} 记录数", expected_count, actual_count)
    check_approx(f"Top20 {sp_name} 占比%", expected_pct, actual_pct, tolerance=0.05)

# Top20 合计
top20_total_expected = 4001
top20_total_actual = sum(sp_freq_2026.get(sp, 0) for sp, _, _ in report_top20)
check("Top20 合计记录数", top20_total_expected, top20_total_actual)
check_approx("Top20 占总记录%", 21.8, (top20_total_actual / N2026) * 100, tolerance=0.2)

# 检查实际 Top 20 排名
print("\n--- 实际 Top 20 物种 ---")
for i, (sp, cnt) in enumerate(sp_freq_2026_sorted[:20], 1):
    info = taxon_species_to_info.get(sp, {})
    taxon = info.get('iconic_taxon_name', '?')
    pct = (cnt / N2026) * 100
    print(f"  {i:2d}. {sp} ({taxon}): {cnt} ({pct:.2f}%)")

# --- 各分类群验证 ---
print("\n--- 各分类群优势种验证 ---")

def verify_taxon_group(taxon_name, report_species_list, report_total_species, report_total_records):
    """验证某个分类群的物种数和记录数，以及具体物种记录数"""
    taxon_rows = [r for r in data_2026 if r.get('iconic_taxon_name', '').strip() == taxon_name]
    actual_total = len(taxon_rows)
    actual_species = len(get_unique_species(taxon_rows))
    sp_freq = species_frequency(taxon_rows)
    
    print(f"\n  [{taxon_name}]")
    check(f"  {taxon_name} 总记录数", report_total_records, actual_total)
    check(f"  {taxon_name} 物种数", report_total_species, actual_species)
    
    for sp_name, expected_count, expected_pct in report_species_list:
        actual_count = sp_freq.get(sp_name, 0)
        actual_pct = (actual_count / actual_total * 100) if actual_total > 0 else 0
        check(f"  {taxon_name} {sp_name} 记录数", expected_count, actual_count)
        check_approx(f"  {taxon_name} {sp_name} 占比%", expected_pct, actual_pct, tolerance=0.2)
    
    return sp_freq

# 鸟类
birds_top10 = [
    ('Spilopelia chinensis', 484, 16.1), ('Passer montanus', 435, 14.5),
    ('Pycnonotus jocosus', 246, 8.2), ('Copsychus saularis', 236, 7.8),
    ('Pycnonotus sinensis', 198, 6.6), ('Acridotheres cristatellus', 162, 5.4),
    ('Egretta garzetta', 162, 5.4), ('Gallinula chloropus', 135, 4.5),
    ('Gracupica nigricollis', 127, 4.2), ('Columba livia', 108, 3.6),
]
verify_taxon_group('Aves', birds_top10, 95, 3007)

# 植物
plants_top10 = [
    ('Oxalis debilis', 324, 3.3), ('Sphagneticola trilobata', 183, 1.9),
    ('Ficus microcarpa', 149, 1.5), ('Pilea microphylla', 137, 1.4),
    ('Hyophila involuta', 133, 1.4), ('Oxalis corniculata', 112, 1.2),
    ('Lantana camara', 106, 1.1), ('Bidens alba', 103, 1.1),
    ('Emilia sonchifolia', 95, 1.0), ('Nelumbo nucifera', 91, 0.9),
]
verify_taxon_group('Plantae', plants_top10, 1074, 9736)

# 昆虫
insects_top10 = [
    ('Apis cerana', 137, 3.7), ('Cheilomenes sexmaculata', 83, 2.3),
    ('Delias pasithoe', 67, 1.8), ('Graphium sarpedon', 66, 1.8),
    ('Polyrhachis dives', 65, 1.8), ('Paratrechina longicornis', 60, 1.6),
    ('Trabala pallida', 60, 1.6), ('Periplaneta americana', 58, 1.6),
    ('Papilio polytes', 56, 1.5), ('Polyrhachis illaudata', 54, 1.5),
]
verify_taxon_group('Insecta', insects_top10, 574, 3673)

# 两栖类
amphibians_top7 = [
    ('Duttaphrynus melanostictus', 142, 46.9), ('Kaloula pulchra', 68, 22.4),
    ('Polypedates megacephalus', 47, 15.5), ('Eleutherodactylus planirostris', 27, 8.9),
    ('Microhyla fissipes', 10, 3.3), ('Hylarana guentheri', 8, 2.6),
    ('Hylarana taipehensis', 1, 0.3),
]
verify_taxon_group('Amphibia', amphibians_top7, 7, 303)

# ============================================================
# 8. 稀有物种分析报告验证
# ============================================================

print("\n")
print("=" * 70)
print("📊 验证：稀有物种分析报告")
print("=" * 70)

freq_dist = Counter(sp_freq_2026.values())
singletons = freq_dist.get(1, 0)
doubletons = freq_dist.get(2, 0)
three_to_five = sum(freq_dist.get(i, 0) for i in range(3, 6))
rare_le5 = sum(freq_dist.get(i, 0) for i in range(1, 6))
uncommon_6_20 = sum(freq_dist.get(i, 0) for i in range(6, 21))
common_gt20 = sum(freq_dist.get(i, 0) for i in range(21, max(freq_dist.keys()) + 1))

print(f"\n  总物种数: {S2026}")
print(f"  Singletons(1次): {singletons} (占 {singletons/S2026*100:.1f}%)")
print(f"  Doubletons(2次): {doubletons} (占 {doubletons/S2026*100:.1f}%)")
print(f"  3-5次: {three_to_five} (占 {three_to_five/S2026*100:.1f}%)")
print(f"  稀有(≤5次): {rare_le5} (占 {rare_le5/S2026*100:.1f}%)")
print(f"  少见(6-20次): {uncommon_6_20} (占 {uncommon_6_20/S2026*100:.1f}%)")
print(f"  常见(>20次): {common_gt20} (占 {common_gt20/S2026*100:.1f}%)")

check("Singletons 数量", 720, singletons)
check("Doubletons 数量", 322, doubletons)
check("3-5次记录物种数", 384, three_to_five)
check("稀有物种 ≤5次", 1426, rare_le5)
check("少见物种 6-20次", 376, uncommon_6_20)
check("常见物种 >20次", 207, common_gt20)

# 验证百分比
check_approx("Singletons 占比%", 35.8, singletons/S2026*100, tolerance=0.2)
check_approx("Doubletons 占比%", 16.0, doubletons/S2026*100, tolerance=0.2)
check_approx("稀有物种 ≤5次 占比%", 71.0, rare_le5/S2026*100, tolerance=0.3)

# --- 各分类群稀有物种分布 ---
print("\n--- 各分类群稀有物种分布验证 ---")
report_rare_by_taxon = {
    'Plantae':        (1074, 338, 728, 67.8),
    'Insecta':        (574,  217, 428, 74.6),
    'Aves':           (95,   32,  53,  55.8),
    'Animalia':       (38,   18,  30,  78.9),
    'Amphibia':       (7,    1,   1,   14.3),
    'Mollusca':       (28,   15,  20,  71.4),
    'Reptilia':       (20,   7,   13,  65.0),
    'Arachnida':      (58,   30,  51,  87.9),
    'Actinopterygii': (38,   18,  33,  86.8),
    'Fungi':          (63,   38,  58,  92.1),
    'Mammalia':       (10,   3,   7,   70.0),
    'Protozoa':       (3,    2,   3,   100.0),
}

for taxon, (exp_S, exp_sing, exp_rare, exp_pct) in report_rare_by_taxon.items():
    taxon_rows = [r for r in data_2026 if r.get('iconic_taxon_name', '').strip() == taxon]
    taxon_sp_freq = species_frequency(taxon_rows)
    taxon_S = len(taxon_sp_freq)
    taxon_sing = sum(1 for v in taxon_sp_freq.values() if v == 1)
    taxon_rare = sum(1 for v in taxon_sp_freq.values() if v <= 5)
    taxon_pct = (taxon_rare / taxon_S * 100) if taxon_S > 0 else 0
    
    print(f"\n  [{taxon}]")
    check(f"  {taxon} 总物种数", exp_S, taxon_S)
    check(f"  {taxon} Singletons", exp_sing, taxon_sing)
    check(f"  {taxon} 稀有≤5次", exp_rare, taxon_rare)
    check_approx(f"  {taxon} 稀有比例%", exp_pct, taxon_pct, tolerance=0.5)

# ============================================================
# 9. 生态指示物种分析报告验证
# ============================================================

print("\n")
print("=" * 70)
print("📊 验证：生态指示物种分析报告")
print("=" * 70)

indicator_species = {
    # 水鸟
    'Egretta garzetta': 162,    # 小白鹭
    'Gallinula chloropus': 135,  # 黑水鸡
    'Ardeola bacchus': 39,       # 池鹭
    'Ardea alba': 29,            # 大白鹭
    'Nycticorax nycticorax': 25, # 夜鹭
    'Actitis hypoleucos': 4,     # 矶鹬
    # 森林鸟类
    'Pycnonotus sinensis': 198,  # 白头鹎
    'Pycnonotus jocosus': 246,   # 红耳鹎
    'Orthotomus sutorius': 13,   # 长尾缝叶莺
    'Zosterops simplex': 21,     # 暗绿绣眼鸟
    'Garrulax canorus': 44,      # 画眉
    # 榕树
    'Ficus microcarpa': 149,     # 细叶榕
    'Ficus rumphii': 39,         # 心叶榕
    # 入侵物种
    'Sphagneticola trilobata': 183,    # 南美蟛蜞菊
    'Anoplolepis gracilipes': 27,      # 长足捷蚁
    'Eleutherodactylus planirostris': 27, # 温室蟾
    'Solenopsis invicta': 7,           # 红火蚁
    'Platydemus manokwari': 7,         # 新几内亚扁虫
    # 城市适应
    'Spilopelia chinensis': 484,       # 珠颈斑鸠
    'Passer montanus': 435,            # 麻雀
    'Copsychus saularis': 236,         # 鹊鸲
    'Acridotheres cristatellus': 162,  # 八哥
    'Columba livia': 108,              # 原鸽
}

print("\n--- 生态指示物种记录数验证 ---")
for sp_name, expected_count in indicator_species.items():
    actual_count = sp_freq_2026.get(sp_name, 0)
    check(f"  {sp_name} 记录数", expected_count, actual_count)

# 验证组合统计
print("\n--- 组合统计验证 ---")
# 珠颈斑鸠+麻雀 = 919
check("珠颈斑鸠+麻雀合计", 919, sp_freq_2026.get('Spilopelia chinensis', 0) + sp_freq_2026.get('Passer montanus', 0))
# 小白鹭+黑水鸡 = 297
check("小白鹭+黑水鸡合计", 297, sp_freq_2026.get('Egretta garzetta', 0) + sp_freq_2026.get('Gallinula chloropus', 0))

# 两栖类
amphib_sp_freq = species_frequency([r for r in data_2026 if r.get('iconic_taxon_name', '').strip() == 'Amphibia'])
check("两栖类总记录数", 303, sum(amphib_sp_freq.values()))
check("两栖类物种数", 7, len(amphib_sp_freq))

# ============================================================
# 10. 十大选题报告中的数据引用的验证
# ============================================================

print("\n")
print("=" * 70)
print("📊 验证：十大选题深度分析报告中引用的数据")
print("=" * 70)

# 2025年占比
pct_plant_2025 = taxon_counts_2025.get('Plantae', 0) / N2025 * 100
pct_aves_2025 = taxon_counts_2025.get('Aves', 0) / N2025 * 100
pct_insecta_2025 = taxon_counts_2025.get('Insecta', 0) / N2025 * 100
pct_captive_2025 = captive_2025 / N2025 * 100

check_approx("2025植物占比% (报告: 76.0%)", 76.0, pct_plant_2025, tolerance=0.2)
check_approx("2025动物界占比% (报告: 23.3%)", 23.3, animalia_2025/N2025*100, tolerance=0.2)
check_approx("2025圈养/栽培占比% (报告: 17.0%)", 17.0, pct_captive_2025, tolerance=0.2)

# 2026年占比
pct_plant_2026 = taxon_counts_2026.get('Plantae', 0) / N2026 * 100
pct_insecta_2026 = taxon_counts_2026.get('Insecta', 0) / N2026 * 100
pct_aves_2026 = taxon_counts_2026.get('Aves', 0) / N2026 * 100

check_approx("2026昆虫占比% (报告: 20.0%)", 20.0, pct_insecta_2026, tolerance=0.2)
check_approx("2026鸟类占比% (报告: 16.4%)", 16.4, pct_aves_2026, tolerance=0.2)

# 两年共有物种
species_2025_set = get_unique_species(data_2025)
species_2026_set = get_unique_species(data_2026)
shared = species_2025_set & species_2026_set
only_2025 = species_2025_set - species_2026_set
only_2026 = species_2026_set - species_2025_set
jaccard = len(shared) / len(species_2025_set | species_2026_set)

print(f"\n  共有物种: {len(shared)}")
print(f"  仅2025: {len(only_2025)}")
print(f"  仅2026: {len(only_2026)}")
print(f"  Jaccard相似度: {jaccard:.4f}")

check("共有物种数", 1399, len(shared))
check("仅2025独有物种", 1580, len(only_2025))
check("仅2026独有物种", 610, len(only_2026))
check_approx("共有物种/2025物种数", 47.0, len(shared)/S2025*100, tolerance=0.3)
check_approx("共有物种/2026物种数", 69.6, len(shared)/S2026*100, tolerance=0.3)
check_approx("Jaccard相似度%", 39.0, jaccard*100, tolerance=0.5)

# 入侵物种两年合计
print("\n--- 入侵物种两年合计 ---")
inv_species_report = {
    'Sphagneticola trilobata': 386,
    'Anoplolepis gracilipes': 85,
    'Solenopsis invicta': 17,
    'Platydemus manokwari': 11,
    'Eleutherodactylus planirostris': 36,
}
sp_freq_2025 = species_frequency(data_2025)
for sp, expected_total in inv_species_report.items():
    actual_total = sp_freq_2025.get(sp, 0) + sp_freq_2026.get(sp, 0)
    check(f"  {sp} 两年合计", expected_total, actual_total)

# ============================================================
# 11. 区域分布验证（引用坐标验证报告中的数据）
# ============================================================

print("\n")
print("=" * 70)
print("📊 验证：区域分布（参照坐标验证报告）")
print("=" * 70)

# 从坐标验证报告读取
with open(BASE_DIR / "异常数据" / "坐标验证报告.json", 'r', encoding='utf-8') as f:
    coord_report = json.load(f)

region_2026 = coord_report['数据集']['2026']['区域分布']
# 合并边界容差内记录
region_normalized = {
    '澳门半岛': region_2026.get('澳门半岛', 0) + region_2026.get('澳门半岛边界容差内', 0),
    '氹仔': region_2026.get('氹仔', 0) + region_2026.get('氹仔边界容差内', 0),
    '路环': region_2026.get('路环', 0) + region_2026.get('路环边界容差内', 0),
    '路氹城': region_2026.get('路氹城', 0) + region_2026.get('路氹城边界容差内', 0),
    '横琴澳大校区': region_2026.get('横琴澳大校区', 0) + region_2026.get('横琴澳大校区边界容差内', 0),
    '新城A区': region_2026.get('新城A区', 0) + region_2026.get('新城A区边界容差内', 0),
}

report_region = {
    '澳门半岛': 8489, '氹仔': 5006, '路环': 4309,
    '路氹城': 509, '横琴澳大校区': 51, '新城A区': 3,
}

print("\n  区域分布（含边界容差内）：")
for region, expected in report_region.items():
    actual = region_normalized.get(region, 0)
    check(f"  2026 {region} 记录数", expected, actual)

# ============================================================
# 12. 2025 vs 2026 对比验证
# ============================================================

print("\n")
print("=" * 70)
print("📊 验证：2025 vs 2026 对比数据")
print("=" * 70)

# 动物界记录变化
check("2025 Animalia 记录数", 7792, animalia_2025)
check("2026 Animalia 记录数", 8474, animalia_2026)
change_pct = (animalia_2026 - animalia_2025) / animalia_2025 * 100
check_approx("动物界记录变化% (报告: +8.8%)", 8.8, change_pct, tolerance=0.3)

# 2025年优势科 Top 10
print("\n--- 2025年优势科 Top 10 ---")
family_counts_2025 = count_by_field(data_2025, 'taxon_family_name')
report_families_2025 = [
    ('Asparagaceae', 1337), ('Asteraceae', 1319), ('Euphorbiaceae', 1226),
    ('Moraceae', 1141), ('Poaceae', 1101), ('Apocynaceae', 1026),
    ('Malvaceae', 938), ('Rubiaceae', 936), ('Fabaceae', 860), ('Arecaceae', 749),
]
for family, expected in report_families_2025:
    actual = family_counts_2025.get(family, 0)
    check(f"2025 {family} 记录数", expected, actual)

# 2026年优势科 Top 10
print("\n--- 2026年优势科 Top 10 ---")
family_counts_2026 = count_by_field(data_2026, 'taxon_family_name')
report_families_2026 = [
    ('Asteraceae', 779), ('Moraceae', 618), ('Columbidae', 592),
    ('Poaceae', 541), ('Pycnonotidae', 461), ('Oxalidaceae', 449),
    ('Passeridae', 435), ('Rubiaceae', 432), ('Fabaceae', 422), ('Formicidae', 418),
]
for family, expected in report_families_2026:
    actual = family_counts_2026.get(family, 0)
    check(f"2026 {family} 记录数", expected, actual)

# 时间缺失统计
time_missing_2025 = sum(1 for r in data_2025 if not r.get('time_observed_at', '').strip())
time_missing_2026 = sum(1 for r in data_2026 if not r.get('time_observed_at', '').strip())
print(f"\n  2025 time_observed_at 缺失: {time_missing_2025} ({time_missing_2025/N2025*100:.1f}%)")
print(f"  2026 time_observed_at 缺失: {time_missing_2026} ({time_missing_2026/N2026*100:.1f}%)")
check("2025 time_observed_at 缺失数 (报告: 402)", 402, time_missing_2025)
check("2026 time_observed_at 缺失数 (报告: 327)", 327, time_missing_2026)

# ============================================================
# 13. 汇总报告
# ============================================================

print("\n")
print("=" * 70)
print("📊 验证汇总")
print("=" * 70)

total_checks = len(results)
passed = sum(1 for r in results if r['match'])
failed = sum(1 for r in results if not r['match'])

print(f"\n  总验证项: {total_checks}")
print(f"  ✅ 通过: {passed}")
print(f"  ❌ 未通过: {failed}")
print(f"  通过率: {passed/total_checks*100:.1f}%")

if failed > 0:
    print(f"\n  ❌ 未通过的项目：")
    for r in results:
        if not r['match']:
            print(f"    - {r['name']}: 期望={r['expected']}, 实际={r['actual']}")
else:
    print(f"\n  🎉 所有验证项均通过！")

# 保存详细报告
report_path = BASE_DIR / "报告文档" / "数值验证报告.json"
with open(report_path, 'w', encoding='utf-8') as f:
    json.dump({
        'verification_date': '2026-06-16',
        'total_checks': total_checks,
        'passed': passed,
        'failed': failed,
        'pass_rate': f"{passed/total_checks*100:.1f}%",
        'details': [{
            'name': r['name'],
            'expected': str(r['expected']),
            'actual': str(r['actual']),
            'match': r['match']
        } for r in results]
    }, f, ensure_ascii=False, indent=2)

print(f"\n详细验证报告已保存至: {report_path}")
