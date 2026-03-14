# nonebot-plugin-appstore-gameranking

一个 NoneBot2 插件，实时查询 App Store 畅销榜，并输出指定游戏在榜单中的排名。

## 📦 插件介绍

- 插件名：`nonebot_plugin_appstore_gameranking`
- 功能：抓取 App Store 中国区畅销榜（Top Grossing），支持默认目标游戏排名、全榜输出、目标自定义、调试信息。
- 主要命令：`/appstore`

## ⚙️ 功能与指令

### /appstore（默认）
输出默认关注游戏的排名：
- 原神·空月之歌
- 崩坏：星穹铁道
- 鸣潮
- 明日方舟：终末地
- 绝区零
- 明日方舟

### /appstore 帮助
```
/appstore 帮助
```
输出命令用法说明。

### /appstore debug
```
/appstore debug
```
输出抓取的原始榜单前10条与筛选结果，用于调试。

### /appstore 全榜 <N>
```
/appstore 全榜 20
```
输出前 N 名畅销榜（N 最大 200，默认 100）。

### /appstore 目标 <游戏1,游戏2,...>
```
/appstore 目标 原神,崩坏：星穹铁道
```
输出指定目标游戏的排名（若未上榜则显示“未上榜（前100名内）”）。

## 🧩 安装

在 NoneBot 项目中，使用 `pip` 安装本插件包：

```bash
pip install nonebot-plugin-appstore-gameranking
```

在 `pyproject.toml` 的 `[tool.nonebot]` 部分加入：

```toml
plugins = ["nonebot_plugin_appstore_gameranking"]
```

## 🧪 本地测试

在开发项目里直接运行 NoneBot，插件会自动注册 `/appstore` 命令。

## 🧠 源码结构

- `nonebot_plugin_appstore_gameranking/__init__.py`：插件元信息
- `nonebot_plugin_appstore_gameranking/data.py`：App Store 爬取与筛选辅助函数
- `nonebot_plugin_appstore_gameranking/handlers.py`：指令解析与结果格式化
- `appstore_scraper_demo.py`：demo 演示脚本

## 📌 注意

- 插件依赖网络请求 https://itunes.apple.com，请确保机器能访问该接口。
- 单次抓取默认最多200条榜单，超出会自动截断。
