import asyncio
from io import SEEK_SET
import time
from package import dm, send_message, get_config, echo
import os
import json


roomid_file = "直播间ID.txt"  # 存放要提醒的直播间ID的文件
config_file = "config.json"  # 存放配置数据的文件
live_file = "开播通知模板.txt"  # 开播通知模板
preparing_file = "下播通知模板.txt"  # 下播通知模板

tasks = []
roomid_list = []
config = {}

live_template = "【${name}】 room_id: ${room_id}, true_id: ${true_room}, uid: ${uid} 开播啦"
preparing_template = (
    "【${name}】 room_id: ${room_id}, true_id: ${true_room}, uid: ${uid} 下播啦"
)


def Init(roomid_file: str):
    status = True
    global roomid_list, config, live_template, preparing_template
    # 读取要提醒的直播间ID
    if os.path.exists(roomid_file):
        with open(roomid_file, "r", encoding="utf-8") as r:
            roomid_list = get_config.get_roomid(r.read())
        print("直播间ID读取成功")
    else:
        with open(roomid_file, "w", encoding="utf-8") as w:
            w.write(get_config.roomid_bak)
        print("直播间ID文件不存在，已为你生成文件，请打开文件添加直播间ID:", roomid_file)
        status = False

    # 读取配置文件
    if os.path.exists(config_file):
        with open(config_file, "r+", encoding="utf-8") as rw:
            try:
                config = json.loads(rw.read())
                print("配置文件读取成功")
            except Exception as e:
                print("似乎无法读取配置文件的数据", e)
                rw.seek(0, SEEK_SET)
                rw.truncate()
                rw.write(get_config.config_bak)
                print("已为你生成新配置文件，请打开文件进行配置:", config_file)
                status = False
    else:
        with open(config_file, "w", encoding="utf-8") as w:
            w.write(get_config.config_bak)
        print("配置文件不存在，已为你生成文件，请打开文件进行配置:", config_file)
        status = False

    # 读取通知模板
    if os.path.exists(live_file):
        with open(live_file, "r+", encoding="utf-8") as r:
            live_template = r.read()
    else:
        with open(live_file, "w", encoding="utf-8") as w:
            w.write(live_template)
        print("开播通知模板不存在，已为你生成文件")
    if os.path.exists(preparing_file):
        with open(preparing_file, "r+", encoding="utf-8") as r:
            preparing_template = r.read()
    else:
        with open(preparing_file, "w", encoding="utf-8") as w:
            w.write(preparing_template)
        print("下播通知模板不存在，以为你生成文件")

    return status


if __name__ == "__main__":
    if Init(roomid_file) is False:
        exit(0)

    print("")
    echo.echoConfig(config)

    print("")
    echo.echo(
        [["#", "直播间ID"]]
        + [["%s" % (i + 1), "%s" % v] for i, v in enumerate(roomid_list)]
    )
    print("")

    print("添加任务")

    loop = asyncio.get_event_loop()
    q = asyncio.Queue()
    echoQ = asyncio.Queue()

    for i in roomid_list:
        tasks.append(dm.DM(i, q, loop, config.get("SSL", None), echoQ).run())

    for i in range(2, -1, -1):
        print("\r添加完成，即将启动 %s" % i, end="", flush=True)
        time.sleep(1)
    print("\n")

    # 输出由 ECHO 接管
    tasks.append(asyncio.ensure_future(echo.ECHO(echoQ, loop).run()))
    tasks.append(
        asyncio.ensure_future(
            send_message.Message(
                q, loop, config, roomid_list, live_template, preparing_template, echoQ
            ).run()
        )
    )
    loop.run_until_complete(asyncio.wait(tasks))
