# -*- coding: utf-8 -*-
"""为点位详情图生成物种中文名数据包。

数据来源优先使用 iNaturalist 分类接口的中文常用名。脚本会把查询结果缓存下来，
以后重新运行时只补查新增物种。
"""
'''有些物种暂时会显示“暂未匹配”，因为 iNaturalist 查询时触发过限流。我已经把脚本改成可断点续跑、低频查询。以后想继续补全中文名，可以运行：
python -X utf8 "生成中文名数据.py" --limit 100 --delay 2.5
'''
'''当前生成结果：
    唯一物种：3606 个
    已匹配中文名：1248 个
    按实际点位记录算，约 72.9% 的点位已经能显示中文名
'''
from __future__ import annotations

import csv
import json
import re
import argparse
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
TABLE_DIR = ROOT / "表格数据"
CLEAN_DIR = TABLE_DIR / "正确数据"
ABNORMAL_DIR = TABLE_DIR / "原始对比异常数据"
OUT_DIR = TABLE_DIR / "中文名数据"
WEB_OUT = ROOT / "热点图展示" / "中文名数据.js"

DATASETS = [
    CLEAN_DIR / "2025 團隊賽數據包_Sheet1.csv",
    CLEAN_DIR / "副本2026 團隊賽數據包_Sheet1.csv",
    ABNORMAL_DIR / "异常数据_2025_由原始减正确.csv",
    ABNORMAL_DIR / "异常数据_2026_由原始减正确.csv",
]

CACHE_FILE = OUT_DIR / "中文名查询缓存.json"
CSV_FILE = OUT_DIR / "中文名数据包.csv"
JSON_FILE = OUT_DIR / "中文名数据包.json"

API_URL = "https://api.inaturalist.org/v1/taxa"
USER_AGENT = "Biodiversity-competition-local-script/1.0"
DEFAULT_DELAY = 1.2
REQUEST_TIMEOUT = 20
CHINESE_RE = re.compile(r"[\u3400-\u9fff]")


def has_chinese(value: str | None) -> bool:
    return bool(value and CHINESE_RE.search(value))


def clean_text(value: Any) -> str:
    return str(value or "").strip()


def read_species() -> dict[str, dict[str, Any]]:
    species: dict[str, dict[str, Any]] = {}
    for path in DATASETS:
        if not path.exists():
            raise FileNotFoundError(path)
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                scientific_name = clean_text(row.get("taxon_species_name")) or clean_text(row.get("taxon_genus_name"))
                if not scientific_name:
                    continue
                item = species.setdefault(
                    scientific_name,
                    {
                        "scientific_name": scientific_name,
                        "record_count": 0,
                        "iconic_taxon_name": clean_text(row.get("iconic_taxon_name")),
                        "taxon_kingdom_name": clean_text(row.get("taxon_kingdom_name")),
                        "taxon_class_name": clean_text(row.get("taxon_class_name")),
                        "taxon_family_name": clean_text(row.get("taxon_family_name")),
                        "taxon_genus_name": clean_text(row.get("taxon_genus_name")),
                    },
                )
                item["record_count"] += 1
    return species


def load_cache() -> dict[str, dict[str, Any]]:
    if not CACHE_FILE.exists():
        return {}
    with CACHE_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_cache(cache: dict[str, dict[str, Any]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tmp = CACHE_FILE.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as file:
        json.dump(cache, file, ensure_ascii=False, indent=2, sort_keys=True)
    tmp.replace(CACHE_FILE)


def choose_result(scientific_name: str, results: list[dict[str, Any]]) -> dict[str, Any] | None:
    target = scientific_name.casefold()
    for item in results:
        if clean_text(item.get("name")).casefold() == target:
            return item
    for item in results:
        if clean_text(item.get("matched_term")).casefold() == target:
            return item
    return results[0] if results else None


def choose_chinese_name(item: dict[str, Any]) -> str:
    preferred = clean_text(item.get("preferred_common_name"))
    if has_chinese(preferred):
        return preferred

    names = item.get("names") if isinstance(item.get("names"), list) else []
    valid_names = [name for name in names if name.get("is_valid", True)]

    preference_order = [
        ("zh-CN", "chinese-simplified"),
        ("zh-Hans", "chinese-simplified"),
        ("zh", "chinese-simplified"),
        ("zh", "chinese-traditional"),
        ("zh-TW", "chinese-traditional"),
        ("zh-Hant", "chinese-traditional"),
    ]
    for locale, lexicon in preference_order:
        for name in valid_names:
            value = clean_text(name.get("name"))
            if name.get("locale") == locale and name.get("lexicon") == lexicon and has_chinese(value):
                return value

    for name in valid_names:
        value = clean_text(name.get("name"))
        locale = clean_text(name.get("locale"))
        lexicon = clean_text(name.get("lexicon")).lower()
        if (locale.startswith("zh") or "chinese" in lexicon) and has_chinese(value):
            return value

    return ""


def query_one(scientific_name: str) -> dict[str, Any]:
    params = {
        "q": scientific_name,
        "rank": "species",
        "locale": "zh-CN",
        "all_names": "true",
        "per_page": "10",
    }
    url = API_URL + "?" + urllib.parse.urlencode(params)
    last_error = ""

    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as response:
                data = json.load(response)
            item = choose_result(scientific_name, data.get("results", []))
            if not item:
                return {
                    "scientific_name": scientific_name,
                    "chinese_name": "",
                    "matched_scientific_name": "",
                    "inaturalist_taxon_id": "",
                    "rank": "",
                    "observations_count": "",
                    "source": "iNaturalist",
                    "error": "not_found",
                    "queried_at": datetime.now().isoformat(timespec="seconds"),
                }
            return {
                "scientific_name": scientific_name,
                "chinese_name": choose_chinese_name(item),
                "matched_scientific_name": clean_text(item.get("name")),
                "inaturalist_taxon_id": item.get("id") or "",
                "rank": clean_text(item.get("rank")),
                "observations_count": item.get("observations_count") or "",
                "source": "iNaturalist",
                "error": "",
                "queried_at": datetime.now().isoformat(timespec="seconds"),
            }
        except Exception as exc:  # 网络查询失败时保留错误，方便下次补查
            last_error = f"{type(exc).__name__}: {exc}"
            time.sleep(1.2 * (attempt + 1))

    return {
        "scientific_name": scientific_name,
        "chinese_name": "",
        "matched_scientific_name": "",
        "inaturalist_taxon_id": "",
        "rank": "",
        "observations_count": "",
        "source": "iNaturalist",
        "error": last_error,
        "queried_at": datetime.now().isoformat(timespec="seconds"),
    }


def write_outputs(records: list[dict[str, Any]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fields = [
        "scientific_name",
        "chinese_name",
        "matched_scientific_name",
        "inaturalist_taxon_id",
        "rank",
        "record_count",
        "iconic_taxon_name",
        "taxon_kingdom_name",
        "taxon_class_name",
        "taxon_family_name",
        "taxon_genus_name",
        "observations_count",
        "source",
        "error",
        "queried_at",
    ]
    with CSV_FILE.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)

    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source": "iNaturalist API /v1/taxa, locale=zh-CN",
        "total_taxa": len(records),
        "with_chinese_name": sum(1 for item in records if item.get("chinese_name")),
        "names": {
            item["scientific_name"]: {
                "chinese_name": item.get("chinese_name", ""),
                "matched_scientific_name": item.get("matched_scientific_name", ""),
                "inaturalist_taxon_id": item.get("inaturalist_taxon_id", ""),
                "source": item.get("source", ""),
            }
            for item in records
        },
    }
    with JSON_FILE.open("w", encoding="utf-8", newline="") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)

    WEB_OUT.write_text(
        "// 自动生成，请运行 生成中文名数据.py 更新。\n"
        + "window.CHINESE_NAME_DATA = "
        + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="生成物种中文名数据包")
    parser.add_argument("--limit", type=int, default=0, help="本次最多查询多少个未缓存物种；0 表示不限制")
    parser.add_argument("--skip-errors", action="store_true", help="跳过之前已经查询失败的物种")
    parser.add_argument("--no-query", action="store_true", help="不访问网络，只用现有缓存生成数据包")
    parser.add_argument("--delay", type=float, default=DEFAULT_DELAY, help="两次查询之间的等待秒数，避免接口限流")
    args = parser.parse_args()

    species = read_species()
    cache = load_cache()
    if args.skip_errors:
        missing = [name for name in species if name not in cache]
    else:
        missing = [name for name in species if name not in cache or cache[name].get("error")]
    missing.sort(key=lambda name: (-species[name]["record_count"], name))
    if args.no_query:
        missing = []
    if args.limit and args.limit > 0:
        missing = missing[: args.limit]
    print(f"共发现 {len(species)} 个唯一物种；缓存已有 {len(cache)} 个；需要查询 {len(missing)} 个。")

    for index, name in enumerate(missing, 1):
        cache[name] = query_one(name)
        if index % 10 == 0 or index == len(missing):
            save_cache(cache)
            print(f"已查询 {index}/{len(missing)}")
        if args.delay > 0 and index != len(missing):
            time.sleep(args.delay)
    if missing:
        save_cache(cache)

    records = []
    for name in sorted(species):
        record = {**species[name], **cache.get(name, {})}
        records.append(record)
    write_outputs(records)

    with_name = sum(1 for item in records if item.get("chinese_name"))
    print(f"已生成 {CSV_FILE}")
    print(f"已生成 {JSON_FILE}")
    print(f"已生成 {WEB_OUT}")
    print(f"中文名覆盖：{with_name}/{len(records)}")


if __name__ == "__main__":
    main()
