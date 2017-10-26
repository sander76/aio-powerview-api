import unittest
import json
import aiohttp
import asyncio
from aioresponses import aioresponses
from aiopvapi.scenes import Scenes

RETURN_VALUE = """
{"sceneIds":[37217,64533],"sceneData":[
{"roomId":26756,"name":"RGluaW5nIFZhbmVzIE9wZW4=","colorId":0,"iconId":0,"id":37217,"order":1},
{"roomId":12372,"name":"TWFzdGVyIE9wZW4=","colorId":9,"iconId":0,"id":64533,"order":7}]}
"""


class TestScenes(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.websession = aiohttp.ClientSession(loop=self.loop)
        self.scenes = Scenes('127.0.0.1', self.loop, self.websession)

    def tearDown(self):
        self.websession.close()

    @aioresponses()
    def test_get_resources_200(self, mocked):
        """Test get resources with status 200."""
        mocked.get('http://127.0.0.1/api/scenes',
                   body=RETURN_VALUE,
                   status=200,
                   headers={'content-type': 'application/json'})
        resources = self.loop.run_until_complete(self.scenes.get_resources())
        self.assertEqual(2, len(resources['sceneIds']))
        self.assertEqual(2, len(resources['sceneData']))
        self.assertEqual('Dining Vanes Open',
                         resources['sceneData'][0]['name_unicode'])
        self.assertEqual('Master Open',
                         resources['sceneData'][1]['name_unicode'])

    @aioresponses()
    def test_get_resources_201(self, mocked):
        """Test get resources with wrong status."""
        mocked.get('http://127.0.0.1/api/scenes',
                   body=RETURN_VALUE,
                   status=201,
                   headers={'content-type': 'application/json'})
        resources = self.loop.run_until_complete(self.scenes.get_resources())
        self.assertIsNone(resources)

    @aioresponses()
    def test_create_scene_201(self, mocked):
        """Tests create new scene."""
        mocked.post('http://127.0.0.1/api/scenes',
                    body='"ok"',
                    status=201,
                    headers={'content-type': 'application/json'})
        resp = self.loop.run_until_complete(
            self.scenes.create_scene(12372, 'New scene', color_id=1, icon_id=2))
        self.assertEqual('ok', resp)
        request = mocked.requests[('POST', 'http://127.0.0.1/api/scenes')][-1]
        self.assertEqual({"scene": {"roomId": 12372, "name": "TmV3IHNjZW5l",
                                    "colorId": 1, "iconId": 2}},
                         json.loads(request.kwargs['data']))

    @aioresponses()
    def test_create_scene_202(self, mocked):
        """Tests create new scene with wrong status code."""
        mocked.post('http://127.0.0.1/api/scenes',
                    body='"ok"',
                    status=202,
                    headers={'content-type': 'application/json'})
        resp = self.loop.run_until_complete(
            self.scenes.create_scene(12372, 'New scene', color_id=1, icon_id=2))
        self.assertIsNone(resp)
