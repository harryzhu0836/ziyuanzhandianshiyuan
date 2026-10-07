#!/usr/bin/env python3
import json
import os
import re

def clean_api_url(raw_url: str) -> str:
    """提取并清洗有效的 MacCMS 采集 API 地址"""
    if not raw_url:
        return ""
    
    # 拆解嵌套代理
    if "url=" in raw_url:
        match = re.search(r'url=(https?://[^\s&]+)', raw_url)
        if match:
            raw_url = match.group(1)

    # 1. 过滤掉 ziyuanzu 官方详情页和非 http(s) 链接
    if "ziyuanzu.com" in raw_url or not (raw_url.startswith("http://") or raw_url.startswith("https://")):
        return ""

    # 2. 如果缺少 MacCMS 路由后缀，尝试自动拼接标准路径
    if not ("provide/vod" in raw_url or "api.php" in raw_url or "apijson" in raw_url or "feifei" in raw_url or "provide" in raw_url):
        raw_url = raw_url.rstrip("/") + "/api.php/provide/vod"

    return raw_url

def main():
    possible_inputs = [
        "docs/data/online.json",
        "docs/data/latest.json",
        "docs/data/sources.json"
    ]
    
    input_path = None
    for p in possible_inputs:
        if os.path.exists(p):
            input_path = p
            break

    output_path = "docs/data/lunatv.json"

    if not input_path:
        print("[ERROR] 找不到任何有效的 JSON 输入数据源！")
        return

    print(f"[INFO] 正在读取 {input_path}...")
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    sites = []

    # 1. 处理 api_site 字典结构（如 pz.v88.qzz.io）
    if isinstance(data, dict) and "api_site" in data:
        api_sites = data.get("api_site", {})
        for domain, info in api_sites.items():
            if not isinstance(info, dict):
                continue
            
            api_url = clean_api_url(info.get("api") or info.get("detail", ""))
            if not api_url:
                continue

            site_key = re.sub(r'[^a-zA-Z0-9_]', '_', domain)
            site_name = info.get("name", domain)

            sites.append({
                "key": f"site_{site_key}",
                "name": site_name,
                "type": 1,
                "api": api_url,
                "searchable": 1,
                "quickSearch": 1,
                "filterable": 1,
                "ext": ""
            })

    # 2. 处理常规列表结构（online.json / latest.json）
    else:
        item_list = []
        if isinstance(data, dict):
            item_list = data.get("data", []) or data.get("resources", [])
        elif isinstance(data, list):
            item_list = data

        for idx, r in enumerate(item_list, 1):
            if not isinstance(r, dict):
                continue

            # 🚨 核心关键：必须优先读取真实的 api 字段，不能错拿 link 网页链接
            raw_api = r.get("api") or r.get("url") or ""
            api_url = clean_api_url(raw_api)
            
            # 如果提取不到有效 API，丢弃该站点
            if not api_url:
                continue

            site_name = r.get("name", f"资源站-{idx}")
            
            sites.append({
                "key": f"site_ziyuan_{idx}",
                "name": site_name,
                "type": 1,
                "api": api_url,
                "searchable": 1,
                "quickSearch": 1,
                "filterable": 1,
                "ext": ""
            })

    lunatv_config = {
        "sites": sites
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(lunatv_config, f, ensure_ascii=False, indent=2)

    print(f"[SUCCESS] 成功清理并转换 {len(sites)} 个有效采集源 -> {output_path}")

if __name__ == "__main__":
    main()
