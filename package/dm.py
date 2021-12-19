import logging
import aiohttp
import asyncio
import time
import struct
import json
import zlib
from collections import namedtuple
from package.utile import get_name, get_live, get_room_title


class DM:
    timestamp: int = 0
    room_id: int = 0
    uid: int = 0
    name: str = ""
    serve_list = []
    token = ""
    ws = None
    HEADER_STRUCT = struct.Struct(">I2H2I")
    HeaderTuple = namedtuple(
        "HeaderTuple", ("pack_len", "raw_header_size", "ver", "operation", "seq_id")
    )
    heart_beat = 2
    popularity = 3
    msg = 5
    first_shake = 7
    h_b = 8
    api_check_sleep = 60

    def __init__(
        self,
        room_id: int,
        id_: int,
        logger: logging.Logger,
        loop=None,
        ssl=None,
        echo_queue=None,
    ):
        self._room_id: int = room_id
        if loop is None:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = loop
        self.ssl = ssl
        self.echo_queue = echo_queue
        self.id_ = id_
        self.logger = logger

    async def run(self):
        try:
            await self.__init_room__()
            await self.__get_dm_conf__()
            self.loop.create_task(self.__api__check__())
            while True:
                for value in self.serve_list:
                    try:
                        await self.__ws__(serve=value["host"], port=value["wss_port"])
                    except Exception:
                        self.logger.exception("与弹幕服务器断开连接")
                    await self.__echo__(0, "与弹幕服务器断开连接")
                await self.__init_room__()
                await self.__get_dm_conf__()
        except Exception as e:
            self.logger.error("run failure", exc_info=e)

    async def __api__check__(self):
        while True:
            await self.__echo__(0, "API Check")
            status, room_id, live, _ = await get_live(
                room_id=self._room_id, logger=self.logger
            )
            if status:
                self.room_id = room_id
                if live == 1:  # 开播
                    await self.__echo__(4, True)
                elif live == 0:  # 下播
                    await self.__echo__(4, False)
                await self.__echo__(0, "API Check 成功")
            else:
                await self.__echo__(0, "API Check 失败")
            await asyncio.sleep(self.api_check_sleep)

    async def __ws__(self, serve, port):
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(
                "wss://%s:%s/sub" % (serve, port), ssl=self.ssl
            ) as ws:
                self.timestamp = int(time.time())
                self.ws = ws
                await self.__first_shake__()
                self.loop.create_task(self.__heart_beat__())
                async for msg in ws:  # type: aiohttp.WSMessage
                    if msg.type == aiohttp.WSMsgType.BINARY:
                        await self.__ws_message__(data=msg.data)

    async def __ws_message__(self, data: bytes):
        offset = 0
        while offset < len(data):
            try:
                header = self.HeaderTuple(*self.HEADER_STRUCT.unpack_from(data, offset))
            except struct.error:
                break
            if header.operation == self.popularity:
                popularity = int.from_bytes(
                    data[
                        offset
                        + self.HEADER_STRUCT.size : offset
                        + self.HEADER_STRUCT.size
                        + 4
                    ],
                    "big",
                )
                await self.__echo__(0, "人气: %s" % popularity)
            elif header.operation == self.msg:
                body = data[offset + self.HEADER_STRUCT.size : offset + header.pack_len]
                if header.ver == 2:
                    body = zlib.decompress(body)
                    await self.__ws_message__(body)
                else:
                    body = json.loads(body.decode("utf-8"))
                    if body.get("cmd") == "LIVE":  # 开播
                        await self.__echo__(4, True)
                    elif body.get("cmd") == "PREPARING":  # 下播
                        await self.__echo__(4, False)
            elif header.operation == self.h_b:
                await self.__echo__(0, "心跳包")
                task = self.ws.send_bytes(
                    self.__encode_pack__("[object Object]", self.heart_beat)
                )
                self.loop.create_task(task)
            offset += header.pack_len

    async def __heart_beat__(self):
        timestamp = self.timestamp
        while timestamp == self.timestamp:
            try:
                await self.__echo__(0, "定时心跳包")
                await self.ws.send_bytes(
                    self.__encode_pack__("[object Object]", self.heart_beat)
                )
            except:
                break
            await asyncio.sleep(30)

    async def __first_shake__(self):
        data = {
            "uid": 0,
            "roomid": self.room_id,
            "protover": 2,
            "platform": "web",
            "clientver": "1.14.0",
            "type": 2,
            "key": self.token,
        }
        body = json.dumps(data, ensure_ascii=False)
        await self.ws.send_bytes(self.__encode_pack__(body, self.first_shake))

    def __encode_pack__(self, data: str, operation: int):
        body = data.encode("utf-8")
        header = self.HEADER_STRUCT.pack(
            self.HEADER_STRUCT.size + len(body),
            self.HEADER_STRUCT.size,
            1,
            operation,
            1,
        )
        return header + body

    async def __get_dm_conf__(self):
        await self.__echo__(0, "获取弹幕服务器地址")

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.live.bilibili.com/room/v1/Danmu/getConf"
            ) as resp:
                response = await resp.json()
                if not isinstance(response.get("data"), dict):
                    await self.__echo__(0, "获取弹幕信息失败")
                elif not response["data"].get("token"):
                    await self.__echo__(0, "获取 token 失败")
                elif not response["data"].get("host_server_list"):
                    await self.__echo__(0, "获取弹幕地址失败")
                else:
                    self.token = response["data"]["token"]
                    self.serve_list = response["data"]["host_server_list"]

        await self.__echo__(0, "获取完成")

    async def __init_room__(self):
        await self.__echo__(0, "初始化直播间数据")

        status, room_id, _, uid = await get_live(
            room_id=self._room_id, logger=self.logger
        )
        if status is False:
            await self.__echo__(0, "无法获取直播间真实ID")

        self.uid = uid
        status, name = await get_name(uid=uid, room_id=self._room_id)
        if status is False:
            await self.__echo__(0, "无法获取主播名字")

        self.name = self.name or name or "%s" % uid
        self.name = self.name.replace("\t", "").replace("\r", "")
        self.room_id = room_id

        await self.__echo__(3, self.name)
        await self.__echo__(2, str(self.room_id))
        await self.__echo__(1, str(self._room_id))
        await self.__echo__(0, "初始化完成")

    async def __echo__(self, type_: int, data: str):
        """
        type_:
            0: 日志显示
            1: 直播间ID
            2: 直播间真实ID
            3: 主播名字
            4: 直播状态
        """

        # 获取标题
        status, title = await get_room_title(self.room_id)

        if self.echo_queue:
            await self.echo_queue.put(
                {
                    "code": type_,
                    "data": data,
                    "room id": self._room_id,
                    "true id": self.room_id,
                    "id": self.id_,
                    "name": self.name,
                    "uid": self.uid,
                    "time": time.time(),
                    "title": title,
                }
            )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    q = asyncio.Queue()
    tasks = [asyncio.ensure_future(DM(room_id=931774, loop=loop).run())]
    loop.run_until_complete(asyncio.wait(tasks))
