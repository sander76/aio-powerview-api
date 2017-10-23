import unittest
import aiohttp
import asyncio
from mocket.plugins.httpretty import HTTPretty, httprettified
from aiopvapi.shades import Shades

RETURN_VALUE = """
{"shadeIds":[29889,56112],"shadeData":[
{"id":29889,"type":6,"batteryStatus":0,"batteryStrength":0,"name":"UmlnaHQ=","roomId":12372,"groupId":18480,
"positions":{"posKind1":1,"position1":0},"firmware":{"revision":1,"subRevision":8,"build":1944}},
{"id":56112,"type":16,"batteryStatus":4,"batteryStrength":180,"name":"UGF0aW8gRG9vcnM=",
"roomId":15103,"groupId":49380,"positions":{"posKind1":3,"position1":65535},
"firmware":{"revision":1,"subRevision":8,"build":1944}}]}
"""


class TestShades(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.websession = aiohttp.ClientSession(loop=self.loop)
        self.shades = Shades('127.0.0.1', self.loop, self.websession)

    def tearDown(self):
        self.websession.close()

    @httprettified
    def test_get_resources_200(self):
        """Test get resources with status 200."""
        HTTPretty.register_uri(HTTPretty.GET, 'http://127.0.0.1/api/shades',
                               body=RETURN_VALUE,
                               status=200,
                               content_type='application/json')
        resources = self.loop.run_until_complete(self.shades.get_resources())
        self.assertEqual(2, len(resources['shadeIds']))
        self.assertEqual(2, len(resources['shadeData']))
        self.assertEqual('Right',
                         resources['shadeData'][0]['name_unicode'])
        self.assertEqual('Patio Doors',
                         resources['shadeData'][1]['name_unicode'])

    @httprettified
    def test_get_resources_201(self):
        """Test get resources with wrong status."""
        HTTPretty.register_uri(HTTPretty.GET, 'http://127.0.0.1/api/shades',
                               body=RETURN_VALUE,
                               status=201,
                               content_type='application/json')
        resources = self.loop.run_until_complete(self.shades.get_resources())
        self.assertIsNone(resources)
