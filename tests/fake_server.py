import asyncio
import socket
import unittest

import aiohttp
from aiohttp import web
from aiohttp.resolver import DefaultResolver
from aiohttp.test_utils import unused_port

from aiopvapi.helpers.aiorequest import AioRequest

FAKE_BASE_URL = "powerview.hub.test"

ROOMS_VALUE = """
{"roomIds":[30284,26756],"roomData":[
{"type":1,"name":"UmVwZWF0ZXJz","colorId":15,"iconId":0,"order":3,"id":30284},
{"order":2,"name":"RGluaW5nIFJvb20=","colorId":0,"iconId":0,"id":26756,"type":0}]}
"""

ROOM_VALUE = """
{"room":{"id":46688,"name":"TGl2aW5nIHJvb20=","order":0,"colorId":7,"iconId":0,"type":0}}
"""

SHADES_VALUE = """
{"shadeIds":[29889,56112],"shadeData":[
{"id":29889,"type":6,"batteryStatus":0,"batteryStrength":0,"name":"UmlnaHQ=","roomId":12372,"groupId":18480,
"positions":{"posKind1":1,"position1":0},"firmware":{"revision":1,"subRevision":8,"build":1944}},
{"id":56112,"type":16,"batteryStatus":4,"batteryStrength":180,"name":"UGF0aW8gRG9vcnM=",
"roomId":15103,"groupId":49380,"positions":{"posKind1":3,"position1":65535},
"firmware":{"revision":1,"subRevision":8,"build":1944}}]}
"""

SHADE_VALUE = """
{"shade":{"id":11155,"name":"U2hhZGUgMQ==","roomId":46688,"groupId":38058,"order":0,"type":8,"batteryStrength":146,"batteryStatus":3,"positions":{"position1":8404,"posKind1":1,"position2":42209,"posKind2":2},"firmware":{"revision":1,"subRevision":4,"build":1643},"signalStrength":4}}
"""

SCENES_VALUE = """
{"sceneIds":[37217,64533],"sceneData":[
{"roomId":26756,"name":"RGluaW5nIFZhbmVzIE9wZW4=","colorId":0,"iconId":0,"id":37217,"order":1},
{"roomId":12372,"name":"TWFzdGVyIE9wZW4=","colorId":9,"iconId":0,"id":64533,"order":7}]}
"""

SCENE_VALUE = """
{"scene":{"roomId":46688,"name":"VGVzdA==","colorId":7,"iconId":0,"id":43436,"order":0}}
"""


class FakeResolver:
    _LOCAL_HOST = {0: '127.0.0.1',
                   socket.AF_INET: '127.0.0.1',
                   socket.AF_INET6: '::1'}

    def __init__(self, fakes, *, loop):
        """fakes -- dns -> port dict"""
        self._fakes = fakes
        self._resolver = DefaultResolver(loop=loop)

    async def resolve(self, host, port=0, family=socket.AF_INET):
        fake_port = self._fakes.get(host)
        if fake_port is not None:
            return [{'hostname': host,
                     'host': self._LOCAL_HOST[family], 'port': fake_port,
                     'family': family, 'proto': 0,
                     'flags': socket.AI_NUMERICHOST}]
        else:
            return await self._resolver.resolve(host, port, family)


class FakePowerViewHub:

    def __init__(self, *, loop):
        self.loop = loop
        self.app = web.Application()
        self.app.router.add_routes(
            [
                web.get('/test_get_status_200', self.test_get_status_200),
                web.get('/wrong_status', self.wrong_status),
                web.get('/invalid_json', self.invalid_json),
                web.get('/get_timeout', self.get_timeout),
                web.post('/post_status_200', self.post_status_200),
                web.post('/post_status_201', self.post_status_201),
                web.get('/api/rooms', self.get_rooms),
                web.get('/api/rooms/1234', self.get_room),
                web.post('/api/rooms', self.new_room),
                web.delete('/api/rooms/{room_id}', self.delete_room),
                web.get('/api/scenes', self.handle_scene),
                web.get('/api/scenes/43436',self.get_scene),
                web.post('/api/scenes', self.create_scene),
                web.get('/api/shades', self.get_shades),
                web.get('/api/shades/11155',self.get_shade),
                web.put('/api/shades/{shade_id}', self.add_shade_to_room),

            ])
        self.runner = None

    async def start(self):
        port = unused_port()
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, '127.0.0.1', port)
        await site.start()
        return {FAKE_BASE_URL: port}

    async def stop(self):
        if self.runner:
            await self.runner.cleanup()

    async def test_get_status_200(self, request):
        return web.json_response(
            {"title": "test"}
            , status=200)

    async def wrong_status(self, request):
        return web.json_response({}, status=201)

    async def invalid_json(self, request):
        return web.Response(
            body='{"title": "test}',
            status=200,
            headers={'content-type': 'application/json'})

    async def get_timeout(self, request):
        await asyncio.sleep(2)
        return web.json_response({})

    async def post_status_200(self, request):
        return web.json_response({
            'a': 'b', 'c': 'd'
        })

    async def post_status_201(self, request):
        return web.json_response({
            'a': 'b', 'c': 'd'
        })

    async def get_rooms(self, request):
        return web.Response(
            body=ROOMS_VALUE,
            headers={'content-type': 'application/json'})

    async def get_room(self, request):
        return web.Response(
            body=ROOM_VALUE,
            headers={'content-type': 'application/json'}
        )

    async def new_room(self, request):
        _js = await request.json()
        return web.json_response({
            "id": 1, "name": _js['room']["name"]
        }, status=201)

    async def delete_room(self, request):
        _id = request.match_info["room_id"]
        if _id == '26756':
            return web.Response(status=204)
        else:
            return web.Response(status=404)

    async def handle_scene(self, request):
        _id = request.query.get('sceneId')
        if _id is None:
            return web.Response(
                body=SCENES_VALUE,
                headers={'content-type': 'application/json'})
        elif _id is not None and _id == '10':
            return web.json_response({'id': 10})
        else:
            return web.Response(status=404)

    async def get_scene(self,request):
        return web.Response(
            body=SCENE_VALUE,
            headers={'content-type': 'application/json'}
        )

    async def get_shades(self, request):
        return web.Response(
            body=SHADES_VALUE,
            headers={'content-type': 'application/json'})

    async def get_shade(self, request):
        return web.Response(
            body=SHADE_VALUE,
            headers={'content-type': 'application/json'}
        )

    async def add_shade_to_room(self, request):
        # todo: finish this.
        _shade_id = request.match_info['shade_id']
        _js = await request.json()
        if _js['shade']['roomId'] == 123:
            return web.json_response({"shade": True})

    async def create_scene(self, request):
        _js = await request.json()
        return web.json_response(_js)


async def main(loop):
    fake_powerview_hub = FakePowerViewHub(loop=loop)
    info = await fake_powerview_hub.start()
    resolver = FakeResolver(info, loop=loop)
    connector = aiohttp.TCPConnector(loop=loop, resolver=resolver)

    async with aiohttp.ClientSession(connector=connector,
                                     loop=loop) as session:
        async with session.get('http://{}/v2.7/me'.format(FAKE_BASE_URL),
                               ) as resp:
            print(await resp.json())

        # async with session.get('https://graph.facebook.com/v2.7/me/friends',
        #                        params={'access_token': token}) as resp:
        #     print(await resp.json())

    await fake_powerview_hub.stop()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))


class TestFakeServer(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.server = FakePowerViewHub(loop=self.loop)
        self.request = None

    def tearDown(self):
        if isinstance(self.request, AioRequest):
            self.loop.run_until_complete(self.request.websession.close())
        self.loop.run_until_complete(self.server.stop())

    async def start_fake_server(self):
        info = await self.server.start()
        resolver = FakeResolver(info, loop=self.loop)
        connector = aiohttp.TCPConnector(loop=self.loop, resolver=resolver)
        _session = aiohttp.ClientSession(connector=connector, loop=self.loop)
        self.request = AioRequest(FAKE_BASE_URL, loop=self.loop,
                                  websession=_session, timeout=1)


def make_url(end_point):
    return 'http://{}/{}'.format(FAKE_BASE_URL, end_point)
