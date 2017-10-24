from mocket.mocket import mocketize, Mocket
from mocket.mockhttp import Entry
import json

from resources.shade import Shade
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

    @mocketize
    def test_add_shade_to_room(self):
        Entry.single_register(Entry.PUT, 'http://127.0.0.1/api/shades/29889',
                               body='"ok"',
                               status=200,
                               headers={'content-type': 'application/json'})
        resp = self.loop.run_until_complete(self.resource.add_shade_to_room(123))
        self.assertEqual('ok', resp)
        request = Mocket.last_request()
        self.assertEqual({"shade": {"id": 29889, "roomId": 123}},
                         json.loads(request.body))
        self.assertEqual('/api/shades/29889', request.path)

    @mocketize
    def test_open(self):
        Entry.single_register(Entry.PUT, 'http://127.0.0.1/api/shades/29889',
                               body='"ok"',
                               status=200,
                               headers={'content-type': 'application/json'})
        resp = self.loop.run_until_complete(self.resource.open())
        self.assertEqual('ok', resp)
        request = Mocket.last_request()
        self.assertEqual({"shade": {"id": 29889, "positions": {"posKind1": 1, "position1": 65535}}},
                         json.loads(request.body))
        self.assertEqual('/api/shades/29889', request.path)

    @mocketize
    def test_close(self):
        Entry.single_register(Entry.PUT, 'http://127.0.0.1/api/shades/29889',
                               body='"ok"',
                               status=200,
                               headers={'content-type': 'application/json'})
        resp = self.loop.run_until_complete(self.resource.close())
        self.assertEqual('ok', resp)
        request = Mocket.last_request()
        self.assertEqual({"shade": {"id": 29889, "positions": {"posKind1": 1, "position1": 0}}},
                         json.loads(request.body))
        self.assertEqual('/api/shades/29889', request.path)

    @mocketize
    def test_move_to(self):
        Entry.single_register(Entry.PUT, 'http://127.0.0.1/api/shades/29889',
                               body='"ok"',
                               status=200,
                               headers={'content-type': 'application/json'})
        resp = self.loop.run_until_complete(self.resource.move_to(3000, 200))
        self.assertEqual('ok', resp)
        request = Mocket.last_request()
        self.assertEqual({"shade": {"id": 29889, "positions": {"posKind1": 1, "position1": 3000}}},
                         json.loads(request.body))
        self.assertEqual('/api/shades/29889', request.path)

    @mocketize
    def test_refresh(self):
        data = {'shade': dict(SHADE_RAW_DATA)}
        data['shade']['name'] = 'name'
        Entry.single_register(Entry.GET, 'http://127.0.0.1/api/shades/29889',
                               body=json.dumps(data),
                               status=200,
                               headers={'content-type': 'application/json'}, match_querystring=False)
        self.loop.run_until_complete(self.resource.refresh())
        self.assertEqual('name', self.resource.name)
