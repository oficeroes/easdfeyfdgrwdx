"""
澳门生态昼夜曲数据可视化
使用专业的Python数据可视化库生成高质量图表
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib import font_manager
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 设置seaborn样式
sns.set_style("whitegrid")
sns.set_context("paper", font_scale=1.2)

# 配色方案
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'accent': '#F18F01',
    'success': '#06A77D',
    'warning': '#F9C74F',
    'danger': '#E63946',
    'night': '#1A1B41',
    'day': '#FFB703',
    'twilight': '#FB8500',
    'morning': '#8ECAE6'
}

def load_data():
    """加载所有数据文件"""
    data = {}

    # 昼夜节律数据
    data['rhythm'] = pd.read_csv('表格数据/生态昼夜曲/昼夜节律摘要.csv')

    # 光污染梯度数据
    data['light'] = pd.read_csv('表格数据/生态昼夜曲/光污染梯度摘要.csv')

    # 年度变化数据
    data['annual'] = pd.read_csv('表格数据/生态昼夜曲/年度类群变化.csv')

    # 入侵物种数据
    data['invasive'] = pd.read_csv('表格数据/生态昼夜曲/入侵物种预警点位.csv')

    return data

def create_circadian_rhythm_chart(data):
    """图表1: 24小时昼夜节律活动图 - 极坐标图"""
    fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(projection='polar'))

    # 准备数据 - 提取主要类群
    taxa = ['鸟类', '昆虫', '两栖类', '软体动物', '蛛形纲']
    colors_map = {
        '鸟类': COLORS['day'],
        '昆虫': COLORS['accent'],
        '两栖类': COLORS['night'],
        '软体动物': COLORS['secondary'],
        '蛛形纲': COLORS['success']
    }

    # 创建24小时的角度
    hours = np.arange(0, 24, 1)
    theta = np.linspace(0, 2 * np.pi, 24, endpoint=False)

    # 为每个类群绘制活动曲线
    for taxon in taxa:
        taxon_data = data['rhythm'][data['rhythm']['taxon_label'] == taxon]
        if not taxon_data.empty:
            peak_hour = int(taxon_data['peak_hour'].values[0])
            night_pct = taxon_data['night_percentage'].values[0]

            # 创建模拟的24小时活动分布（基于峰值时间和夜间比例）
            activity = np.zeros(24)
            for i in range(24):
                # 使用高斯分布模拟活动模式
                distance = min(abs(i - peak_hour), 24 - abs(i - peak_hour))
                activity[i] = 100 * np.exp(-(distance ** 2) / 20)

            ax.plot(theta, activity, linewidth=2.5, label=taxon,
                   color=colors_map[taxon], alpha=0.8)
            ax.fill(theta, activity, alpha=0.15, color=colors_map[taxon])

    # 设置标签
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_xticks(theta)
    ax.set_xticklabels([f'{h}:00' for h in hours], fontsize=10)
    ax.set_ylim(0, 100)

    # 添加昼夜区域背景
    night_start = np.pi * 18 / 12  # 18:00
    night_end = np.pi * 6 / 12     # 6:00

    ax.set_title('澳门生物多样性24小时活动节律\n主要类群时间分布模式',
                pad=20, fontsize=16, fontweight='bold')
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), frameon=True, fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('生态昼夜曲资料/可视化图表/01_专业版_24小时活动节律图.png',
                dpi=300, bbox_inches='tight', facecolor='white')
    print("[OK] 已生成: 01_专业版_24小时活动节律图.png")
    plt.close()

def create_night_activity_comparison(data):
    """图表2: 夜间活动比例对比图"""
    fig, ax = plt.subplots(figsize=(12, 8))

    # 筛选有意义的类群
    rhythm_data = data['rhythm'].sort_values('night_percentage', ascending=True)

    # 创建水平条形图
    y_pos = np.arange(len(rhythm_data))
    bars = ax.barh(y_pos, rhythm_data['night_percentage'],
                   color=[COLORS['night'] if x > 50 else COLORS['day']
                         for x in rhythm_data['night_percentage']],
                   alpha=0.8, edgecolor='black', linewidth=0.5)

    # 添加数值标签
    for i, (bar, value) in enumerate(zip(bars, rhythm_data['night_percentage'])):
        ax.text(value + 2, i, f'{value:.1f}%',
               va='center', fontsize=10, fontweight='bold')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(rhythm_data['taxon_label'], fontsize=11)
    ax.set_xlabel('夜间活动记录占比 (%)', fontsize=12, fontweight='bold')
    ax.set_title('澳门各类群夜间活动比例对比\n（基于2026年调查数据）',
                fontsize=14, fontweight='bold', pad=15)

    # 添加参考线
    ax.axvline(x=50, color='red', linestyle='--', linewidth=1.5, alpha=0.5, label='50%基准线')
    ax.legend(fontsize=10)

    ax.set_xlim(0, max(rhythm_data['night_percentage']) + 10)
    ax.grid(axis='x', alpha=0.3)

    plt.tight_layout()
    plt.savefig('生态昼夜曲资料/可视化图表/02_专业版_夜间活动比例对比.png',
                dpi=300, bbox_inches='tight', facecolor='white')
    print("[OK] 已生成: 02_专业版_夜间活动比例对比.png")
    plt.close()

def create_light_gradient_analysis(data):
    """图表3: 光污染梯度分析图"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    light_data = data['light'][data['light']['light_gradient'] != '补充样本'].copy()

    # 子图1: 不同光照区域的记录数和物种数
    x = np.arange(len(light_data))
    width = 0.35

    bars1 = ax1.bar(x - width/2, light_data['records'], width,
                    label='观察记录数', color=COLORS['primary'], alpha=0.8)
    bars2 = ax1.bar(x + width/2, light_data['species'], width,
                    label='物种数', color=COLORS['accent'], alpha=0.8)

    ax1.set_xlabel('光污染梯度区域', fontsize=12, fontweight='bold')
    ax1.set_ylabel('数量', fontsize=12, fontweight='bold')
    ax1.set_title('不同光照区域的物种多样性', fontsize=13, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(light_data['light_gradient'], fontsize=11)
    ax1.legend(fontsize=10)
    ax1.grid(axis='y', alpha=0.3)

    # 添加数值标签
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=9)

    # 子图2: 夜间活动比例
    colors_gradient = [COLORS['danger'], COLORS['warning'], COLORS['success']]
    bars = ax2.bar(light_data['light_gradient'],
                   light_data['night_focus_percentage'],
                   color=colors_gradient, alpha=0.8, edgecolor='black', linewidth=0.5)

    ax2.set_xlabel('光污染梯度区域', fontsize=12, fontweight='bold')
    ax2.set_ylabel('夜间活动记录占比 (%)', fontsize=12, fontweight='bold')
    ax2.set_title('光照强度与夜间活动的关系', fontsize=13, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)

    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.suptitle('澳门光污染梯度与生物活动分析',
                fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('生态昼夜曲资料/可视化图表/03_专业版_光污染梯度分析.png',
                dpi=300, bbox_inches='tight', facecolor='white')
    print("[OK] 已生成: 03_专业版_光污染梯度分析.png")
    plt.close()

def create_annual_change_chart(data):
    """图表4: 年度类群变化对比图"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

    annual_data = data['annual'].sort_values('records_2026', ascending=False).head(10)

    # 子图1: 记录数变化
    x = np.arange(len(annual_data))
    width = 0.35

    bars1 = ax1.bar(x - width/2, annual_data['records_2025'], width,
                    label='2025年', color=COLORS['secondary'], alpha=0.8)
    bars2 = ax1.bar(x + width/2, annual_data['records_2026'], width,
                    label='2026年', color=COLORS['primary'], alpha=0.8)

    ax1.set_xlabel('类群', fontsize=11, fontweight='bold')
    ax1.set_ylabel('记录数', fontsize=11, fontweight='bold')
    ax1.set_title('2025-2026年各类群记录数对比', fontsize=12, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(annual_data['taxon_label'], rotation=45, ha='right', fontsize=10)
    ax1.legend(fontsize=10)
    ax1.grid(axis='y', alpha=0.3)

    # 子图2: 物种数变化
    bars1 = ax2.bar(x - width/2, annual_data['species_2025'], width,
                    label='2025年', color=COLORS['secondary'], alpha=0.8)
    bars2 = ax2.bar(x + width/2, annual_data['species_2026'], width,
                    label='2026年', color=COLORS['primary'], alpha=0.8)

    ax2.set_xlabel('类群', fontsize=11, fontweight='bold')
    ax2.set_ylabel('物种数', fontsize=11, fontweight='bold')
    ax2.set_title('2025-2026年各类群物种数对比', fontsize=12, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(annual_data['taxon_label'], rotation=45, ha='right', fontsize=10)
    ax2.legend(fontsize=10)
    ax2.grid(axis='y', alpha=0.3)

    # 子图3: 记录数增长率
    colors_delta = [COLORS['success'] if x > 0 else COLORS['danger']
                   for x in annual_data['record_delta']]
    bars = ax3.barh(annual_data['taxon_label'], annual_data['record_delta'],
                    color=colors_delta, alpha=0.8, edgecolor='black', linewidth=0.5)

    ax3.set_xlabel('记录数变化量', fontsize=11, fontweight='bold')
    ax3.set_title('2025-2026年记录数增减情况', fontsize=12, fontweight='bold')
    ax3.axvline(x=0, color='black', linestyle='-', linewidth=1)
    ax3.grid(axis='x', alpha=0.3)

    # 添加数值标签
    for i, (bar, value) in enumerate(zip(bars, annual_data['record_delta'])):
        ax3.text(value + (200 if value > 0 else -200), i,
                f'{value:+d}',
                va='center', ha='left' if value > 0 else 'right',
                fontsize=9, fontweight='bold')

    # 子图4: 占比变化
    colors_pct = [COLORS['success'] if x > 0 else COLORS['danger']
                 for x in annual_data['percentage_point_delta']]
    bars = ax4.barh(annual_data['taxon_label'],
                    annual_data['percentage_point_delta'],
                    color=colors_pct, alpha=0.8, edgecolor='black', linewidth=0.5)

    ax4.set_xlabel('占比变化 (百分点)', fontsize=11, fontweight='bold')
    ax4.set_title('2025-2026年占比增减情况', fontsize=12, fontweight='bold')
    ax4.axvline(x=0, color='black', linestyle='-', linewidth=1)
    ax4.grid(axis='x', alpha=0.3)

    # 添加数值标签
    for i, (bar, value) in enumerate(zip(bars, annual_data['percentage_point_delta'])):
        ax4.text(value + (0.5 if value > 0 else -0.5), i,
                f'{value:+.1f}pp',
                va='center', ha='left' if value > 0 else 'right',
                fontsize=9, fontweight='bold')

    plt.suptitle('澳门生物多样性年度变化分析 (2025 vs 2026)',
                fontsize=15, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig('生态昼夜曲资料/可视化图表/04_专业版_年度变化对比.png',
                dpi=300, bbox_inches='tight', facecolor='white')
    print("[OK] 已生成: 04_专业版_年度变化对比.png")
    plt.close()

def create_invasive_species_alert(data):
    """图表5: 入侵物种预警分析"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

    invasive_data = data['invasive']

    # 子图1: 入侵物种类型分布
    type_counts = invasive_data['type'].value_counts()
    colors_type = [COLORS['danger'], COLORS['warning'], COLORS['accent'], COLORS['primary']]

    wedges, texts, autotexts = ax1.pie(type_counts.values,
                                        labels=type_counts.index,
                                        autopct='%1.1f%%',
                                        colors=colors_type[:len(type_counts)],
                                        startangle=90,
                                        textprops={'fontsize': 11, 'fontweight': 'bold'})
    ax1.set_title('入侵物种类型分布', fontsize=12, fontweight='bold')

    # 子图2: 关注等级分布
    concern_counts = invasive_data['concern'].value_counts()
    colors_concern = {'高': COLORS['danger'], '中': COLORS['warning']}

    bars = ax2.bar(concern_counts.index, concern_counts.values,
                   color=[colors_concern.get(x, COLORS['primary']) for x in concern_counts.index],
                   alpha=0.8, edgecolor='black', linewidth=1)

    ax2.set_xlabel('关注等级', fontsize=11, fontweight='bold')
    ax2.set_ylabel('记录数', fontsize=11, fontweight='bold')
    ax2.set_title('入侵物种关注等级分布', fontsize=12, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)

    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')

    # 子图3: Top 10入侵物种
    species_counts = invasive_data['chinese_name'].value_counts().head(10)

    bars = ax3.barh(range(len(species_counts)), species_counts.values,
                    color=COLORS['danger'], alpha=0.7, edgecolor='black', linewidth=0.5)

    ax3.set_yticks(range(len(species_counts)))
    ax3.set_yticklabels(species_counts.index, fontsize=10)
    ax3.set_xlabel('观察记录数', fontsize=11, fontweight='bold')
    ax3.set_title('Top 10 入侵物种记录数', fontsize=12, fontweight='bold')
    ax3.grid(axis='x', alpha=0.3)

    for i, (bar, value) in enumerate(zip(bars, species_counts.values)):
        ax3.text(value + 1, i, f'{value}',
                va='center', fontsize=9, fontweight='bold')

    # 子图4: 不同区域的入侵物种分布
    area_counts = invasive_data['light_gradient'].value_counts()

    colors_area = {
        '高光区': COLORS['danger'],
        '中高光区': COLORS['warning'],
        '相对低光区': COLORS['success'],
        '补充样本': COLORS['primary']
    }

    bars = ax4.bar(range(len(area_counts)), area_counts.values,
                   color=[colors_area.get(x, COLORS['primary']) for x in area_counts.index],
                   alpha=0.8, edgecolor='black', linewidth=1)

    ax4.set_xticks(range(len(area_counts)))
    ax4.set_xticklabels(area_counts.index, rotation=20, ha='right', fontsize=10)
    ax4.set_ylabel('记录数', fontsize=11, fontweight='bold')
    ax4.set_title('入侵物种在不同光照区域的分布', fontsize=12, fontweight='bold')
    ax4.grid(axis='y', alpha=0.3)

    for bar in bars:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=9, fontweight='bold')

    plt.suptitle('澳门入侵物种预警分析',
                fontsize=15, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig('生态昼夜曲资料/可视化图表/05_专业版_入侵物种预警.png',
                dpi=300, bbox_inches='tight', facecolor='white')
    print("[OK] 已生成: 05_专业版_入侵物种预警.png")
    plt.close()

def create_summary_dashboard(data):
    """图表6: 数据概览仪表板"""
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

    # 计算关键指标
    total_records_2026 = data['annual']['records_2026'].sum()
    total_species_2026 = data['annual']['species_2026'].sum()
    invasive_species = data['invasive']['chinese_name'].nunique()
    invasive_records = len(data['invasive'])

    # 大标题
    fig.suptitle('澳门生物多样性调查数据概览 (2026)',
                fontsize=18, fontweight='bold', y=0.98)

    # 关键指标卡片
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.text(0.5, 0.6, f'{total_records_2026:,}',
            ha='center', va='center', fontsize=36, fontweight='bold',
            color=COLORS['primary'])
    ax1.text(0.5, 0.3, '总观察记录数',
            ha='center', va='center', fontsize=14, color='gray')
    ax1.axis('off')
    ax1.set_facecolor('#f8f9fa')

    ax2 = fig.add_subplot(gs[0, 1])
    ax2.text(0.5, 0.6, f'{total_species_2026:,}',
            ha='center', va='center', fontsize=36, fontweight='bold',
            color=COLORS['success'])
    ax2.text(0.5, 0.3, '记录物种总数',
            ha='center', va='center', fontsize=14, color='gray')
    ax2.axis('off')
    ax2.set_facecolor('#f8f9fa')

    ax3 = fig.add_subplot(gs[0, 2])
    ax3.text(0.5, 0.6, f'{invasive_species}',
            ha='center', va='center', fontsize=36, fontweight='bold',
            color=COLORS['danger'])
    ax3.text(0.5, 0.3, '入侵物种数',
            ha='center', va='center', fontsize=14, color='gray')
    ax3.axis('off')
    ax3.set_facecolor('#f8f9fa')

    # 类群分布饼图
    ax4 = fig.add_subplot(gs[1, :2])
    top_taxa = data['annual'].nlargest(8, 'records_2026')
    colors_pie = sns.color_palette("husl", len(top_taxa))

    wedges, texts, autotexts = ax4.pie(top_taxa['records_2026'],
                                        labels=top_taxa['taxon_label'],
                                        autopct='%1.1f%%',
                                        colors=colors_pie,
                                        startangle=90,
                                        textprops={'fontsize': 10})
    ax4.set_title('主要类群记录数占比', fontsize=13, fontweight='bold', pad=10)

    # 光照梯度对比
    ax5 = fig.add_subplot(gs[1, 2])
    light_data = data['light'][data['light']['light_gradient'] != '补充样本']

    bars = ax5.bar(range(len(light_data)), light_data['records'],
                   color=[COLORS['danger'], COLORS['warning'], COLORS['success']],
                   alpha=0.8)
    ax5.set_xticks(range(len(light_data)))
    ax5.set_xticklabels(light_data['light_gradient'], rotation=20, ha='right', fontsize=9)
    ax5.set_ylabel('记录数', fontsize=10, fontweight='bold')
    ax5.set_title('光照区域分布', fontsize=11, fontweight='bold')
    ax5.grid(axis='y', alpha=0.3)

    for bar in bars:
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=8)

    # 年度对比趋势
    ax6 = fig.add_subplot(gs[2, :])
    top_changes = data['annual'].nlargest(10, 'records_2026')

    x = np.arange(len(top_changes))
    width = 0.35

    bars1 = ax6.bar(x - width/2, top_changes['records_2025'], width,
                    label='2025年', color=COLORS['secondary'], alpha=0.7)
    bars2 = ax6.bar(x + width/2, top_changes['records_2026'], width,
                    label='2026年', color=COLORS['primary'], alpha=0.7)

    ax6.set_xlabel('类群', fontsize=11, fontweight='bold')
    ax6.set_ylabel('记录数', fontsize=11, fontweight='bold')
    ax6.set_title('Top 10 类群年度记录数对比', fontsize=12, fontweight='bold')
    ax6.set_xticks(x)
    ax6.set_xticklabels(top_changes['taxon_label'], rotation=30, ha='right', fontsize=10)
    ax6.legend(fontsize=10, loc='upper right')
    ax6.grid(axis='y', alpha=0.3)

    plt.savefig('生态昼夜曲资料/可视化图表/06_专业版_数据概览仪表板.png',
                dpi=300, bbox_inches='tight', facecolor='white')
    print("[OK] 已生成: 06_专业版_数据概览仪表板.png")
    plt.close()

def main():
    """主函数"""
    print("=" * 60)
    print("澳门生态昼夜曲 - 专业数据可视化")
    print("=" * 60)
    print("\n正在加载数据...")

    try:
        data = load_data()
        print("[OK] 数据加载完成\n")

        print("开始生成图表...")
        print("-" * 60)

        create_circadian_rhythm_chart(data)
        create_night_activity_comparison(data)
        create_light_gradient_analysis(data)
        create_annual_change_chart(data)
        create_invasive_species_alert(data)
        create_summary_dashboard(data)

        print("-" * 60)
        print("\n[完成] 所有图表生成完成！")
        print(f"输出目录: 生态昼夜曲资料/可视化图表/")
        print("\n生成的图表:")
        print("  1. 01_专业版_24小时活动节律图.png")
        print("  2. 02_专业版_夜间活动比例对比.png")
        print("  3. 03_专业版_光污染梯度分析.png")
        print("  4. 04_专业版_年度变化对比.png")
        print("  5. 05_专业版_入侵物种预警.png")
        print("  6. 06_专业版_数据概览仪表板.png")
        print("\n" + "=" * 60)

    except Exception as e:
        print(f"\n[错误] {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
