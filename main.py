import asyncio
import time
from package import dm, send_message
from string import Template

"""
需要 aiohttp 模块进行 WebSocket 连接
弹幕数据解析参考了 https://github.com/xfgryujk/blivedm 的代码

room_list
    type: list
    直播间id，整数型

提醒方式：
    1. Telegram
    2. Server酱（通过微信提醒）【http://sc.ftqq.com/3.version】

  Telegram：
    tg: 启用则 True，否则 False
    tg_token: 你的 Bot 的 token
    tg_id: 你的tg账号的 id

  Server酱：
    sc: 启用则 True，否则 False
    sc_token: 你的 SCKEY
"""


def now_time() -> str:
    nt = time.strftime(u'%Y年%m月%d日 %H:%M:%S'.encode('unicode_escape').decode('utf8'),
                       time.localtime()).encode('utf-8').decode('unicode_escape')
    return nt


# 标题模板
live_title = "【${name}】 ${status}"
# 内容模板
live_content = "【${name}】 ${status}\n${time}"

template_title = Template(live_title)
template_content = Template(live_content)

kv = {
    "LIVE": "开播啦",
    "PREPARING": "下播啦",
    "time": now_time
}

room_list = [  # 房间ID，每个ID用 英文逗号 隔开
    931774
]

tg = False  # 是否使用 Telegram 通知
sc = False  # 是否使用 Server酱 通知
tg_token = ''  # Telegram机器人 的 Token
tg_id = ''  # Telegram账号 的 ID
sc_token = ''  # Server酱 的 Token

ssl = None  # SSL

room_result = {}
tasks = []


async def get_message(queue):
    s_m = send_message.SessionAio(tg_token=tg_token, tg_id=tg_id, sc_token=sc_token, loop=loop)
    while True:
        data = await queue.get()
        print(data)
        if (data['live_status'] == 'LIVE' and room_result[data['room_id']] is True) or \
                (data['live_status'] == 'PREPARING' and room_result[data['room_id']] is False):
            continue
        if data['live_status'] == 'LIVE':
            room_result[data['room_id']] = True
        else:
            room_result[data['room_id']] = False
        template_data = {
            "name": data["name"],
            "status": kv[data["live_status"]],
            "time": now_time()
        }
        text = template_content.safe_substitute(template_data)
        title = template_title.safe_substitute(template_data)
        await s_m.send(tg=tg, sc=sc, sc_title=title, text=text)


if __name__ == '__main__':
    q = asyncio.Queue()
    loop = asyncio.get_event_loop()
    for room_id in room_list:
        room_result[room_id] = False
        task = asyncio.ensure_future(dm.DM(room_id=room_id, loop=loop, queue=q, ssl=ssl).run())
        tasks.append(task)
    tasks.append(asyncio.ensure_future(get_message(queue=q)))
    loop.run_until_complete(asyncio.wait(tasks))
