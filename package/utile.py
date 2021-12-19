import asyncio
import json
from typing import *
import logging
import aiohttp
import re


async def get_room_title(room_id: int = 0) -> Tuple[bool, str]:
    url = "https://live.bilibili.com/%s" % room_id
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ("
                                                           "KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"}) \
                as resp:
            text = await resp.text("utf-8")
            text_re = re.findall(r"window\.__NEPTUNE_IS_MY_WAIFU__=(.*?)<", text)
            if text_re:
                try:
                    text_json = json.loads(text_re[1])
                    return True, text_json["roomInfoRes"]["data"]["room_info"]["title"]
                except Exception:
                    pass
    return False, ""


async def get_name(uid: int = 0, room_id: int = 0) -> tuple:
    uid2name = "https://api.bilibili.com/x/space/acc/info"
    room_id2name = "https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom"
    if not uid and not room_id:
        raise Exception("uid 和 room_id 为空")
    try:
        async with aiohttp.ClientSession() as session:
            if uid:
                async with session.get(uid2name, params={"mid": str(uid)}) as resp:
                    response: dict = await resp.json()
                    if response.get("data") and response["data"].get("name"):
                        return True, response["data"]["name"]
            if room_id:
                async with session.get(
                    room_id2name, params={"room_id": str(room_id)}
                ) as resp:
                    response = await resp.json()
                    if (
                        response.get("data")
                        and response["data"].get("anchor_info")
                        and response["data"]["anchor_info"].get("base_info")
                        and response["data"]["anchor_info"]["base_info"].get("uname")
                    ):
                        return (
                            True,
                            response["data"]["anchor_info"]["base_info"]["uname"],
                        )
            return False, ""
    except Exception:
        return False, ""


async def get_live(
    room_id: int, logger: logging.Logger
) -> Tuple[bool, int, int, int]:  # (获取情况, 直播间真实id, 直播间状态【是否直播，0：离线，1：直播，2：轮播】, 主播uid)
    if not room_id:
        # raise Exception("room_id 为空")
        return False, 0, 0, 0
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.live.bilibili.com/room/v1/Room/room_init",
                params={"id": str(room_id)},
            ) as resp:
                response = await resp.json()
                if (
                    isinstance(response.get("data"), dict)
                    and response["data"].get("room_id")
                    and isinstance(response["data"].get("live_status"), int)
                    and response["data"].get("uid")
                ):
                    return (
                        True,
                        response["data"]["room_id"],
                        response["data"]["live_status"],
                        response["data"]["uid"],
                    )
            async with session.get(
                "https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom",
                params={"room_id": str(room_id)},
            ) as resp:
                response = await resp.json()
                if (
                    isinstance(response.get("data"), dict)
                    and isinstance(response["data"].get("room_info"), dict)
                    and response["data"]["room_info"].get("room_id")
                    and response["data"]["room_info"].get("uid")
                    and isinstance(
                        response["data"]["room_info"].get("live_status"), int
                    )
                ):
                    return (
                        True,
                        response["data"]["room_info"]["room_id"],
                        response["data"]["room_info"]["live_status"],
                        response["data"]["room_info"]["uid"],
                    )
            return False, 0, 0, 0
    except Exception:
        logger.exception("room id: %d" % room_id)
        return False, 0, 0, 0


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    tasks = [
        # asyncio.ensure_future(get_name(uid=11783021, room_id=931774)),
        # asyncio.ensure_future(get_live(room_id=931774)),
        asyncio.ensure_future(get_room_title(room_id=11783021))
    ]
    loop.run_until_complete(asyncio.wait(tasks))
    for task in tasks:
        print(task.result())
