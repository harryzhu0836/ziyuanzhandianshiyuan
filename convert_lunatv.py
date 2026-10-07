#!/usr/bin/env python3
import json
import os

def main():
    online_path = "docs/data/online.json"
    output_path = "docs/data/lunatv.json"

    if not os.path.exists(online_path):
        print("[WARN] online.json 不存在，跳过转换")
        return

    with open(online_path, "r", encoding="utf-8") as f:
        online_data = json.load(f)

    sites = []
    # 兼容 online.json 的列表结构
    item_list = online_data.get("data", []) if isinstance(online_data, dict) else online_data

    for idx, r in enumerate(item_list, 1):
        api_url = r.get("api") or r.get("link") or ""
        if not api_url:
            continue
        
        sites.append({
            "key": f"ziyuan_{idx}",
            "name": r.get("name", f"资源站-{idx}"),
            "type": 1,
            "api": api_url,
            "searchable": 1,
            "quickSearch": 1,
            "filterable": 1
        })

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"sites": sites}, f, ensure_ascii=False, indent=2)

    print(f"[SUCCESS] 已将 {len(sites)} 个在线源转换为 LunaTV 格式: {output_path}")

if __name__ == "__main__":
    main()
