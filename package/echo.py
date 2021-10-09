import asyncio
import time
from typing import *


class EchoFormat:
    th: List[str] = []
    td: List[List[str]] = []
    first_echo: bool = True
    last_update: float = time.time()

    def __init__(self) -> None:
        pass

    def init_th(self, *arg) -> None:
        self.th.clear()
        for i, x in enumerate(arg):  # type: str
            if isinstance(x, str) is True:
                self.th.append(x)
            else:
                print("非str类型", i, ":", x)

    def del_th(self) -> None:
        self.th.clear()

    def create_td(self) -> Tuple[int, list]:
        self.td.append([])
        while len(self.td[len(self.td) - 1]) < len(self.th):
            self.td[len(self.td) - 1].append("")
        return len(self.td) - 1, self.td[len(self.td) - 1]

    def update_td(self, index: int, *arg):
        for i, x in enumerate(arg):  # type: int, str
            if i < len(self.th):
                self.td[index][i] = x
        self.last_update = time.time()

    def update_element(self, row: int, column: int, arg: str):
        # 横排数列
        # row: 排
        # column: 列
        self.td[row][column] = arg
        self.last_update = time.time()

    def str_width(self) -> List[int]:
        str_len = [str_width(v) + 3 for v in self.th]
        for v in self.td:  # type: int, List[str]
            for i, x in enumerate(v):
                if i >= len(str_len):
                    break
                str_len[i] = (
                    str_len[i] if str_len[i] > str_width(x) + 3 else str_width(x) + 3
                )
        return str_len

    def echo(self):
        if not self.first_echo:
            print("\033[%sA" % (len(self.td) + 2))
        else:
            self.first_echo = False
        str_len = self.str_width()
        # th
        print(build_format(str_len, self.th) % tuple(self.th))
        # td
        for v in self.td:
            print(build_format(str_len, v) % tuple(v))

    async def loop(self):
        last_update: float = 0
        while True:
            if last_update >= self.last_update:
                await asyncio.sleep(1)
                continue
            self.echo()
            last_update = self.last_update


def build_format(str_len: List[int], str_list: List[str]) -> str:
    str_format = ""
    for i, v in enumerate(str_list):  # type: str
        str_format += "%-{}.{}s".format(
            str_len[i] - alpha_len(v), str_len[i] - alpha_len(v)
        )
    str_format += "\033[K"
    return str_format


def str_width(text: str) -> int:
    count = len(text)
    for i in text:
        if "\u4e00" <= i <= "\u9fff":
            count += 1
    return count


def alpha_len(text: str) -> int:
    count = 0
    for i in text:
        if "\u4e00" <= i <= "\u9fff":
            count += 1
    return count


if __name__ == "__main__":
    ef = EchoFormat()
    ef.init_th("#", "直播间ID", "真实ID", "主播名", "开播/下播", "实时状态")
    i, v = ef.create_td()
    v.append("1")
    v.append("2")
    v.append("3")
    v.append("4")
    v.append("5")
    v.append("6")

    ef.echo()
