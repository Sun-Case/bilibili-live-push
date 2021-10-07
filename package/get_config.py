config_bak = """{
    "Telegram": {
        "status": false,
        "bot_token": "",
        "user_id": "",
        "proxy": null
    },
    "ServerChan": {
        "status": false,
        "token": "",
        "use_content_as_summary": false,
        "summary": "直播通知",
        "proxy": null
    },
    "WxPusher": {
        "status": false,
        "appToken": "",
        "summary": "",
        "contentType": 1,
        "topicIds": [],
        "uids": [],
        "url": "",
        "proxy": null
    },
    "PushPlus": {
        "status": false,
        "token": "",
        "title": "",
        "template": "html",
        "topic": "",
        "channel": "",
        "webhook": "",
        "callbackUrl": "",
        "proxy": ""
    },
    "SSL": null,
    "LIVE": false,
    "PREPARING": false,
    "PROXY": null
}"""
roomid_bak = """# 每行一个直播间ID

1
931774
"""


def get_roomid(text: str):
    room_list = []

    lines = text.split("\n")
    while "" in lines:
        lines.remove("")

    for line in lines:
        try:
            room_list.append(int(line))
        except Exception:
            pass

    return room_list


if __name__ == "__main__":
    get_roomid(
        """# 每行一个直播间ID

1
931774
"""
    )
