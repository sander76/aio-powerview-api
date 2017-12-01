import json
from aioresponses import aioresponses
from aiopvapi.resources.shade import Shade
from test_apiresource import TestApiResource

SHADE_RAW_DATA = {"id": 29889, "type": 6, "batteryStatus": 0, "batteryStrength": 0,
                  "name": "UmlnaHQ=", "roomId": 12372,
                  "groupId": 18480, "positions": {"posKind1": 1, "position1": 0},
                  "firmware": {"revision": 1, "subRevision": 8, "build": 1944}}


class TestShade(TestApiResource):

    def get_resource_raw_data(self):
        return SHADE_RAW_DATA

    def get_resource_uri(self):
        return 'http://127.0.0.1/api/shades/29889'

    def get_resource(self, loop, websession):
        return Shade(SHADE_RAW_DATA, 'http://127.0.0.1', loop, websession)

    def test_name_property(self):
        # No name_unicode, so base64 encoded is returned
        self.assertEqual('UmlnaHQ=', self.resource.name)

    @aioresponses()
    def test_add_shade_to_room(self, mocked):
        mocked.put('http://127.0.0.1/api/shades/29889',
                   body='"ok"',
                   status=200,
                   headers={'content-type': 'application/json'})
        resp = self.loop.run_until_complete(self.resource.add_shade_to_room(123))
        self.assertEqual(resp,'ok')
        request = mocked.requests[('PUT', 'http://127.0.0.1/api/shades/29889')][-1]
        self.assertEqual({"shade": {"id": 29889, "roomId": 123}},
                        request.kwargs['json'])

    @aioresponses()
    def test_open(self, mocked):
        mocked.put('http://127.0.0.1/api/shades/29889',
                   body='"ok"',
                   status=200,
                   headers={'content-type': 'application/json'})
        resp = self.loop.run_until_complete(self.resource.open())
        self.assertIsNone(resp)
        request = mocked.requests[('PUT', 'http://127.0.0.1/api/shades/29889')][-1]
        self.assertEqual({"shade": {"id": 29889, "positions": {"posKind1": 1, "position1": 65535}}},
                         request.kwargs['json'])

    @aioresponses()
    def test_close(self, mocked):
        mocked.put('http://127.0.0.1/api/shades/29889',
                   body='"ok"',
                   status=200,
                   headers={'content-type': 'application/json'})
        resp = self.loop.run_until_complete(self.resource.close())
        self.assertIsNone(resp)
        request = mocked.requests[('PUT', 'http://127.0.0.1/api/shades/29889')][-1]
        self.assertEqual({"shade": {"id": 29889, "positions": {"posKind1": 1, "position1": 0}}},
                         request.kwargs['json'])

    @aioresponses()
    def test_move_to(self, mocked):
        mocked.put('http://127.0.0.1/api/shades/29889',
                   body='"ok"',
                   status=200,
                   headers={'content-type': 'application/json'})
        resp = self.loop.run_until_complete(self.resource.move_to(3000, 200))
        self.assertIsNone(resp)
        request = mocked.requests[('PUT', 'http://127.0.0.1/api/shades/29889')][-1]
        self.assertEqual({"shade": {"id": 29889, "positions": {"posKind1": 1, "position1": 3000}}},
                         request.kwargs['json'])

    @aioresponses()
    def test_refresh(self, mocked):
        data = {'shade': dict(SHADE_RAW_DATA)}
        data['shade']['name'] = 'name'
        mocked.get('http://127.0.0.1/api/shades/29889',
                   body=json.dumps(data),
                   status=200,
                   headers={'content-type': 'application/json'})
        self.loop.run_until_complete(self.resource.refresh())
        self.assertEqual('name', self.resource.name)
