import asyncio
import time


class ECHO:
    q: asyncio.Queue
    data: dict

    def __init__(self, q: asyncio.Queue, loop) -> None:
        self.q = q
        self.data = {}
        self.loop = loop

    async def run(self):
        self.loop.create_task(self.show())

        while True:
            data = await self.q.get()
            if data["id"] not in self.data:
                self.data[data["id"]] = {
                    "msg": "",
                    "room_id": "",
                    "name": "",
                    "status": ""
                }

            if data["code"] == 0:
                self.data[data["id"]]["msg"] = time.strftime(
                    "%m-%d %H:%M:%S", time.localtime())+" "+data["data"]
            elif data["code"] == 1:
                self.data[data["id"]]["room_id"] = "%s" % data["data"]
            elif data["code"] == 2:
                self.data[data["id"]]["name"] = data["data"]
            elif data["code"] == 3:
                self.data[data["id"]]["status"] = "直播" if data["data"] else "下播"

    async def show(self):
        while True:
            data = [["#", "直播间ID", "真实ID", "主播名", "开播/下播", "实时状态"]]

            count = 0
            for k, v in self.data.items():
                count += 1
                data.append(["%s" % count, "%s" % k, v.get("room_id", ""),
                            v.get("name", ""), v.get("status", ""), v.get("msg", "")])

            echo(data)
            await asyncio.sleep(1)
            print("\033[%sA" % (count+2))


def echoConfig(config: dict):
    l = [["通知方式", "状态"]]
    for k, v in config.items():
        if isinstance(v, dict) is False:
            continue
        if "status" not in v:
            continue
        l.append([k, "开启"if v["status"]else"关闭"])
    echo(l)


def echo(table: list):
    # 横行竖列
    hor = len(table)  # 列
    row = 0           # 行
    maxHor = []       # 每列最大占位
    doubleChar = []   # 汉字数量

    if hor == 0:
        return
    for i in table:
        row = len(i) if row < len(i)else row
        for k, v in enumerate(i):
            while len(maxHor) < k+1:
                maxHor.append(0)
                doubleChar.append(0)
            maxHor[k] = (len(v)+alpha_len(v)
                         ) if maxHor[k] < (len(v)+alpha_len(v))else maxHor[k]
            doubleChar[k] = alpha_len(
                v) if doubleChar[k] < alpha_len(v)else doubleChar[k]
    for i in table:
        ctrl = " "
        for j, k in enumerate(i):
            ctrl += "%-{}.{}s".format(maxHor[j]+2 -
                                      alpha_len(k), maxHor[j]+2-alpha_len(k))
        ctrl += "\033[K"
        print(ctrl % tuple(i))


def alpha_len(text: str) -> int:
    count = 0
    for i in text:
        if '\u4e00' <= i <= '\u9fff':
            count += 1
    return count


if __name__ == "__main__":
    echo([["123", "345"], ["4567", "1", "666"]])
