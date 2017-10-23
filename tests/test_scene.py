from mocket.plugins.httpretty import HTTPretty, httprettified

from aiopvapi.resources.scene import Scene
from test_apiresource import TestApiResource

SCENE_RAW_DATA = {"roomId": 26756, "name": "RGluaW5nIFZhbmVzIE9wZW4=",
                  "colorId": 0, "iconId": 0, "id": 37217, "order": 1}


class TestScene(TestApiResource):

    def get_resource_raw_data(self):
        return SCENE_RAW_DATA

    def get_resource_uri(self):
        return 'http://127.0.0.1/api/scenes/37217'

    def get_resource(self, loop, websession):
        return Scene(SCENE_RAW_DATA, 'http://127.0.0.1', loop, websession)

    def test_name_property(self):
        # No name_unicode, so base64 encoded is returned
        self.assertEqual('RGluaW5nIFZhbmVzIE9wZW4=', self.resource.name)

    def test_room_id_property(self):
        self.assertEqual(26756, self.resource.room_id)

    @httprettified
    def test_activate_200(self):
        HTTPretty.register_uri(HTTPretty.GET, 'http://127.0.0.1/api/scenes',
                               body='"ok"',
                               status=200,
                               content_type='application/json')
        resp = self.loop.run_until_complete(self.resource.activate())
        self.assertEqual('ok', resp)
        request = HTTPretty.last_request
        self.assertEqual('/api/scenes?sceneId=37217', request.path)
        self.assertEqual('GET', request.command)

    @httprettified
    def test_activate_201(self):
        """Test scene activation with wrong status."""
        HTTPretty.register_uri(HTTPretty.GET, 'http://127.0.0.1/api/scenes',
                               body='"ok"',
                               status=201,
                               content_type='application/json')
        resp = self.loop.run_until_complete(self.resource.activate())
        self.assertIsNone(resp)