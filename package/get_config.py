from io import SEEK_SET
from typing import *
import os
import logging
import json
import re


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
        "summary": "",
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
    "LIVE": true,
    "PREPARING": true,
    "PROXY": null,
    "BASE_CONFIG": {
        "roomid_file": "直播间ID.txt",
        "live_file": "开播通知模板.txt",
        "preparing_file": "下播通知模板.txt"
    }
}"""
roomid_bak = """# 每行一个直播间ID

1
931774
"""
live_template_bak = "【${name}】 room_id: ${room_id}, true_id: ${true_room}, uid: ${uid} 开播啦 时间: ${YYYY}-${mm}-${dd} ${HH}:${MM}:${SS}"
preparing_template_bak = "【${name}】 room_id: ${room_id}, true_id: ${true_room}, uid: ${uid} 下播啦 时间: ${YYYY}-${mm}-${dd} ${HH}:${MM}:${SS}"


class ContentProcess:
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    def rewrite_file(self, file: str, content: str, encoding: str = "utf-8") -> bool:
        """
        覆写文本文件
        """
        try:
            with open(file, "w", encoding=encoding) as w:
                w.seek(0, SEEK_SET)
                w.truncate()
                w.write(content)
            return True
        except Exception:
            self.logger.exception("%s write file failure" % file)
        return False

    def get_int_from_text(
        self, file: str = None, text: str = None, flag: str = "#"
    ) -> Tuple[bool, List[int]]:
        """
        文本内容每行存放一个整数
        从 文本内容 获取 整数
        """

        if file:
            status, text_ = self.get_text_from_file(file)
            if status is True:
                text = text_

        if not text:
            return False, []

        roomid_list = []

        lines = text.split("\n")
        while "" in lines:
            lines.remove("")

        for line in lines:
            if re.match(r"([ ]*)([%s]+)(.*)" % flag, line):
                continue

            try:
                roomid_list.append(int(line))
            except Exception as e:
                self.logger.warn("非法字符, 无法转成整型: %s", line, exc_info=e)

        return True, roomid_list

    def get_text_from_file(
        self, file: str, encoding: str = "utf-8"
    ) -> Tuple[bool, str]:
        """
        从 文本文件 获取 文本内容
        """
        if os.path.exists(file):
            try:
                with open(file, "r", encoding=encoding) as r:
                    try:
                        return True, r.read()
                    except Exception:
                        self.logger.exception("%s: read file failure" % file)
                return False, ""
            except Exception:
                self.logger.exception("%s: open file failure" % file)
                return False, ""
        else:
            return False, ""


class GetConfig:
    def __init__(self, logger: logging.Logger, config_file: str) -> None:
        self.logger = logger
        self.config: Dict = json.loads(config_bak)
        self.config_file = config_file
        self.roomid_list = []
        self.template = {}
        self.c_p = ContentProcess(logger)

    def get_template(self):
        base_config = self.config["BASE_CONFIG"]

        for v in [
            {"file": "live_file", "key": "live_template", "default": live_template_bak},
            {
                "file": "preparing_file",
                "key": "preparing_template",
                "default": preparing_template_bak,
            },
        ]:  # type: Dict[str, str]
            file_name: str = base_config[v["file"]]
            status, content = self.c_p.get_text_from_file(file_name)
            if status:
                self.template[v["key"]] = content
            else:
                self.template[v["key"]] = v["default"]
                self.c_p.rewrite_file(base_config[v["file"]], v["default"])
                print("%s: 文件不存在，已为你生成示例文件" % base_config[v["file"]])

    def get_roomid_list(self) -> bool:
        """
        读取直播间ID
        """
        base_config: Dict[str, str] = self.config["BASE_CONFIG"]
        roomid_file = base_config["roomid_file"]

        if not os.path.exists(roomid_file):
            if self.c_p.rewrite_file(roomid_file, roomid_bak):
                print("%s: 直播间ID文件不存在，以为你生成新示例文件，请打开文件添加直播间ID" % roomid_file)
            else:
                print("%s: 覆写文件失败" % roomid_file)
            return False

        status, roomid_list = self.c_p.get_int_from_text(file=roomid_file)
        if status:
            self.roomid_list = roomid_list
            print("直播间ID读取成功")
            return True
        else:
            print("%s: 读取失败" % roomid_file)
            return False

    def get_config(self) -> bool:
        """
        读取配置文件
        """
        if os.path.exists(self.config_file):
            status, content = self.c_p.get_text_from_file(self.config_file)
            if status:
                try:
                    new = json.loads(content)
                    merge_dict(new, self.config)
                    if not self.c_p.rewrite_file(
                        self.config_file,
                        json.dumps(self.config, ensure_ascii=False, indent=4),
                    ):
                        print("%s: 配置文件覆写错误" % self.config_file)
                    return True
                except Exception:
                    print("%s: 解析配置文件失败")
                    if self.c_p.rewrite_file(
                        self.config_file,
                        json.dumps(self.config, ensure_ascii=False, indent=4),
                    ):
                        print("%s: 以为你生成新配置文件，请打开文件进行配置" % self.config_file)
                    else:
                        print("%s: 覆写配置文件失败" % self.config_file)
                    return False
            else:
                print("%s: 读取配置文件失败" % self.config_file)
                if self.c_p.rewrite_file(
                    self.config_file,
                    json.dumps(self.config, ensure_ascii=False, indent=4),
                ):
                    print("%s: 已为你生成新配置文件，请打开文件进行配置" % self.config_file)
                else:
                    print("%s: 覆写配置文件失败" % self.config_file)
                return False
        else:
            if self.c_p.rewrite_file(
                self.config_file, json.dumps(self.config, ensure_ascii=False, indent=4)
            ):
                print("%s: 配置文件不存在，以为你生成配置文件，请打开文件进行配置" % self.config_file)
            else:
                print("%s: 生成配置文件失败" % self.config_file)
            return False


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
    pass
