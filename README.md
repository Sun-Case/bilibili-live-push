# Bilibili live push
哔哩哔哩（Bilibili）直播通知提醒

#### 由于用到格式控制符，最好在 Linux终端 下使用

#### 目前来看代码要完善的地方很多，所以使用过程中出现问题请稍安勿躁，可提交 Issues

#### 关于推送方式
1. **Server酱** 暂时不支持，新API还没用过，需要测试
2. 目前有想法实现 **一对多推送** [Issues #2](issues/2)
3. 如果有其他推送方式，欢迎提出来

## 使用方法

1. 安装所需库：`pip install aiohttp` 或 `pip install -r requirements.txt`
2. 首次运行，会在 **工作路径** 生成 **4**个文件，文件名及作用如下
    1. **直播间ID.txt**
        - 存放需要检测的直播间ID
    2. **config.json**
        - 配置文件，用于配置通知方式
    3. **开播通知模板.txt**
        - 用于生成信息，到时候发送的消息就来源于该模板
    4. **下播通知模板.txt**
        - 同上
3. 配置 **直播间ID.txt**
    1. 每行放一个直播间ID
    2. 直播间ID在URL有，如：`https://live.bilibili.com/一串数字`，这一串数字就是直播间ID
    3. `#` 开头为注释，当然如果行内有非数字的字符，也会跳过整行
4. 配置 **config.json**
    1. `Telegram` 字段用于配置 **Telegram** 推送
        1. 将 `status` 置 `true` 即可开启 Telegram推送
        2. `bot_token` 为 **你的 机器人Token**
        3. `user_id` 为 **你的 Telegram账号 ID**
        4. 请确保运行此程序的计算机能访问 Telegram，否则无法发送消息
    2. `ServerChan` 字段用于配置 **Server酱** 推送
        1. 将 `status` 置 `true` 即可开启推送
        2. `token` 是 **你的 SendKey**, 在 [https://sct.ftqq.com/sendkey](https://sct.ftqq.com/sendkey)
    2. `SSL` 字段用于处理 aiohttp 出现 SSL证书错误
        1. 如果出现错误，则需要 置为 `false`
    3. `LIVE` 字段用于开启开播提醒，如果 置为 `false`，则开播不提醒
    4. `PREPARING` 字段用于开启下播提醒，如果 置为 `false`，则下播不提醒
5. 配置 **开播通知模板** 及 **下播通知模板**
    1. 关键字用 **花括号** 括起来, 然后 **左花括号** 前面加上美元符号`$`，在生成消息时会替换为相应数据
    2. 目前能用的关键字为
        1. **`${name}`**: 主播名
        2. **`${room_id}`**: 直播间ID
        3. **`${true_room}`**: 直播间真实ID
        4. **`${uid}`**: 主播UID
        5. **`${YYYY}`**: 年
        6. **`${mm}`**: 月
        7. **`${dd}`**: 日
        8. **`${HH}`**: 时
        9. **`${MM}`**: 分
        10. **`${SS}`**: 秒

## 原理
1. 连接B站直播间的弹幕服务器，主播开播及下播时，B站发送数据到观众；开播为 `LIVE`，下播为 `PREPARING`
2. 定时请求B站API，获取直播间的直播状态，以避免弹幕服务器在断开时，主播开播/下播，导致跳过通知

## 代码来源
1. 弹幕数据解析参考了 [blivedm](https://github.com/xfgryujk/blivedm) 的代码
