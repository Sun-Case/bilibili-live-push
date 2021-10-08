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

    async def ServerChan(self, summary: str, content: str) -> bool:
        url = "https://sctapi.ftqq.com/%s.send" % self.config["ServerChan"]["token"]
        if self.config["ServerChan"]["use_content_as_summary"]:
            data = {"text": content, "desp": content}
        else:
            data = {"text": summary, "desp": content}
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

    async def WxPusher(self, summary: str, content: str) -> bool:
        url = "http://wxpusher.zjiecode.com/api/send/message"
        data = {
            "appToken": self.config["WxPusher"]["appToken"],
            "content": content,
            "summary": summary,  # 消息摘要，显示在微信聊天页面或者模版消息卡片上，限制长度100，可以不传，不传默认截取content前面的内容。
            "contentType": self.config["WxPusher"][
                "contentType"
            ],  # 内容类型 1表示文字  2表示html(只发送body标签内部的数据即可，不包括body标签) 3表示markdown
            "topicIds": self.config["WxPusher"][
                "topicIds"
            ],  # 发送目标的topicId，是一个数组！！！，也就是群发，使用uids单发的时候， 可以不传。
            "uids": self.config["WxPusher"][
                "uids"
            ],  # 发送目标的UID，是一个数组。注意uids和topicIds可以同时填写，也可以只填写一个。
            "url": self.config["WxPusher"]["url"],  # 原文链接，可选参数
        }
        if summary == "":
            del data["summary"]
        async with aiohttp.ClientSession() as session:
            try:
                await session.post(
                    url,
                    json=data,
                    timeout=3,
                    proxy=self.config["WxPusher"]["proxy"] or self.config["PROXY"],
                )
                return True
            except:
                return False

    async def PushPlus(self, title: str, content: str) -> bool:
        url = "http://www.pushplus.plus/send"
        data = {"token": self.config["PushPlus"]["token"], "content": content}
        if title:
            data["title"] = title
        for v in ["title", "template", "topic", "channel", "webhook", "callbackUrl"]:
            if self.config["PushPlus"].get(v, ""):
                data[v] = self.config["PushPlus"][v]
        async with aiohttp.ClientSession() as session:
            try:
                await session.get(
                    url,
                    json=data,
                    timeout=3,
                    proxy=self.config["PushPlus"]["proxy"] or self.config["PROXY"],
                )
                return True
            except:
                return False

    async def Qmsg(self, content: str) -> bool:
        url = "https://qmsg.zendee.cn/send/" + self.config["Qmsg"]["key"]
        data = {"msg": content}
        if self.config["Qmsg"]["qq"] and len(self.config["Qmsg"]["qq"]) != 0:
            data["qq"] = self.config["Qmsg"]["qq"]

        async with aiohttp.ClientSession() as session:
            try:
                await session.post(
                    url,
                    data=data,
                    timeout=3,
                    proxy=self.config["Qmsg"]["proxy"] or self.config["PROXY"],
                )
                return True
            except Exception as e:
                return False
