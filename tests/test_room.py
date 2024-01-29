from unittest.mock import Mock

from aiopvapi.helpers.aiorequest import PvApiResponseStatusError
from aiopvapi.resources.room import Room
from tests.fake_server import FAKE_BASE_URL
from tests.test_apiresource import TestApiResource

ROOM_RAW_DATA = {
    "order": 2,
    "name": "RGluaW5nIFJvb20=",
    "colorId": 0,
    "iconId": 0,
    "id": 26756,
    "type": 0,
}


class TestRoom(TestApiResource):
    def get_resource_raw_data(self):
        return ROOM_RAW_DATA

    def get_resource_uri(self):
        return "http://{}/api/rooms/26756".format(FAKE_BASE_URL)

    def get_resource(self):
        _request = Mock()
        _request.hub_ip = FAKE_BASE_URL
        _request.api_version = 2
        _request.api_path = "api"
        return Room(ROOM_RAW_DATA, _request)

    def test_full_path(self):
        self.assertEqual(
            self.resource.base_path, "http://{}/api/rooms".format(FAKE_BASE_URL)
        )

    def test_name_property(self):
        # No name_unicode, so base64 encoded is returned
        self.assertEqual("Dining Room", self.resource.name)

    def test_delete_room_success(self):
        """Tests deleting a room"""

        async def go():
            await self.start_fake_server()
            room = self.get_resource()
            resp = await room.delete()
            return resp

        resp = self.loop.run_until_complete(go())
        self.assertTrue(resp)

    def test_delete_room_fail(self):
        """Tests deleting a room with wrong id."""

        async def go():
            await self.start_fake_server()
            room = self.get_resource()
            room._resource_path += "1"
            resp = await room.delete()
            return resp

        with self.assertRaises(PvApiResponseStatusError):
            self.loop.run_until_complete(go())
