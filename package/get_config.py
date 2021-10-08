from typing import *


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
    "Qmsg": {
        "status": false,
        "key": "",
        "qq": [],
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


# 以 old 为基础，将 new 存在的且类型相同的合并到 old 上
def merge_dict(new: dict, old: dict):
    seq: List[Dict[str, Dict]] = []  # 类似队列

    seq.append({"new": new, "old": old})

    while len(seq) != 0:
        new = seq[0]["new"]
        old = seq[0]["old"]
        seq.pop(0)

        if (not isinstance(new, dict)) or (not isinstance(old, dict)):
            continue

        for k in old.keys():  # type: str
            if k not in new:
                continue

            if isinstance(old[k], dict):
                seq.append({"new": new[k], "old": old[k]})
            elif isinstance(old[k], list):
                old[k] = new[k]
            elif isinstance(old[k], type(None)):
                old[k] = new[k]
            else:
                old[k] = new[k]


if __name__ == "__main__":
    get_roomid(
        """# 每行一个直播间ID

1
931774
"""
    )
