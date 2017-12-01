import unittest
import json
import aiohttp
import asyncio

from aiopvapi.helpers.aiorequest import PvApiResponseStatusError
from aiopvapi.rooms import Rooms
from aioresponses import aioresponses

RETURN_VALUE = """
{"roomIds":[30284,26756],"roomData":[
{"type":1,"name":"UmVwZWF0ZXJz","colorId":15,"iconId":0,"order":3,"id":30284},
{"order":2,"name":"RGluaW5nIFJvb20=","colorId":0,"iconId":0,"id":26756,"type":0}]}
"""


class TestRooms(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.websession = aiohttp.ClientSession(loop=self.loop)
        self.rooms = Rooms('127.0.0.1', self.loop, self.websession)

    def tearDown(self):
        self.websession.close()

    @aioresponses()
    def test_get_resources_200(self, mocked):
        """Test get resources with status 200."""
        mocked.get('http://127.0.0.1/api/rooms',
                   body=RETURN_VALUE,
                   status=200,
                   headers={'content-type': 'application/json'})
        resources = self.loop.run_until_complete(self.rooms.get_resources())
        self.assertEqual(2, len(resources['roomIds']))
        self.assertEqual(2, len(resources['roomData']))
        self.assertEqual('Repeaters',
                         resources['roomData'][0]['name_unicode'])
        self.assertEqual('Dining Room',
                         resources['roomData'][1]['name_unicode'])

    @aioresponses()
    def test_get_resources_201(self, mocked):
        """Test get resources with wrong status."""
        mocked.get('http://127.0.0.1/api/rooms',
                   body=RETURN_VALUE,
                   status=201,
                   headers={'content-type': 'application/json'})
        with self.assertRaises(PvApiResponseStatusError):
            resources = self.loop.run_until_complete(self.rooms.get_resources())

    @aioresponses()
    def test_create_room_201(self, mocked):
        """Tests create new room."""
        mocked.post('http://127.0.0.1/api/rooms',
                    body='{}',
                    status=201,
                    headers={'content-type': 'application/json'})
        resp = self.loop.run_until_complete(
            self.rooms.create_room('New room', color_id=1, icon_id=2))
        self.assertEqual({}, resp)
        request = mocked.requests[('POST', 'http://127.0.0.1/api/rooms')][-1]

        self.assertEqual({"room": {"name": "TmV3IHJvb20=", "colorId": 1,
                                   "iconId": 2}},
                         request.kwargs['json'])

    @aioresponses()
    def test_create_room_202(self, mocked):
        """Tests create new room with wrong status code."""
        mocked.post('http://127.0.0.1/api/rooms',
                    body='"ok"',
                    status=202,
                    headers={'content-type': 'application/json'})
        with self.assertRaises(PvApiResponseStatusError):
            resp = self.loop.run_until_complete(
                self.rooms.create_room('New room', color_id=1, icon_id=2))
