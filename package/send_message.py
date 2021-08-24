import aiohttp
import asyncio
from string import Template


class Message:
    loop: asyncio.AbstractEventLoop

    def __init__(
        self,
        q: asyncio.Queue,
        loop,
        config: dict,
        room_list: list,
        live_template: str,
        preparing_template: str,
        echoQ,
    ) -> None:
        self.q = q
        self.loop = loop
        self.config = config
        self.room_status = {}
        self.live_template = Template(live_template)
        self.preparing_template = Template(preparing_template)
        self.echoQ = echoQ

        for i in room_list:
            self.room_status[i] = False

    async def run(self):
        while True:
            data = await self.q.get()
            if data["status"] != self.room_status[data["room_id"]]:
                self.room_status[data["room_id"]] = data["status"]
                if data["status"] is True and self.config["LIVE"] is False:
                    continue
                if data["status"] is False and self.config["PREPARING"] is False:
                    continue
                content = self.__content__(
                    data["name"],
                    data["status"],
                    data["room_id"],
                    data["true_room"],
                    data["uid"],
                )
                for k, v in self.config.items():
                    if k == "Telegram" and v["status"]:
                        self.loop.create_task(self.Telegram(content, data["room_id"]))
                    if k == "ServerChan" and v["status"]:
                        self.loop.create_task(self.ServerChan(content, data["room_id"]))

    def __content__(
        self, name: str, status: bool, room_id: int, true_room: int, uid: int
    ):
        if status:
            content = self.live_template.safe_substitute(
                name=name, room_id=room_id, true_room=true_room, uid=uid
            )
        else:
            content = self.preparing_template.safe_substitute(
                name=name, room_id=room_id, true_room=true_room, uid=uid
            )
        return content

    async def Telegram(self, content: str, room_id):
        url = (
            "https://api.telegram.org/bot%s/sendMessage"
            % self.config["Telegram"]["bot_token"]
        )
        data = {"chat_id": self.config["Telegram"]["user_id"], "text": content}
        async with aiohttp.ClientSession() as session:
            for a in range(0, 3):
                try:
                    await session.post(url, data=data, timeout=3)
                    await self.echoQ.put(
                        {"code": 0, "data": "Telegram 发送成功 %s" % (a + 1), "id": room_id}
                    )
                    break
                except:
                    await self.echoQ.put(
                        {"code": 0, "data": "Telegram 发送失败 %s" % (a + 1), "id": room_id}
                    )

    async def ServerChan(self, content: str, room_id):
        # print(content)
        pass
