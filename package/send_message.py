import aiohttp
import asyncio
import logging
from package import get_config


class Message:
    loop: asyncio.AbstractEventLoop

    def __init__(
        self, loop, config: get_config.GetConfig, logger: logging.Logger
    ) -> None:
        self.loop = loop
        self.config = config
        self.logger = logger

        self.telegram_config = config.config["Telegram"]
        self.serverchan_config = config.config["ServerChan"]
        self.wxpusher_config = config.config["WxPusher"]
        self.pushplus_config = config.config["PushPlus"]
        self.qmsg_config = config.config["Qmsg"]
        self.global_proxy = config.config["PROXY"]

    async def Telegram(self, content: str) -> bool:
        url = (
            "https://api.telegram.org/bot%s/sendMessage"
            % self.telegram_config["bot_token"]
        )
        data = {"chat_id": self.telegram_config["user_id"], "text": content}
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(
                    url,
                    data=data,
                    timeout=3,
                    proxy=self.telegram_config["proxy"] or self.global_proxy,
                )
            return True
        except Exception:
            self.logger.exception("Telegram 推送失败")
            return False

    async def ServerChan(self, summary: str, content: str) -> bool:
        url = "https://sctapi.ftqq.com/%s.send" % self.serverchan_config["token"]
        if not summary:
            data = {"text": content, "desp": content}
        else:
            data = {"text": summary, "desp": content}
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(
                    url,
                    data=data,
                    timeout=3,
                    proxy=self.serverchan_config["proxy"] or self.global_proxy,
                )
            return True
        except Exception:
            self.logger.exception("ServerChan 推送失败")
            return False

    async def WxPusher(self, summary: str, content: str) -> bool:
        url = "http://wxpusher.zjiecode.com/api/send/message"
        data = {
            "appToken": self.wxpusher_config["appToken"],
            "content": content,
            "summary": summary,  # 消息摘要，显示在微信聊天页面或者模版消息卡片上，限制长度100，可以不传，不传默认截取content前面的内容。
            "contentType": self.wxpusher_config[
                "contentType"
            ],  # 内容类型 1表示文字  2表示html(只发送body标签内部的数据即可，不包括body标签) 3表示markdown
            "topicIds": self.wxpusher_config[
                "topicIds"
            ],  # 发送目标的topicId，是一个数组！！！，也就是群发，使用uids单发的时候， 可以不传。
            "uids": self.wxpusher_config[
                "uids"
            ],  # 发送目标的UID，是一个数组。注意uids和topicIds可以同时填写，也可以只填写一个。
            "url": self.wxpusher_config["url"],  # 原文链接，可选参数
        }
        if summary == "":
            del data["summary"]
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(
                    url,
                    json=data,
                    timeout=3,
                    proxy=self.wxpusher_config["proxy"] or self.global_proxy,
                )
            return True
        except Exception:
            self.logger.exception("WxPusher 推送失败")
            return False

    async def PushPlus(self, title: str, content: str) -> bool:
        url = "http://www.pushplus.plus/send"
        data = {"token": self.pushplus_config["token"], "content": content}
        if title:
            data["title"] = title
        for v in ["title", "template", "topic", "channel", "webhook", "callbackUrl"]:
            if self.pushplus_config[v]:
                data[v] = self.pushplus_config[v]
        try:
            async with aiohttp.ClientSession() as session:
                await session.get(
                    url,
                    json=data,
                    timeout=3,
                    proxy=self.pushplus_config["proxy"] or self.global_proxy,
                )
            return True
        except Exception:
            self.logger.exception("PushPlus 推送失败")
            return False

    async def Qmsg(self, content: str) -> bool:
        url = "https://qmsg.zendee.cn/send/" + self.qmsg_config["key"]
        data = {"msg": content}
        if self.qmsg_config["qq"] and len(self.qmsg_config["qq"]) != 0:
            data["qq"] = self.qmsg_config["qq"]

        try:
            async with aiohttp.ClientSession() as session:
                await session.post(
                    url,
                    data=data,
                    timeout=3,
                    proxy=self.qmsg_config["proxy"] or self.global_proxy,
                )
                return True
        except Exception:
            self.logger.exception("Qmsg 推送失败")
            return False
