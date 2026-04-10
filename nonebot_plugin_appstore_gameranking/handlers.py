import json

from nonebot import on_command, require
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11.message import Message

require("nonebot_plugin_localstore")
import nonebot_plugin_localstore as store

from .data import get_appstore_top_grossing, filter_and_sort_target_apps

appstore_cmd = on_command("appstore", aliases={"appstore榜单", "appstore排名"}, priority=5, block=True)

DEFAULT_GAMES_DEFAULT = ["原神·空月之歌", "崩坏：星穹铁道", "鸣潮", "明日方舟：终末地", "绝区零", "明日方舟"]
DEFAULT_GAMES_FILE = store.get_plugin_config_file("default_games.json")


def get_default_games():
    if not DEFAULT_GAMES_FILE.exists():
        try:
            DEFAULT_GAMES_FILE.write_text(
                json.dumps(DEFAULT_GAMES_DEFAULT, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass
        return DEFAULT_GAMES_DEFAULT.copy()

    try:
        content = DEFAULT_GAMES_FILE.read_text(encoding="utf-8")
        data = json.loads(content)
        if isinstance(data, list) and all(isinstance(x, str) for x in data):
            return data
    except Exception:
        pass

    return DEFAULT_GAMES_DEFAULT.copy()


def save_default_games(games):
    try:
        DEFAULT_GAMES_FILE.write_text(
            json.dumps(games, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return True
    except Exception:
        return False


def format_target_rankings(apps, target_names):
    filtered = filter_and_sort_target_apps(apps, target_names)
    lines = ["🎮 指定游戏排名："]
    for item in filtered:
        lines.append(f"{item['游戏名称']}：{item['排名']}")
    return "\n".join(lines)


@appstore_cmd.handle()
async def handle_appstore_cmd(bot: Bot, event: Event, arg: Message = CommandArg()):
    text = arg.extract_plain_text().strip()
    if not text:
        apps = await get_appstore_top_grossing(country="cn", limit=100)
        await appstore_cmd.finish(format_target_rankings(apps, get_default_games()))
        return

    parts = text.split()
    if parts[0] in ["帮助", "help", "h", "?", "？"]:
        await appstore_cmd.finish(
            "用法：\n1. /appstore -> 默认输出指定游戏排名\n2. /appstore debug -> 输出抓取原始栏目信息+筛选结果\n3. /appstore 全榜 <N> -> 输出前N名榜单简要\n4. /appstore 目标 原神,崩坏:星穹铁道 -> 输出目标游戏排名\n5. /appstore 添加 <游戏名> -> 将游戏添加到默认关注列表"
        )
        return

    if parts[0] == "debug":
        apps = await get_appstore_top_grossing(country="cn", limit=100)
        raw_lines = ["[DEBUG] 抓取榜单前10原始结果："]
        for i, app in enumerate(apps[:10], 1):
            raw_lines.append(f"{i}. {app.get('应用名称', 'N/A')} | AppID {app.get('App ID', 'N/A')}")
        debug_names = get_default_games()
        filtered = filter_and_sort_target_apps(apps, debug_names)
        raw_lines.append("\n[DEBUG] 筛选结果：")
        for item in filtered:
            raw_lines.append(f"{item['游戏名称']} -> {item['排名']} | {item['完整应用名']}")
        await appstore_cmd.finish("\n".join(raw_lines))
        return

    if parts[0] in ["添加", "add"]:
        name = " ".join(parts[1:]).strip()
        if not name:
            await appstore_cmd.finish("请提供要添加的游戏名称，例如：/appstore 添加 原神·空月之歌")
            return
        games = get_default_games()
        if name in games:
            await appstore_cmd.finish(f"游戏“{name}”已在默认关注列表中，无需重复添加。")
            return
        games.append(name)
        if save_default_games(games):
            await appstore_cmd.finish(
                f"已将游戏“{name}”添加到默认关注列表。\n当前默认关注游戏：\n" + "\n".join(games)
            )
        else:
            await appstore_cmd.finish("保存失败，请检查文件权限或稍后重试。")
        return

    if parts[0] in ["目标", "target", "filter"]:
        names = [x.strip() for x in " ".join(parts[1:]).replace("，", ",").replace("、", ",").split(",") if x.strip()]
        if not names:
            await appstore_cmd.finish("请提供目标游戏名称列表，例如：/appstore 目标 原神,崩坏:星穹铁道")
            return
        apps = await get_appstore_top_grossing(country="cn", limit=100)
        await appstore_cmd.finish(format_target_rankings(apps, names))
        return

    if parts[0] in ["全榜", "full", "all"]:
        limit = 100
        if len(parts) >= 2 and parts[1].isdigit():
            limit = max(1, min(int(parts[1]), 100))
        apps = await get_appstore_top_grossing(country="cn", limit=limit)
        msg = [f"App Store 畅销榜（中国区）前{min(limit, len(apps))}："]
        for i, app in enumerate(apps[:min(limit, 20)], 1):
            msg.append(f"{i}. {app['应用名称']} ({app['开发者']})")
        await appstore_cmd.finish("\n".join(msg))
        return

    apps = await get_appstore_top_grossing(country="cn", limit=100)
    await appstore_cmd.finish(format_target_rankings(apps, get_default_games()))
