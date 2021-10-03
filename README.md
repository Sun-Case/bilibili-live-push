# Bilibili live push
哔哩哔哩（Bilibili）直播通知提醒

#### 由于用到格式控制符，最好在 Linux终端 下使用

#### 目前来看代码要完善的地方很多，所以使用过程中出现问题请稍安勿躁，可提交 Issues

#### 关于推送方式
1. 目前有想法实现 **一对多推送** [Issues #2](https://github.com/Sun-Case/bilibili-live-push/issues/2)
2. 如果有其他推送方式，欢迎提出来

## 使用方法

### 安装所需库
- 安装所需库：`pip install aiohttp` 或 `pip install -r requirements.txt`

### 首次运行并配置
-  首次运行，会在 **工作路径** 生成 **4**个文件，文件名及作用如下

| 文件名 | 功能 |
|:-:|:-:|
| 直播间ID.txt | 存放需要检测的直播间ID |
| config.json | 配置文件，用于配置通知方式 |
| 开播通知模板.txt | 用于生成消息<br />到时发送的消息就来源于该模板 |
| 下播通知模板.txt | 同上 |


### 配置 `直播间ID.txt`
1. 每行放一个直播间ID
2. 直播间ID在URL有，如：`https://live.bilibili.com/一串数字`，这一串数字就是直播间ID
3. `#` 开头为注释，当然如果行内有非数字的字符，也会跳过整行

### 配置 `config.json`

#### 配置 `Telegram` 推送
> `Telegram` 字段用于配置 **Telegram** 推送
1. 将 `status` 置 `true` 即可开启 Telegram推送
2. `bot_token` 为 **你的 机器人Token**
3. `user_id` 为 **你的 Telegram账号 ID**
4. `proxy` 为 代理服务器地址，通过代理服务器连接 Telegram服务器
    1. 格式为: `http://host:port`
5. 请确保运行此程序的计算机能访问 Telegram，否则无法发送消息

#### 配置 `ServerChan` 推送
> `ServerChan` 字段用于配置 **Server酱** 推送
1. 将 `status` 置 `true` 即可开启推送
2. `token` 是 **你的 SendKey**, 在 [https://sct.ftqq.com/sendkey](https://sct.ftqq.com/sendkey)
3. `proxy` 为 代理服务器地址，通过代理服务器连接 ServerChan服务器
    1. 格式为 `http://host:port`

#### 解决SSL证书错误
> `SSL` 字段用于处理 aiohttp 出现 SSL证书错误

如果出现错误，则需要 置为 `false`

#### 开启开播、下播通知
> `LIVE` 字段用于开启开播提醒\
> `PREPARING` 字段用于开启下播提醒

如果 置为 `false`，则关闭相应功能

#### 配置全局代理服务器地址
> `PROXY` 为 全局代理服务器地址

格式为 `http://host:port`

### 配置 `开播通知模板.txt` 及 `下播通知模板.txt`
关键字用 **花括号** 括起来, 然后 **左花括号** 前面加上美元符号`$`，在生成消息时会替换为相应数据

#### 目前能用的关键字有

| 关键字 | 功能 |
| :-: | :-: |
| `${name}` | 主播名 |
| `${room_id}` | 直播间ID |
| `${true_room}` | 直播间真实ID |
| `${uid}` | 主播UID |
| `${YYYY}` | 年 |
| `${mm}` | 月 |
| `${dd}` | 日 |
| `${HH}` | 时 |
| `${MM}` | 分 |
| `${SS}` | 秒 |

## 原理
1. 连接B站直播间的弹幕服务器，主播开播及下播时，B站发送数据到观众；开播为 `LIVE`，下播为 `PREPARING`
2. 定时请求B站API，获取直播间的直播状态，以避免弹幕服务器在断开时，主播开播/下播，导致跳过通知

## 代码来源
1. 弹幕数据解析参考了 [blivedm](https://github.com/xfgryujk/blivedm) 的代码
