from unittest.mock import Mock

from aiopvapi.helpers.aiorequest import PvApiResponseStatusError
from aiopvapi.resources.scene import Scene

from tests.fake_server import FAKE_BASE_URL
from tests.test_apiresource import TestApiResource

SCENE_RAW_DATA = {
    "roomId": 26756,
    "name": "RGluaW5nIFZhbmVzIE9wZW4=",
    "colorId": 0,
    "iconId": 0,
    "id": 37217,
    "order": 1,
}


class TestScene(TestApiResource):
    def get_resource_raw_data(self):
        return SCENE_RAW_DATA

    def get_resource_uri(self):
        return "http://{}/api/scenes/37217".format(FAKE_BASE_URL)

    def get_resource(self):
        _request = Mock()
        _request.hub_ip = FAKE_BASE_URL
        _request.api_version = 2
        return Scene(SCENE_RAW_DATA, _request)

    def test_name_property(self):
        # No name_unicode, so base64 encoded is returned
        self.assertEqual("RGluaW5nIFZhbmVzIE9wZW4=", self.resource.name)

    def test_room_id_property(self):
        self.assertEqual(26756, self.resource.room_id)

    def test_full_path(self):
        self.assertEqual(
            self.resource._base_path,
            "http://{}/api/scenes".format(FAKE_BASE_URL),
        )

    def test_activate_200(self):
        """Test scene activation"""

        async def go():
            await self.start_fake_server()
            scene = Scene({"id": 10}, self.request)
            resp = await scene.activate()
            return resp

        resp = self.loop.run_until_complete(go())
        self.assertEqual(resp["id"], 10)

    def test_activate_404(self):
        """Test scene activation"""

        async def go():
            await self.start_fake_server()
            scene = Scene({"id": 11}, self.request)
            resp = await scene.activate()
            return resp

        with self.assertRaises(PvApiResponseStatusError):
            resp = self.loop.run_until_complete(go())

    # @aioresponses()
    # def test_activate_200(self, mocked):
    #     mocked.get('http://127.0.0.1/api/scenes',
    #                body='"ok"',
    #                status=200,
    #                headers={'content-type': 'application/json'})
    #     resp = self.loop.run_until_complete(self.resource.activate())
    #     self.assertEqual('ok', resp)
    #     request = mocked.requests[('GET', 'http://127.0.0.1/api/scenes')][-1]
    #     self.assertEqual({'sceneId': 37217}, request.kwargs['params'])
    #
    # @aioresponses()
    # def test_activate_201(self, mocked):
    #     """Test scene activation with wrong status."""
    #     mocked.get('http://127.0.0.1/api/scenes',
    #                body='"ok"',
    #                status=201,
    #                headers={'content-type': 'application/json'})
    #     with self.assertRaises(PvApiResponseStatusError):
    #         resp = self.loop.run_until_complete(self.resource.activate())
