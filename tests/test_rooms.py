import unittest
import json
import aiohttp
import asyncio
from aiopvapi.rooms import Rooms
from mocket.mocket import mocketize, Mocket
from mocket.mockhttp import Entry

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

    @mocketize
    def test_get_resources_200(self):
        """Test get resources with status 200."""
        Entry.single_register(Entry.GET, 'http://127.0.0.1/api/rooms',
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

    @mocketize
    def test_get_resources_201(self):
        """Test get resources with wrong status."""
        Entry.single_register(Entry.GET, 'http://127.0.0.1/api/rooms',
                               body=RETURN_VALUE,
                               status=201,
                               headers={'content-type': 'application/json'})
        resources = self.loop.run_until_complete(self.rooms.get_resources())
        self.assertIsNone(resources)

    @mocketize
    def test_create_room_201(self):
        """Tests create new room."""
        Entry.single_register(Entry.POST, 'http://127.0.0.1/api/rooms',
                               body='"ok"',
                               status=201,
                               headers={'content-type': 'application/json'})
        resp = self.loop.run_until_complete(
            self.rooms.create_room('New room', color_id=1, icon_id=2))
        self.assertEqual('ok', resp)
        request = Mocket.last_request()
        self.assertEqual({"room": {"name": "TmV3IHJvb20=", "colorId": 1,
                                   "iconId": 2}},
                         json.loads(request.body))
        self.assertEqual('POST', request.command)

    @mocketize
    def test_create_room_202(self):
        """Tests create new room with wrong status code."""
        Entry.single_register(Entry.POST, 'http://127.0.0.1/api/rooms',
                               body='"ok"',
                               status=202,
                               headers={'content-type': 'application/json'})
        resp = self.loop.run_until_complete(
            self.rooms.create_room('New room', color_id=1, icon_id=2))
        self.assertIsNone(resp)
