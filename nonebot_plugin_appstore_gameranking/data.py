import httpx
from typing import List, Dict


async def get_appstore_top_grossing(country: str = "cn", limit: int = 200) -> List[Dict]:
    """异步爬取 App Store 畅销榜。
    返回包含排名、应用名称、App ID、开发者等字段的列表。
    """
    if limit < 1:
        limit = 1
    if limit > 200:
        limit = 200

    api_url = f"https://itunes.apple.com/{country}/rss/topgrossingapplications/limit={limit}/json"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Accept": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
            response = await client.get(api_url)
            response.raise_for_status()
            data = response.json()
            app_list = []
            for rank, item in enumerate(data.get("feed", {}).get("entry", []), start=1):
                app_list.append({
                    "排名": rank,
                    "应用名称": item["im:name"]["label"],
                    "App ID": item["id"]["attributes"]["im:id"],
                    "开发者": item["im:artist"]["label"],
                    "分类名称": item["category"]["attributes"]["label"],
                    "应用链接": item["id"]["label"]
                })
            return app_list
    except Exception:
        return []


def filter_and_sort_target_apps(all_apps: List[Dict], target_names: List[str]) -> List[Dict]:
    """从榜单中筛选目标游戏并按排名排序。"""
    target_apps = []
    unranked_apps = []
    for name in target_names:
        name = name.strip()
        found = False
        for app in all_apps:
            if app.get("应用名称", "").strip() == name:
                target_apps.append({
                    "游戏名称": name,
                    "排名": app["排名"],
                    "完整应用名": app["应用名称"],
                    "开发者": app["开发者"],
                    "App ID": app["App ID"]
                })
                found = True
                break
        if not found:
            unranked_apps.append({
                "游戏名称": name,
                "排名": "未上榜（前100名内）",
                "完整应用名": name,
                "开发者": "未知",
                "App ID": "未知"
            })

    target_apps.sort(key=lambda x: x["排名"] if isinstance(x["排名"], int) else 999)
    target_apps.extend(unranked_apps)
    return target_apps


def format_ranking_list(app_list: List[Dict], limit: int = 10) -> str:
    if not app_list:
        return "未能获取榜单数据，请稍后重试。"
    lines = [f"App Store 畅销榜 TOP {min(limit, len(app_list))}（来源：itunes.apple.com）"]
    for item in app_list[:limit]:
        lines.append(f"{item['排名']}. {item['应用名称']} ({item['开发者']}) | AppID: {item['App ID']}")
    return "\n".join(lines)
