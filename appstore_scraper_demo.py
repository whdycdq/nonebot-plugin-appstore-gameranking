import requests
import json
import sys

# 解决Windows终端中文乱码问题
sys.stdout.reconfigure(encoding='utf-8')

def get_appstore_top_grossing(country="cn", limit=200):
    """
    爬取App Store畅销榜（苹果官方接口，无第三方依赖）
    :param country: 国家/地区代码（cn=中国，us=美国，jp=日本等）
    :param limit: 获取数量（1-200，最大200）
    :return: 榜单列表（含排名、名称、AppID、开发者等）
    """
    # 苹果官方RSS JSON接口（最稳定、合规）
    api_url = f"https://itunes.apple.com/{country}/rss/topgrossingapplications/limit={limit}/json"
    
    # 请求头（模拟手机端，避免被拦截）
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Accept": "application/json"
    }

    try:
        # 发送请求（超时10秒，避免卡死）
        response = requests.get(api_url, headers=headers, timeout=10)
        # 检查HTTP状态码（非200则抛出异常）
        response.raise_for_status()
        # 解析JSON数据
        data = response.json()

        # 提取核心数据
        app_list = []
        for rank, item in enumerate(data["feed"]["entry"], 1):
            app_info = {
                "排名": rank,
                "应用名称": item["im:name"]["label"],
                "App ID": item["id"]["attributes"]["im:id"],
                "开发者": item["im:artist"]["label"],
                "分类ID": item["category"]["attributes"]["term"],
                "分类名称": item["category"]["attributes"]["label"],
                "图标链接(100x100)": item["im:image"][2]["label"],
                "应用链接": item["id"]["label"]
            }
            app_list.append(app_info)
        
        return app_list

    # 针对性异常处理
    except requests.exceptions.HTTPError as e:
        print(f"HTTP请求错误（状态码异常）：{e}")
        return []
    except requests.exceptions.Timeout:
        print("请求超时！请检查网络或稍后重试")
        return []
    except json.JSONDecodeError:
        print("接口返回数据格式错误，可能是苹果接口临时调整")
        return []
    except KeyError as e:
        print(f"数据解析错误：缺少字段 {e}，可能是接口结构变化")
        return []
    except Exception as e:
        print(f"未知错误：{e}")
        return []

def filter_and_sort_target_apps(all_apps, target_names):
    """
    从榜单中筛选指定应用，并按排名从高到低排序（未上榜的放最后）
    :param all_apps: 完整榜单列表
    :param target_names: 要筛选的应用名称列表
    :return: 排序后的应用信息列表
    """
    target_apps = []
    unranked_apps = []
    
    # 遍历目标应用名称，先筛选出所有目标应用
    for name in target_names:
        matched = False
        # 遍历榜单找匹配的应用
        for app in all_apps:
            # 模糊匹配（避免名称特殊符号/空格导致匹配失败）
            if name in app["应用名称"]:
                target_apps.append({
                    "游戏名称": name,
                    "排名": app["排名"],
                    "完整应用名": app["应用名称"],
                    "开发者": app["开发者"],
                    "App ID": app["App ID"]
                })
                matched = True
                break
        if not matched:
            # 未上榜的应用
            unranked_apps.append({
                "游戏名称": name,
                "排名": 999,  # 用999标记未上榜，方便排序
                "完整应用名": name,
                "开发者": "未知",
                "App ID": "未知"
            })
    
    # 按排名从高到低排序（数字越小排名越高）
    target_apps.sort(key=lambda x: x["排名"])
    # 合并已上榜和未上榜的应用（未上榜的放最后）
    target_apps += unranked_apps
    
    # 把未上榜的排名标记改回文字描述
    for app in target_apps:
        if app["排名"] == 999:
            app["排名"] = "未上榜（前200名内）"
    
    return target_apps

# 主程序入口
if __name__ == "__main__":
    # 1. 爬取中国区畅销榜前200名
    print("正在爬取App Store中国区畅销榜前200名...")
    top_200_apps = get_appstore_top_grossing(country="cn", limit=200)
    
    # 2. 筛选指定游戏（新增绝区零）
    target_games = ["原神", "崩坏：星穹铁道", "鸣潮", "明日方舟：终末地", "绝区零"]
    sorted_target_apps = filter_and_sort_target_apps(top_200_apps, target_games)
    
    # 3. 输出结果（按排名顺序）
    if top_200_apps:
        print("\n===== 指定游戏排名信息（按排名从高到低） =====")
        for idx, app in enumerate(sorted_target_apps, 1):
            print(f"\n{idx}. {app['游戏名称']}:")
            print(f"   排名：{app['排名']}")
            print(f"   完整应用名：{app['完整应用名']}")
            print(f"   开发者：{app['开发者']}")
            print(f"   App ID：{app['App ID']}")
        
        # 4. 保存完整榜单和筛选结果
        # 保存完整前200榜单
        with open("appstore_top_200.json", "w", encoding="utf-8") as f:
            json.dump(top_200_apps, f, ensure_ascii=False, indent=2)
        # 保存排序后的筛选结果
        with open("target_games_ranking_sorted.json", "w", encoding="utf-8") as f:
            json.dump(sorted_target_apps, f, ensure_ascii=False, indent=2)
        
        print("\n✅ 数据保存完成：")
        print("  - 完整前200榜单：appstore_top_200.json")
        print("  - 排序后游戏排名：target_games_ranking_sorted.json")
    else:
        print("❌ 未能获取到榜单数据")