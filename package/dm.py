import aiohttp
import asyncio
import time
import struct
import json
import zlib
from collections import namedtuple
from package.utile import get_name, get_live


class DM:
    timestamp: int = 0
    room_id: int = 0
    uid: int = 0
    name: str = ''
    serve_list = []
    token = ''
    ws = None
    HEADER_STRUCT = struct.Struct('>I2H2I')
    HeaderTuple = namedtuple('HeaderTuple', ('pack_len', 'raw_header_size', 'ver', 'operation', 'seq_id'))
    heart_beat = 2
    popularity = 3
    msg = 5
    first_shake = 7
    h_b = 8
    api_check_sleep = 60

    def __init__(self, room_id: int, queue, loop=None, ssl=None):
        if not room_id:
            raise Exception('room_id 错误')
        self._room_id: int = room_id
        if loop is None:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = loop
        self.queue = queue
        self.ssl = ssl

    async def run(self):
        await self.__init_room__()
        await self.__get_dm_conf__()
        print('name: {name}, room_id: {room_id}, true_room_id: {true_room_id}, uid: {uid}'.format(
            name=self.name, room_id=self._room_id, true_room_id=self.room_id, uid=self.uid
        ))
        self.loop.create_task(self.__api__check__())
        while True:
            for value in self.serve_list:
                try:
                    await self.__ws__(serve=value['host'], port=value['wss_port'])
                except:
                    pass
                print('【%s】web socket断开' % self.name)
            await self.__init_room__()
            await self.__get_dm_conf__()

    async def __api__check__(self):
        live_status = False
        while True:
            print('【%s】api check' % self.name)
            status, room_id, live, uid = await get_live(room_id=self.room_id)
            if status:
                if live == 1 and live_status is False:  # 开播
                    print('【%s】api check 开播' % self.name)
                    live_status = True
                    await self.queue.put({'live_status': 'LIVE', 'uid': self.uid, 'room_id': self._room_id,
                                          'true_room': self.room_id, 'name': self.name})
                elif live == 0 and live_status is True:  # 下播
                    print('【%s】api check 下播' % self.name)
                    live_status = False
                    await self.queue.put({'live_status': 'PREPARING', 'uid': self.uid, 'room_id': self.room_id,
                                          'true_room': self.room_id, 'name': self.name})
            await asyncio.sleep(self.api_check_sleep)

    async def __ws__(self, serve, port):
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect('wss://%s:%s/sub' % (serve, port), ssl=self.ssl) as ws:
                self.timestamp = int(time.time())
                self.ws = ws
                await self.__first_shake__()
                self.loop.create_task(self.__heart_beat__())
                async for msg in ws:  # type: aiohttp.WSMessage
                    if msg.type == aiohttp.WSMsgType.BINARY:
                        await self.__ws_message__(data=msg.data)

    async def __ws_message__(self, data: bytes):
        offset = 0
        while offset < len(data):
            try:
                header = self.HeaderTuple(*self.HEADER_STRUCT.unpack_from(data, offset))
            except struct.error:
                break
            if header.operation == self.popularity:
                popularity = int.from_bytes(data[offset + self.HEADER_STRUCT.size:
                                                 offset + self.HEADER_STRUCT.size + 4], 'big')
                print('【%s】人气：%s' % (self.name, popularity))
            elif header.operation == self.msg:
                body = data[offset + self.HEADER_STRUCT.size: offset + header.pack_len]
                if header.ver == 2:
                    body = zlib.decompress(body)
                    await self.__ws_message__(body)
                else:
                    body = json.loads(body.decode('utf-8'))
                    if body.get('cmd') == "LIVE":  # 开播
                        print('【%s】web socket 开播' % self.name)
                        await self.queue.put({'live_status': 'LIVE', 'uid': self.uid, 'room_id': self._room_id,
                                              'true_room': self.room_id, 'name': self.name})
                    elif body.get('cmd') == "PREPARING":  # 下播
                        print('【%s】web socket 下播' % self.name)
                        await self.queue.put({'live_status': 'PREPARING', 'uid': self.uid, 'room_id': self.room_id,
                                              'true_room': self.room_id, 'name': self.name})
            elif header.operation == self.h_b:
                print('【%s】心跳包' % self.name)
                task = self.ws.send_bytes(self.__encode_pack__('[object Object]', self.heart_beat))
                self.loop.create_task(task)
            offset += header.pack_len

    async def __heart_beat__(self):
        timestamp = self.timestamp
        while timestamp == self.timestamp:
            try:
                print('【%s】定时心跳包' % self.name)
                await self.ws.send_bytes(self.__encode_pack__('[object Object]', self.heart_beat))
            except:
                break
            await asyncio.sleep(30)

    async def __first_shake__(self):
        data = {
            'uid': 0,
            'roomid': self.room_id,
            'protover': 2,
            'platform': 'web',
            'clientver': '1.14.0',
            'type': 2,
            'key': self.token
        }
        body = json.dumps(data, ensure_ascii=False)
        await self.ws.send_bytes(self.__encode_pack__(body, self.first_shake))

    def __encode_pack__(self, data: str, operation: int):
        body = data.encode('utf-8')
        header = self.HEADER_STRUCT.pack(
            self.HEADER_STRUCT.size + len(body),
            self.HEADER_STRUCT.size,
            1,
            operation,
            1
        )
        return header + body

    async def __get_dm_conf__(self):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.live.bilibili.com/room/v1/Danmu/getConf') as resp:
                response = await resp.json()
                if not isinstance(response.get('data'), dict):
                    raise Exception('获取弹幕信息')
                if not response['data'].get('token'):
                    raise Exception('获取token失败')
                if not response['data'].get('host_server_list'):
                    raise Exception('获取弹幕地址失败')
                self.token = response['data']['token']
                self.serve_list = response['data']['host_server_list']

    async def __init_room__(self):
        status, room_id, live_status, uid = await get_live(room_id=self._room_id)
        if status is False:
            raise Exception('直播间初始化失败，无法获取直播间真实ID')
        self.room_id = room_id
        self.uid = uid
        status, name = await get_name(uid=uid, room_id=room_id)
        self.name = name or '%s' % uid


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    q = asyncio.Queue()
    tasks = [
        asyncio.ensure_future(DM(room_id=931774, queue=q, loop=loop).run())
    ]
    loop.run_until_complete(asyncio.wait(tasks))
