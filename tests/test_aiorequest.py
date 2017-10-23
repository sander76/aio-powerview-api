import unittest
import aiohttp
import asyncio
from mocket.plugins.httpretty import HTTPretty, httprettified

from aiopvapi.helpers.aiorequest import AioRequest


class TestAioRequest(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.websession = aiohttp.ClientSession(loop=self.loop)
        self.request = AioRequest(self.loop, self.websession, timeout=.1)

    def tearDown(self):
        self.websession.close()

    @httprettified
    def test_get_status_200(self):
        """Test get with status 200."""
        HTTPretty.register_uri(HTTPretty.GET, 'http://127.0.0.1/1',
                               body='{"title": "test"}',
                               status=200,
                               content_type='application/json')

        ret = self.loop.run_until_complete(self.request.get('http://127.0.0.1/1'))
        self.assertEqual({'title': 'test'}, ret)

    @httprettified
    def test_get_wrong_status(self):
        """Test get with some other status."""
        HTTPretty.register_uri(HTTPretty.GET, 'http://127.0.0.1/2',
                               status=201)
        ret = self.loop.run_until_complete(self.request.get('http://127.0.0.1/2'))
        self.assertIsNone(ret)

    @httprettified
    def test_get_invalid_json(self):
        """Test get with invalid Json."""
        HTTPretty.register_uri(HTTPretty.GET, 'http://127.0.0.1/3',
                               body='{"title": "test}',
                               status=200,
                               content_type='application/json')
        ret = self.loop.run_until_complete(self.request.get('http://127.0.0.1/3'))
        self.assertIsNone(ret)

    @httprettified
    def test_get_timeout(self):
        """Test get timeout."""
        ret = self.loop.run_until_complete(self.request.get('http://127.0.0.1/4'))
        self.assertIsNone(ret)


    @httprettified
    def test_post_status_200(self):
        """Test good post requests (200)."""
        HTTPretty.register_uri(HTTPretty.POST, 'http://127.0.0.1/1', body='{"title": "test"}',
                               status=200,
                               content_type='application/json')
        ret = self.loop.run_until_complete(self.request.post('http://127.0.0.1/1', {'a': 'b', 'c':'d'}))
        self.assertEqual(({'title':'test'}, 200), ret)

    @httprettified
    def test_post_status_201(self):
        """Test good post requests (201)."""
        HTTPretty.register_uri(HTTPretty.POST, 'http://127.0.0.1/2', body='{"title": "test"}',
                               status=201,
                               content_type='application/json')
        ret = self.loop.run_until_complete(self.request.post('http://127.0.0.1/2', {'a': 'b', 'c': 'd'}))
        self.assertEqual(({'title': 'test'}, 201), ret)

    @httprettified
    def test_post_wrong_status(self):
        """Test post request with wrong status."""
        HTTPretty.register_uri(HTTPretty.POST, 'http://127.0.0.1/3', body='{"title": "test"}',
                               status=202,
                               content_type='application/json')
        ret = self.loop.run_until_complete(self.request.post('http://127.0.0.1/3', {'a': 'b', 'c': 'd'}))
        self.assertEqual((None, 202), ret)

    @httprettified
    def test_post_broken_json(self):
        """Test post request with broken JSON."""
        HTTPretty.register_uri(HTTPretty.POST, 'http://127.0.0.1/4', body='{"title": "test}',
                               status=200,
                               content_type='application/json')
        ret = self.loop.run_until_complete(self.request.post('http://127.0.0.1/4', {'a': 'b', 'c': 'd'}))
        self.assertEqual((None, 200), ret)

    @httprettified
    def test_post_timeot(self):
        """Test post timeout."""
        ret = self.loop.run_until_complete(self.request.post('http://127.0.0.1/5', {'a': 'b', 'c': 'd'}))
        self.assertEqual((None, None), ret)

    @httprettified
    def test_put_status_200(self):
        """Test good put requests (200)."""
        HTTPretty.register_uri(HTTPretty.PUT, 'http://127.0.0.1/1', body='{"title": "test"}',
                               status=200,
                               content_type='application/json')
        ret = self.loop.run_until_complete(self.request.put('http://127.0.0.1/1', {'a': 'b', 'c': 'd'}))
        self.assertEqual(({'title': 'test'}, 200), ret)

    @httprettified
    def test_put_wrong_status(self):
        """Test put request with wrong status."""
        HTTPretty.register_uri(HTTPretty.PUT, 'http://127.0.0.1/2', body='{"title": "test"}',
                               status=201,
                               content_type='application/json')
        ret = self.loop.run_until_complete(self.request.put('http://127.0.0.1/2', {'a': 'b', 'c': 'd'}))
        self.assertEqual((None, 201), ret)

    @httprettified
    def test_put_broken_json(self):
        """Test put request with broken JSON."""
        HTTPretty.register_uri(HTTPretty.PUT, 'http://127.0.0.1/4', body='{"title": "test}',
                               status=200,
                               content_type='application/json')
        ret = self.loop.run_until_complete(self.request.put('http://127.0.0.1/4', {'a': 'b', 'c': 'd'}))
        self.assertEqual((None, 200), ret)

    @httprettified
    def test_put_timeout(self):
        """Test put request with timeout."""
        ret = self.loop.run_until_complete(self.request.put('http://127.0.0.1/5', {'a': 'b', 'c': 'd'}))
        self.assertEqual((None, None), ret)

    @httprettified
    def test_delete_status_200(self):
        """Test delete request with status 200"""
        HTTPretty.register_uri(HTTPretty.DELETE, 'http://127.0.0.1/1', body='{"title": "test"}',
                               status=200,
                               content_type='application/json')
        ret = self.loop.run_until_complete(self.request.delete('http://127.0.0.1/1'))
        self.assertEqual(200, ret)

    @httprettified
    def test_delete_status_204(self):
        """Test delete request with status 204"""
        HTTPretty.register_uri(HTTPretty.DELETE, 'http://127.0.0.1/2', body='{"title": "test"}',
                               status=204,
                               content_type='application/json')
        ret = self.loop.run_until_complete(self.request.delete('http://127.0.0.1/2'))
        self.assertEqual(204, ret)

    @httprettified
    def test_delete_wrong_status(self):
        """Test delete request with wrong status"""

        HTTPretty.register_uri(HTTPretty.DELETE, 'http://127.0.0.1/3', body='{"title": "test"}',
                               status=202,
                               content_type='application/json')
        ret = self.loop.run_until_complete(self.request.delete('http://127.0.0.1/3'))
        self.assertEqual(202, ret)

    @httprettified
    def test_delete_timeout(self):
        """Test delete request with timeout"""
        ret = self.loop.run_until_complete(self.request.delete('http://127.0.0.1/5'))
        self.assertEqual(False, ret)
