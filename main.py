import asyncio
from string import Template
import time
from package import dm, send_message, get_config, echo
import logging

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.WARN)
handler = logging.FileHandler("run.log")
formatter = logging.Formatter(
    "%(asctime)s - %(module)s - %(funcName)s - %(levelname)s - %(lineno)d - %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


config_file = "config.json"  # 存放配置数据的文件

tasks = []

# 所有直播间数据统一处理
class Process:
    def __init__(self, logger: logging.Logger, config: get_config.GetConfig) -> None:
        self.logger: logging.Logger = logger
        self.config = config
        self.loop = asyncio.get_event_loop()

        self.echoQ = asyncio.Queue()

        self.echo = echo.EchoFormat()

        self.send_message = send_message.Message(self.loop, config, logger)

        self.live_template = Template(config.template["live_template"])
        self.preparing_template = Template(config.template["preparing_template"])
        self.telegram_config = config.config["Telegram"]
        self.serverchan_config = config.config["ServerChan"]
        self.wxpusher_config = config.config["WxPusher"]
        self.pushplus_config = config.config["PushPlus"]
        self.qmsg_config = config.config["Qmsg"]

        self.live_status = {}
        self.tasks = []
        self.echo.init_th("#", "直播间ID", "直播间真实ID", "主播名", "开播/下播", "实时状态")

    def create_tasks(self):
        self.config.roomid_list.sort()
        for i in self.config.roomid_list:  # type: int
            # 创建 td
            id_, _ = self.echo.create_td()
            # 创建 dm
            task = dm.DM(
                i, id_, self.logger, self.loop, self.config.config["SSL"], self.echoQ
            )
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
                        if (data["data"] is True and self.config.config["LIVE"]) or (
                            data["data"] is False and self.config.config["PREPARING"]
                        ):
                            self.loop.create_task(self.send_msg(data))
            except Exception:
                self.logger.exception("日志显示错误")

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
                title=data["title"],
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
                title=data["title"],
            )

        # 推送消息
        if self.telegram_config["status"]:
            self.loop.create_task(self.__telegram__(data, content))
        if self.serverchan_config["status"]:
            self.loop.create_task(
                self.__server_chan__(data, self.serverchan_config["summary"], content)
            )
        if self.wxpusher_config["status"]:
            self.loop.create_task(
                self.__wx_pusher__(data, self.wxpusher_config["summary"], content)
            )
        if self.pushplus_config["status"]:
            self.loop.create_task(
                self.__push_plus__(data, self.pushplus_config["title"], content)
            )
        if self.qmsg_config["status"]:
            self.loop.create_task(self.__qmsg__(data, content))

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

    async def __server_chan__(self, data: dict, summary: str, content: str):
        for i in range(3):
            rt = await self.send_message.ServerChan(summary, content)
            data["code"] = 0
            data["time"] = time.time()
            if rt:
                data["data"] = "Server Chan 推送成功"
                await self.echoQ.put(data)
                break
            else:
                data["data"] = "Server Chan 第 %s 次推送失败" % (i + 1)
                await self.echoQ.put(data)

    async def __wx_pusher__(self, data: dict, summary: str, content: str):
        for i in range(3):
            rt = await self.send_message.WxPusher(summary, content)
            data["code"] = 0
            data["time"] = time.time()
            if rt:
                data["data"] = "WxPusher 推送成功"
                await self.echoQ.put(data)
                break
            else:
                data["data"] = "WxPusher 第 %s 次推送失败" % (i + 1)
                await self.echoQ.put(data)

    async def __push_plus__(self, data: dict, title: str, content: str):
        for i in range(3):
            rt = await self.send_message.PushPlus(title, content)
            data["code"] = 0
            data["time"] = time.time()
            if rt:
                data["data"] = "PushPlus 推送成功"
                await self.echoQ.put(data)
                break
            else:
                data["data"] = "PushPlus 第 %s 次推送失败" % (i + 1)
                await self.echoQ.put(data)

    async def __qmsg__(self, data: dict, content: str):
        for i in range(3):
            rt = await self.send_message.Qmsg(content)
            data["code"] = 0
            data["time"] = time.time()
            if rt:
                data["data"] = "Qmsg 推送成功"
                await self.echoQ.put(data)
                break
            else:
                data["data"] = "Qmsg 第 %s 次推送失败" % (i + 1)
                await self.echoQ.put(data)

    def run(self):
        self.create_tasks()
        self.tasks.append(self.loop_echo())
        self.tasks.append(self.echo.loop())
        self.loop.run_until_complete(asyncio.wait(self.tasks))


if __name__ == "__main__":
    config = get_config.GetConfig(logger, config_file)
    status_list = [config.get_config(), config.get_roomid_list(), config.get_template()]
    if False in status_list:
        exit(0)

    process = Process(logger, config)
    process.run()
