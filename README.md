# Bilibili_Live_Notice
哔哩哔哩（Bilibili）直播通知提醒

## 准备模块
1. 安装模块：`aiohttp` 或 `pip install -r requirements.txt`

## 配置 （主要编辑 `main.py` 文件）
- 添加直播间
  - `room_list` 内添加直播间ID。**整数类型，不要用 *引号* 括起来**
- 配置提醒方式
  - Telegram
    - 令 `tg = True`
    - `tg_token` 为 **Telegram机器人 的 Token**
    - `tg_id` 为 **Telegram个人账号 的 ID**
  - 微信提醒
    - [Server酱](http://sc.ftqq.com/3.version)
      - 令 `sc = True`
      - `sc_token` 为 **Server酱 的 Token**
- 模板（可选配置）
  - **通知提醒** 的 **标题** 和 **内容** 对应的模板为 `live_title` 和 `live_content`
  - 占位符
    - name: 主播名字
    - status: **开播** 或 **下播**
      - 可修改 `kv` 对应的值，从而改变生成的内容
    - time: 开播/下播 时间
      - 默认格式是 `年-月-日 时:分:秒`,可修改 `now_time` 函数的返回值

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
