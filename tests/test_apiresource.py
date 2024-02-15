from unittest.mock import Mock

from aiopvapi.helpers.api_base import ApiResource, ApiEntryPoint
from aiopvapi.helpers.aiorequest import AioRequest
from tests.fake_server import TestFakeServer, FAKE_BASE_URL


class TestApiResource(TestFakeServer):
    def get_resource_raw_data(self):
        return {"id": 1}

    def get_resource_uri(self):
        return "http://{}/base/1".format(FAKE_BASE_URL)

    def get_resource(self):
        """Get the resource being tested."""
        _request = Mock(spec=AioRequest)
        _request.hub_ip = FAKE_BASE_URL
        _request.api_version = 2
        _request.api_path = "api"
        return ApiResource(_request, "base", self.get_resource_raw_data())

    def setUp(self):
        super().setUp()
        self.resource = self.get_resource()

    def test_id_property(self):
        """Test id property."""
        self.assertEqual(self.get_resource_raw_data()["id"], self.resource.id)
        # Try to replace raw data, id shouldn't change!
        self.resource.raw_data = {"id": 2}
        self.assertEqual(self.get_resource_raw_data()["id"], self.resource.id)

    def test_full_path(self):
        self.assertEqual(
            self.resource.base_path, "http://{}/api/base".format(FAKE_BASE_URL)
        )

    def test_name_property(self):
        """Test name property."""
        self.assertEqual("", self.resource.name)
        self.resource.raw_data = {"name": "Name"}
        self.assertEqual("Name", self.resource.name)
        self.resource.raw_data = {"name": "Name", "name_unicode": "Name Unicode"}
        self.assertEqual("Name Unicode", self.resource.name)

    def test_raw_data_property(self):
        """Test raw_data getter/setter."""
        self.assertEqual(self.get_resource_raw_data(), self.resource.raw_data)
        # Set new raw data
        data = {"name": "name"}
        self.resource.raw_data = data
        self.assertEqual({"name": "name"}, self.resource.raw_data)
        # Try to change the original data, resource should have made a copy!
        data["name"] = "no name"
        self.assertEqual({"name": "name"}, self.resource.raw_data)


class TestApiResource_V3(TestApiResource):
    def get_resource(self):
        """Get the resource being tested."""
        _request = Mock()
        _request.hub_ip = FAKE_BASE_URL
        _request.api_version = 3
        _request.api_path = "home"
        return ApiResource(_request, "base", self.get_resource_raw_data())

    def test_full_path(self):
        self.assertEqual(
            self.resource.base_path, "http://{}/home/base".format(FAKE_BASE_URL)
        )

    # def test_delete_200(self, mocked):
    #     """Test delete resources with status 200."""
    #     mocked.delete(self.get_resource_uri(),
    #                   body="",
    #                   status=200,
    #                   headers={'content-type': 'application/json'})
    #     val = self.loop.run_until_complete(self.resource.delete())
    #     self.assertIsNone(val)
    #
    # @aioresponses()
    # def test_delete_204(self, mocked):
    #     """Test delete resources with status 204."""
    #     mocked.delete(self.get_resource_uri(),
    #                   body="",
    #                   status=204,
    #                   headers={'content-type': 'application/json'})
    #     self.assertTrue(self.loop.run_until_complete(self.resource.delete()))
    #
    # @aioresponses()
    # def test_delete_201(self, mocked):
    #     """Test delete resources with wrong status."""
    #     mocked.delete(self.get_resource_uri(),
    #                   body="",
    #                   status=201,
    #                   headers={'content-type': 'application/json'})
    #     with self.assertRaises(PvApiResponseStatusError):
    #         self.loop.run_until_complete(self.resource.delete())


test_data1 = {
    "sceneMemberIds": [60113, 27759, 63292, 18627, 59345, 32461, 63181, 45145, 64087],
    "sceneMemberData": [
        {
            "id": 60113,
            "sceneId": 64040,
            "shadeId": 18390,
            "positions": {"position1": 65535, "posKind1": 1},
        },
        {
            "id": 27759,
            "sceneId": 34037,
            "shadeId": 11155,
            "positions": {
                "position1": 7563,
                "posKind1": 1,
                "position2": 16157,
                "posKind2": 2,
            },
        },
        {
            "id": 63292,
            "sceneId": 53808,
            "shadeId": 11155,
            "positions": {"position1": 0, "posKind1": 1, "position2": 0, "posKind2": 2},
        },
        {
            "positions": {
                "posKind2": 2,
                "position2": 42144,
                "posKind1": 1,
                "position1": 23390,
            },
            "id": 18627,
            "sceneId": 43436,
            "shadeId": 11155,
            "type": 0,
        },
        {
            "id": 59345,
            "sceneId": 39635,
            "shadeId": 11155,
            "positions": {
                "position1": 45598,
                "posKind1": 1,
                "position2": 0,
                "posKind2": 2,
            },
        },
        {
            "id": 32461,
            "sceneId": 34037,
            "shadeId": 18390,
            "positions": {"position1": 65535, "posKind1": 1},
        },
        {
            "positions": {"posKind1": 1, "position1": 58134},
            "id": 63181,
            "sceneId": 43436,
            "shadeId": 18390,
            "type": 0,
        },
        {
            "id": 45145,
            "sceneId": 64040,
            "shadeId": 11155,
            "positions": {
                "position1": 8404,
                "posKind1": 1,
                "position2": 42209,
                "posKind2": 2,
            },
        },
        {
            "id": 64087,
            "sceneId": 49867,
            "shadeId": 18390,
            "positions": {"posKind1": 1, "position1": 0},
            "type": 0,
        },
    ],
}


def test_clean_names():
    req = Mock()
    req.hub_ip = "123.123.123"
    req.api_version = 2
    req.api_path = "api"
    api = ApiEntryPoint(req, "abc")
    try:
        api._sanitize_resources(test_data1)
    except NotImplementedError:
        pass
