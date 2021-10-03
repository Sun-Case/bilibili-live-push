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
        "summary": "直播通知",
        "proxy": null
    },
    "WxPusher": {
        "status": false,
        "appToken": "",
        "summary": "直播通知",
        "contentType": 1,
        "topicIds": [],
        "uids": [],
        "url": "",
        "proxy": null
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
