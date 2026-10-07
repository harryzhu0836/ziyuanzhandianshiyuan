#!/usr/bin/env python3
import json
import os

def main():
    online_path = "docs/data/online.json"
    output_path = "docs/data/lunatv.json"

    if not os.path.exists(online_path):
        print(f"[ERROR] 找不到输入文件: {online_path}")
        return

    with open(online_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    sites = []

    # 1. 优先适配 pz.v88.qzz.io 这类 api_site 字典结构
    if isinstance(data, dict) and "api_site" in data:
        api_sites = data.get("api_site", {})
        for domain, info in api_sites.items():
            if not isinstance(info, dict):
                continue
            
            api_url = info.get("api", "")
            if not api_url or not (api_url.startswith("http://") or api_url.startswith("https://")):
                continue

            # 安全处理 Key，替换特殊字符
            site_key = domain.replace(".", "_").replace("-", "_")
            site_name = info.get("name", domain)

            sites.append({
                "key": f"site_{site_key}",
                "name": site_name,
                "type": 1,  # 1 为标准 MacCMS/JSON 采集接口
                "api": api_url,
                "searchable": 1,
                "quickSearch": 1,
                "filterable": 1,
                "ext": ""
            })

    # 2. 兼容传统的数组列表结构 (online.json)
    else:
        item_list = []
        if isinstance(data, dict):
            item_list = data.get("data", []) or data.get("resources", [])
        elif isinstance(data, list):
            item_list = data

        for idx, r in enumerate(item_list, 1):
            if not isinstance(r, dict):
                continue

            api_url = r.get("api") or r.get("url") or r.get("link") or ""
            if not api_url or not (api_url.startswith("http://") or api_url.startswith("https://")):
                continue

            sites.append({
                "key": f"site_ziyuan_{idx}",
                "name": r.get("name", f"资源站-{idx}"),
                "type": 1,
                "api": api_url,
                "searchable": 1,
                "quickSearch": 1,
                "filterable": 1,
                "ext": ""
            })

    # 生成 LunaTV 标准格式
    lunatv_config = {
        "sites": sites
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(lunatv_config, f, ensure_ascii=False, indent=2)

    print(f"[SUCCESS] 成功转换 {len(sites)} 个站点到 {output_path}")

if __name__ == "__main__":
    main()
