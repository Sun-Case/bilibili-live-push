import asyncio
from io import SEEK_SET
from string import Template
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

live_template = "【${name}】 room_id: ${room_id}, true_id: ${true_room}, uid: ${uid} 开播啦 时间: ${YYYY}-${mm}-${dd} ${HH}:${MM}:${SS}"
preparing_template = "【${name}】 room_id: ${room_id}, true_id: ${true_room}, uid: ${uid} 下播啦 开播啦 时间: ${YYYY}-${mm}-${dd} ${HH}:${MM}:${SS}"


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
                # 合并并保存配置文件
                config = {**json.loads(get_config.config_bak), **config}
                rw.seek(0, SEEK_SET)
                rw.truncate()
                rw.write(json.dumps(config, ensure_ascii=False, indent=4))
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


# 所有直播间数据统一处理
class Process:
    def __init__(self) -> None:
        self.loop = asyncio.get_event_loop()
        self.echoQ = asyncio.Queue()
        self.echo = echo.EchoFormat()
        self.send_message = send_message.Message(self.loop, config)
        self.live_template = Template(live_template)
        self.preparing_template = Template(preparing_template)
        self.live_status = {}
        self.tasks = []
        self.echo.init_th("#", "直播间ID", "直播间真实ID", "主播名", "开播/下播", "实时状态")

    def create_tasks(self):
        roomid_list.sort()
        for i in roomid_list:  # type: int
            # 创建 td
            id_, _ = self.echo.create_td()
            # 创建 dm
            task = dm.DM(i, id_, self.loop, config.get("SSL", None), self.echoQ)
            self.echo.update_element(id_, 0, str(id_ + 1))
            self.tasks.append(task.run())
            self.live_status[id_] = False
        self.tasks.append(self.echo.loop())

    async def loop_echo(self):
        while True:
            data: dict = await self.echoQ.get()
            try:
                if data["code"] == 0:  # 日志显示
                    self.echo.update_element(
                        data["id"],
                        5,
                        time.strftime("%H:%M:%S", time.localtime(data["time"]))
                        + "  "
                        + data["data"],
                    )
                elif data["code"] == 1:  # 直播间ID
                    self.echo.update_element(data["id"], 1, data["data"])
                elif data["code"] == 2:  # 直播间真实ID
                    self.echo.update_element(data["id"], 2, data["data"])
                elif data["code"] == 3:  # 主播名
                    self.echo.update_element(data["id"], 3, data["data"])
                elif data["code"] == 4:  # 直播状态
                    self.echo.update_element(
                        data["id"], 4, "直播" if data["data"] else "下播"
                    )
                    if (
                        self.live_status[data["id"]] is False and data["data"] is True
                    ) or (
                        self.live_status[data["id"]] is True and data["data"] is False
                    ):
                        # 开播 or 下播
                        self.live_status[data["id"]] = data["data"]
                        self.loop.create_task(self.send_msg(data))
            except Exception as e:
                print(e)

    async def send_msg(self, data: dict):
        # 生成 年月日时分秒
        YYYY = time.strftime("%Y", time.localtime(data["time"]))
        mm = time.strftime("%m", time.localtime(data["time"]))
        dd = time.strftime("%d", time.localtime(data["time"]))
        HH = time.strftime("%H", time.localtime(data["time"]))
        MM = time.strftime("%M", time.localtime(data["time"]))
        SS = time.strftime("%S", time.localtime(data["time"]))
        # 根据模板生成内容
        if data["data"]:
            content = self.live_template.safe_substitute(
                name=data["name"],
                room_id=data["room id"],
                true_room=data["true id"],
                uid=data["uid"],
                YYYY=YYYY,
                mm=mm,
                dd=dd,
                HH=HH,
                MM=MM,
                SS=SS,
            )
        else:
            content = self.preparing_template.safe_substitute(
                name=data["name"],
                room_id=data["room id"],
                true_room=data["true id"],
                uid=data["uid"],
                YYYY=YYYY,
                mm=mm,
                dd=dd,
                HH=HH,
                MM=MM,
                SS=SS,
            )

        # 推送消息
        if (
            "Telegram" in config
            and "status" in config["Telegram"]
            and config["Telegram"]["status"]
        ):
            self.loop.create_task(self.__telegram__(data, content))
        if (
            "ServerChan" in config
            and "status" in config["ServerChan"]
            and config["ServerChan"]["status"]
        ):
            self.loop.create_task(self.__server_chan__(data, content))

    async def __telegram__(self, data: dict, content: str):
        for i in range(3):
            rt = await self.send_message.Telegram(content)
            data["code"] = 0
            data["time"] = time.time()
            if rt:
                data["data"] = "Telegram 推送成功"
                await self.echoQ.put(data)
                break
            else:
                data["data"] = "Telegram 第 %s 次推送失败" % (i + 1)
                await self.echoQ.put(data)

    async def __server_chan__(self, data: dict, content: str):
        for i in range(3):
            rt = await self.send_message.ServerChan("直播通知", content)
            data["code"] = 0
            data["time"] = time.time()
            if rt:
                data["data"] = "Server Chan 推送成功"
                await self.echoQ.put(data)
                break
            else:
                data["data"] = "Server Chan 第 %s 次推送失败" % (i + 1)
                await self.echoQ.put(data)

    def run(self):
        self.create_tasks()
        self.tasks.append(self.loop_echo())
        self.tasks.append(self.echo.loop())
        self.loop.run_until_complete(asyncio.wait(self.tasks))


if __name__ == "__main__":
    if Init(roomid_file) is False:
        exit(0)

    process = Process()
    process.run()
