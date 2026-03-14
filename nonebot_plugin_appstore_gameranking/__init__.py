from nonebot.plugin import PluginMetadata
from . import handlers

__plugin_name__ = "AppStore游戏榜单"
__plugin_usage__ = "支持 /appstore 或 appstore 文本查询指定游戏排名"

__plugin_meta__ = PluginMetadata(
    name="AppStore游戏榜单",
    description="实时查询 App Store 中国区畅销榜，并输出指定游戏排名。",
    usage="/appstore",
    type="application",
    homepage="https://github.com/whdycdq/nonebot-plugin-appstore-gameranking",
    supported_adapters={"~onebot.v11"},
)

