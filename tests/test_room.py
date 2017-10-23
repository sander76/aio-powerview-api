from mocket.plugins.httpretty import HTTPretty, httprettified

from aiopvapi.resources.room import Room
from test_apiresource import TestApiResource

ROOM_RAW_DATA = {"order": 2, "name": "RGluaW5nIFJvb20=",
                 "colorId": 0, "iconId": 0, "id": 26756, "type": 0}


class TestRoom(TestApiResource):

    def get_resource_raw_data(self):
        return ROOM_RAW_DATA

    def get_resource_uri(self):
        return 'http://127.0.0.1/api/rooms/26756'

    def get_resource(self, loop, websession):
        return Room(ROOM_RAW_DATA, 'http://127.0.0.1', loop, websession)

    def test_name_property(self):
        # No name_unicode, so base64 encoded is returned
        self.assertEqual('RGluaW5nIFJvb20=', self.resource.name)

