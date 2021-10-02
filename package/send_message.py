import aiohttp
import asyncio


class Message:
    loop: asyncio.AbstractEventLoop

    def __init__(self, loop, config: dict) -> None:
        self.loop = loop
        self.config = config

    async def Telegram(self, content: str) -> bool:
        url = (
            "https://api.telegram.org/bot%s/sendMessage"
            % self.config["Telegram"]["bot_token"]
        )
        data = {"chat_id": self.config["Telegram"]["user_id"], "text": content}
        async with aiohttp.ClientSession() as session:
            try:
                await session.post(
                    url,
                    data=data,
                    timeout=3,
                    proxy=self.config["Telegram"]["proxy"] or self.config["PROXY"],
                )
                return True
            except:
                return False

    async def ServerChan(self, title: str, content: str) -> bool:
        url = "https://sctapi.ftqq.com/%s.send" % self.config["ServerChan"]["token"]
        data = {"text": title, "desp": content}
        async with aiohttp.ClientSession() as session:
            try:
                await session.post(
                    url,
                    data=data,
                    timeout=3,
                    proxy=self.config["ServerChan"]["proxy"] or self.config["PROXY"],
                )
                return True
            except:
                return False
