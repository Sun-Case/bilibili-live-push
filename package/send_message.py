import aiohttp
import asyncio


class SessionAio:
    def __init__(self, tg_token: str = '', tg_id: str = '', sc_token: str = '', loop=None):
        self.tg_token = tg_token
        self.tg_id = tg_id
        self.sc_token = sc_token
        self.loop = loop or asyncio.get_event_loop()

    async def send(self, tg: bool = False, tg_text: str = '',
                   sc: bool = False, sc_title: str = '', sc_desp: str = '',
                   text: str = ''):
        task = self.loop.create_task(self.main(tg=tg, tg_text=tg_text,
                                               sc=sc, sc_title=sc_title, sc_desp=sc_desp,
                                               text=text))
        await task
        print('result', task.result())
        return task.result()

    async def main(self, tg: bool = False, tg_text: str = '',
                   sc: bool = False, sc_title: str = '', sc_desp: str = '',
                   text: str = ''):
        result = []
        run_detail = {}
        if tg is True:
            result.append(self.loop.create_task(self.tg_send(tg_text=tg_text, text=text)))
        if sc is True:
            result.append(self.loop.create_task(self.sc_send(sc_title=sc_title, sc_desp=sc_desp, text=text)))
        for z in result:
            await z
        for y in result:
            run_detail[y.result()[0]] = y.result()[1]
        return run_detail

    async def tg_send(self, tg_text: str = '', text: str = '') -> list:
        tg_text = tg_text or text
        tg_data = {'chat_id': self.tg_id, 'text': tg_text}
        async with aiohttp.ClientSession() as session:
            for a in [0, 1, 2]:
                try:
                    await session.post(url='https://api.telegram.org/bot%s/sendMessage' % self.tg_token,
                                       data=tg_data, timeout=3)
                    return ['tg', True]
                except:
                    pass
        return ['tg', False]

    async def sc_send(self, sc_title: str = '', sc_desp: str = '', text: str = '') -> list:
        sc_desp = sc_desp or text
        sc_data = {'text': sc_title, 'desp': sc_desp}
        async with aiohttp.ClientSession() as session:
            for a in [0, 1, 2]:
                try:
                    await session.post(url='https://sc.ftqq.com/%s.send' % self.sc_token, data=sc_data, timeout=3)
                    return ['sc', True]
                except:
                    pass
        return ['sc', False]


if __name__ == '__main__':
    a = SessionAio(tg_token='', tg_id='',
                   sc_token='')
    b = a.send(tg=True, tg_text='测试', sc=True, sc_title='测试', sc_desp='测试')
    print(b)
