# 澳门生物多样性数据分析项目

本项目用于参加 2026 年澳门校际团队挑战赛。我们围绕 2025 与 2026 年澳门生物多样性观测数据，完成数据读取、格式转换、坐标异常识别、清洗、统计验证、中文物种名补全，以及交互式热点地图展示。

项目的核心目标不是只做一张图，而是建立一条可以复查的数据分析流程：从原始数据包开始，逐步得到可分析的 CSV、可追踪的异常记录、用于报告的正确数据，以及可以向评委和同学展示的可视化页面。

## 团队成员

| 成员 | 角色 | 主要工作 |
| --- | --- | --- |
| 黄语萱 | 队长 | 统筹研究方向、整合分析报告、把控展示表达 |
| 莫欣睿 | 队员 | 数据清洗、异常点复核、物种与生态指标整理 |
| 林俊宇 | 队员 | 脚本开发、地图可视化、统计数值验证 |

## 项目内容

我们从比赛提供的数据包中提取观测记录，并围绕以下问题开展分析：

1. 澳门不同年份的生物多样性记录数量、物种数量和类群结构有什么变化。
2. 哪些物种是高频优势物种，哪些物种较稀有，哪些物种适合作为生态指示物种。
3. 观测点坐标是否落在澳门陆地区域内，异常点如何识别和剔除。
4. 清洗后的数据如何支撑 Shannon 指数、Simpson 指数、Pielou 均匀度等报告数值。
5. 如何把正确数据和异常数据以交互式地图方式展示出来。

## 目录结构

```text
Biodiversity_competition/
├── README.md
├── requirements.txt
├── scripts/                         # 全部可运行脚本
│   ├── data_conversion/             # 数据读取与格式转换
│   │   ├── convert_to_csv.py
│   │   ├── export_readable_text.py
│   │   └── preview_raw_data.py
│   ├── data_cleaning/               # 数据清洗与异常数据同步
│   │   ├── clean_correct_data.py
│   │   └── update_abnormal_from_clean.py
│   ├── analysis/                    # 专题分析与研究大纲生成
│   │   └── generate_ecological_nocturne.py
│   ├── validation/                  # 坐标验证与报告数值验证
│   │   ├── check_coordinates.py
│   │   └── verify_reports.py
│   ├── visualization/               # 地图数据与中文名数据生成
│   │   ├── generate_heatmap_data.py
│   │   └── generate_chinese_names.py
│   └── serve/
│       └── server.py                # 本地地图服务器
├── 工具/                            # 可执行工具
│   ├── cloudflared-windows-386.exe
│   └── mutagen.exe
├── 数据包/                          # 原始 Excel 和说明 PDF
├── 表格数据/                        # 转换后的 CSV、正确数据、中文名数据
├── 异常数据/                        # 坐标异常结果和澳门陆地参考边界
├── 热点图展示/                      # 交互式 HTML 地图和生成后的 JS 数据
├── 报告文档/                        # 分析报告、比赛要求、验证报告
├── 图片素材/                        # 展示图片素材
└── 往届作品参考/                    # 往届项目与选题参考
```

## 环境配置

建议使用 Python 3.10 或以上版本。

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

如果只查看 `热点图展示/*.html`，浏览器可以直接打开；如果要完整加载本地 JS 数据和分享页面，建议用服务器脚本启动。

## 推荐运行流程

从项目根目录运行以下命令：

```powershell
# 1. 将原始 Excel 数据包转换为 CSV
python scripts/data_conversion/convert_to_csv.py

# 2. 检查坐标异常，生成异常清单
python scripts/validation/check_coordinates.py

# 3. 根据坐标异常清单生成正确数据
python scripts/data_cleaning/clean_correct_data.py

# 4. 反推出原始对比异常数据，供地图同时展示正确点和异常点
python scripts/data_cleaning/update_abnormal_from_clean.py

# 5. 生成热点图使用的数据文件
python scripts/visualization/generate_heatmap_data.py

# 6. 使用现有缓存生成中文物种名数据
python scripts/visualization/generate_chinese_names.py --no-query

# 7. 验证报告关键数值
python scripts/validation/verify_reports.py

# 8. 生成“澳门生态昼夜曲”专题分析和研究大纲
python scripts/analysis/generate_ecological_nocturne.py

# 9. 启动本地地图页面
python scripts/serve/server.py
```

## 脚本说明

### 数据转换

`scripts/data_conversion/convert_to_csv.py`

将 `数据包/` 中的 Excel 转换为 CSV，输出到 `表格数据/`，并生成前 100 行预览和 `_元数据摘要.json`。

```powershell
python scripts/data_conversion/convert_to_csv.py
python scripts/data_conversion/convert_to_csv.py "2025 團隊賽數據包.xlsx" --preview-rows 50
```

`scripts/data_conversion/preview_raw_data.py`

在终端中快速预览原始 PDF 和 Excel 的前几行，适合检查数据包是否能正常读取。

```powershell
python scripts/data_conversion/preview_raw_data.py --rows 20
```

`scripts/data_conversion/export_readable_text.py`

把 PDF 说明和 Excel 内容导出为文本，输出到 `可读文本/`，方便搜索和整理。

```powershell
python scripts/data_conversion/export_readable_text.py --max-rows 500
```

### 数据验证与清洗

`scripts/validation/check_coordinates.py`

使用 `异常数据/macau_land_reference.geojson` 判断观测坐标是否落在澳门陆地区域或边界容差内。输出坐标异常 CSV 和 `坐标验证报告.json`。

```powershell
python scripts/validation/check_coordinates.py
```

`scripts/data_cleaning/clean_correct_data.py`

读取坐标异常清单，按 `id` 从原始表格数据中剔除异常记录，生成 `表格数据/正确数据/`。

```powershell
python scripts/data_cleaning/clean_correct_data.py
```

`scripts/data_cleaning/update_abnormal_from_clean.py`

根据“原始数据减正确数据”重新生成异常数据，输出到 `表格数据/原始对比异常数据/`。当正确数据更新后应运行一次。

```powershell
python scripts/data_cleaning/update_abnormal_from_clean.py
```

`scripts/validation/verify_reports.py`

重新计算总记录数、物种数、Shannon 指数、Simpson 指数、Pielou 均匀度、Top 物种和跨年份共同物种，检查是否与报告关键数值一致。

```powershell
python scripts/validation/verify_reports.py
```

### 专题分析

`scripts/analysis/generate_ecological_nocturne.py`

围绕“澳门生态昼夜曲：年度变迁下的不夜城与生物多样性”生成专题分析结果。脚本会复用正确数据和坐标验证区域口径，输出年度类群变化、昼夜节律、简化光污染梯度、入侵物种预警点位，以及可用于 A0 海报和 5 分钟短片的研究大纲。

```powershell
python scripts/analysis/generate_ecological_nocturne.py
```

### 可视化

`scripts/visualization/generate_heatmap_data.py`

读取正确数据和原始对比异常数据，生成 `热点图展示/热点图数据.js`，供两个 HTML 地图页面加载。

```powershell
python scripts/visualization/generate_heatmap_data.py
```

`scripts/visualization/generate_chinese_names.py`

为地图点位详情补充中文物种名。默认会访问 iNaturalist API；如果只想使用已有缓存，使用 `--no-query`。

```powershell
python scripts/visualization/generate_chinese_names.py --no-query
python scripts/visualization/generate_chinese_names.py --limit 100 --delay 2.5
```

`scripts/serve/server.py`

启动本地静态服务器并打开热点图页面。需要外网临时分享链接时可加 `--tunnel`，脚本会尝试调用 `工具/cloudflared-windows-386.exe`。

```powershell
python scripts/serve/server.py
python scripts/serve/server.py --port 8081
python scripts/serve/server.py --tunnel
```

## 主要输出

| 输出位置 | 内容 |
| --- | --- |
| `表格数据/` | Excel 转换后的原始 CSV 和预览 CSV |
| `异常数据/` | 坐标异常清单、详细版异常清单、坐标验证报告 |
| `表格数据/正确数据/` | 剔除异常坐标后的可分析数据 |
| `表格数据/原始对比异常数据/` | 用原始数据减正确数据得到的异常记录 |
| `表格数据/中文名数据/` | 物种中文名缓存、CSV 和 JSON 数据包 |
| `表格数据/生态昼夜曲/` | 年度变迁、昼夜节律、光污染梯度和入侵预警专题 CSV |
| `热点图展示/` | 交互式地图页面及其 JS 数据 |
| `报告文档/` | 分析报告与数值验证报告 |

## 分析报告

项目已整理多份 Markdown 报告，主要包括：

| 报告 | 说明 |
| --- | --- |
| `报告文档/数据综合分析报告.md` | 总体数据结构和核心发现 |
| `报告文档/生物多样性指数分析报告.md` | Shannon、Simpson、Pielou 等指数分析 |
| `报告文档/优势物种分析报告.md` | 高频物种和类群优势结构 |
| `报告文档/稀有物种分析报告.md` | 低频物种和稀有性分析 |
| `报告文档/生态指示物种分析报告.md` | 湿地、森林、入侵和城市适应指示物种 |
| `报告文档/十大选题深度分析.md` | 后续展示和研究选题储备 |
| `报告文档/澳门生态昼夜曲研究大纲.md` | 年度变迁、不夜城梯度、昆虫乐声、鸟类日班夜班和入侵预警的最终主线大纲 |

## AI 工具使用说明

本项目在代码整理、数据处理脚本编写、报告结构梳理和可视化呈现中使用了 AI 辅助工具。最终提交学术海报和科普短片时，应按比赛要求标注 AI 工具参与情况。

## 许可与用途

本仓库用于校际团队挑战赛项目开发、学习和展示交流。数据来源、边界数据来源及外部 API 结果应在最终作品中按要求注明。
