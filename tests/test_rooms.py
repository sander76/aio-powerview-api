import unittest
import json
import aiohttp
import asyncio
from mocket.plugins.httpretty import HTTPretty, httprettified
from aiopvapi.rooms import Rooms

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

    @httprettified
    def test_get_resources_200(self):
        """Test get resources with status 200."""
        HTTPretty.register_uri(HTTPretty.GET, 'http://127.0.0.1/api/rooms',
                               body=RETURN_VALUE,
                               status=200,
                               content_type='application/json')
        resources = self.loop.run_until_complete(self.rooms.get_resources())
        self.assertEqual(2, len(resources['roomIds']))
        self.assertEqual(2, len(resources['roomData']))
        self.assertEqual('Repeaters',
                         resources['roomData'][0]['name_unicode'])
        self.assertEqual('Dining Room',
                         resources['roomData'][1]['name_unicode'])

    @httprettified
    def test_get_resources_201(self):
        """Test get resources with wrong status."""
        HTTPretty.register_uri(HTTPretty.GET, 'http://127.0.0.1/api/rooms',
                               body=RETURN_VALUE,
                               status=201,
                               content_type='application/json')
        resources = self.loop.run_until_complete(self.rooms.get_resources())
        self.assertIsNone(resources)

    @httprettified
    def test_create_room_201(self):
        """Tests create new room."""
        HTTPretty.register_uri(HTTPretty.POST, 'http://127.0.0.1/api/rooms',
                               body='"ok"',
                               status=201,
                               content_type='application/json')
        resp = self.loop.run_until_complete(
            self.rooms.create_room('New room', color_id=1, icon_id=2))
        self.assertEqual('ok', resp)
        request = HTTPretty.last_request
        self.assertEqual({"room": {"name": "TmV3IHJvb20=", "colorId": 1,
                                   "iconId": 2}},
                         json.loads(request.body.decode('utf-8')))
        self.assertEqual('POST', request.command)

    @httprettified
    def test_create_room_202(self):
        """Tests create new room with wrong status code."""
        HTTPretty.register_uri(HTTPretty.POST, 'http://127.0.0.1/api/rooms',
                               body='"ok"',
                               status=202,
                               content_type='application/json')
        resp = self.loop.run_until_complete(
            self.rooms.create_room('New room', color_id=1, icon_id=2))
        self.assertIsNone(resp)
