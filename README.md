# Bilibili_Live_Notice
哔哩哔哩（Bilibili）直播通知提醒

## 准备模块
1. 安装模块：`aiohttp` 或 `pip install -r requirements.txt`

## 设置提示方式
* 编辑 `main.py` 文件，`room_list` 内添加直播间ID，选择提示方式，并配置好 `token`
1. Telegram【需要获取 账号的ID，及 Bot 的 Token】
2. [Server酱](http://sc.ftqq.com/3.version) 【通过微信提醒】

## 运行
1. 运行 `main.py` 文件，`python ./main.py`
2. 检查是否能正常运行，确保不会出现不断重连

## 注意事项
1. aiohttp 可能会出现 SSL证书错误（我没遇到过），需要将 `main.py` 的 `ssl = False`
2. 代码在 Python3.6 及 Python3.7 成功运行

## 原理
1. 连接B站直播间的弹幕服务器，主播开播及下播时，B站发送数据到观众；开播为 `LIVE`，下播为 `PREPARING`
2. 定时请求B站API，获取直播间的直播状态，以避免弹幕服务器在断开时，主播开播/下播，导致跳过通知

## 代码来源
1. 弹幕数据解析参考了 [blivedm](https://github.com/xfgryujk/blivedm) 的代码

## 其他
1. 自学编程，可能有不完善的方面，还需要改进
