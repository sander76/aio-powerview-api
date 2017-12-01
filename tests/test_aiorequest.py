import unittest
from json.decoder import JSONDecodeError

import aiohttp
import asyncio
from aioresponses import aioresponses
from aiopvapi.helpers.aiorequest import AioRequest, PvApiConnectionError, \
    PvApiResponseStatusError


class TestAioRequest(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.websession = aiohttp.ClientSession(loop=self.loop)
        self.request = AioRequest(self.loop, self.websession, timeout=.1)

    def tearDown(self):
        self.websession.close()

    @aioresponses()
    def test_get_status_200(self, mocked):
        """Test get with status 200."""
        mocked.get( 'http://127.0.0.1/1',
                              body='{"title": "test"}',
                              status=200,
                              headers={'content-type': 'application/json'})

        ret = self.loop.run_until_complete(self.request.get('http://127.0.0.1/1'))
        self.assertEqual({'title': 'test'}, ret)

    @aioresponses()
    def test_get_wrong_status(self, mocked):
        """Test get with some other status."""
        mocked.get('http://127.0.0.1/2',
                   status=201)
        with self.assertRaises(PvApiResponseStatusError):
            ret = self.loop.run_until_complete(self.request.get('http://127.0.0.1/2'))


    @aioresponses()
    def test_get_invalid_json(self, mocked):
        """Test get with invalid Json."""
        mocked.get('http://127.0.0.1/3',
                   body='{"title": "test}',
                   status=200,
                   headers={'content-type': 'application/json'})
        with self.assertRaises(JSONDecodeError):
            ret = self.loop.run_until_complete(self.request.get('http://127.0.0.1/3'))

    @aioresponses()
    def test_get_timeout(self, mocked):
        """Test get timeout."""
        with self.assertRaises(PvApiConnectionError):
            ret = self.loop.run_until_complete(self.request.get('http://127.0.0.1/4'))

    @aioresponses()
    def test_post_status_200(self, mocked):
        """Test good post requests (200)."""
        mocked.post('http://127.0.0.1/1', body='{"title": "test"}',
                    status=200,
                    headers={'content-type': 'application/json'})
        ret = self.loop.run_until_complete(self.request.post('http://127.0.0.1/1', {'a': 'b', 'c': 'd'}))
        self.assertEqual({'title': 'test'}, ret)

    @aioresponses()
    def test_post_status_201(self, mocked):
        """Test good post requests (201)."""
        mocked.post('http://127.0.0.1/2', body='{"title": "test"}',
                    status=201,
                    headers={'content-type': 'application/json'})
        ret = self.loop.run_until_complete(self.request.post('http://127.0.0.1/2', {'a': 'b', 'c': 'd'}))
        self.assertEqual({'title': 'test'}, ret)

    @aioresponses()
    def test_post_wrong_status(self, mocked):
        """Test post request with wrong status."""
        mocked.post('http://127.0.0.1/3', body='{"title": "test"}',
                    status=202,
                    headers={'content-type': 'application/json'})
        with self.assertRaises(PvApiResponseStatusError):
            ret = self.loop.run_until_complete(self.request.post('http://127.0.0.1/3', {'a': 'b', 'c': 'd'}))

    @aioresponses()
    def test_post_broken_json(self, mocked):
        """Test post request with broken JSON."""
        mocked.post('http://127.0.0.1/4', body='{"title": "test}',
                    status=200,
                    headers={'content-type': 'application/json'})
        with self.assertRaises(JSONDecodeError):
            ret = self.loop.run_until_complete(self.request.post('http://127.0.0.1/4', {'a': 'b', 'c': 'd'}))

    @aioresponses()
    def test_post_timeot(self, mocked):
        """Test post timeout."""
        with self.assertRaises(PvApiConnectionError):
            ret = self.loop.run_until_complete(self.request.post('http://127.0.0.1/5', {'a': 'b', 'c': 'd'}))

    @aioresponses()
    def test_put_status_200(self, mocked):
        """Test good put requests (200)."""
        mocked.put('http://127.0.0.1/1', body='{"title": "test"}',
                   status=200,
                   headers={'content-type': 'application/json'})
        ret = self.loop.run_until_complete(self.request.put('http://127.0.0.1/1', {'a': 'b', 'c': 'd'}))
        self.assertEqual({'title': 'test'}, ret)

    @aioresponses()
    def test_put_wrong_status(self, mocked):
        """Test put request with wrong status."""
        mocked.put('http://127.0.0.1/2', body='{"title": "test"}',
                   status=201,
                   headers={'content-type': 'application/json'})
        with self.assertRaises(PvApiResponseStatusError):
            ret = self.loop.run_until_complete(self.request.put('http://127.0.0.1/2', {'a': 'b', 'c': 'd'}))

    @aioresponses()
    def test_put_broken_json(self, mocked):
        """Test put request with broken JSON."""
        mocked.put('http://127.0.0.1/4', body='{"title": "test}',
                   status=200,
                   headers={'content-type': 'application/json'})
        with self.assertRaises(JSONDecodeError):
            ret = self.loop.run_until_complete(self.request.put('http://127.0.0.1/4', {'a': 'b', 'c': 'd'}))

    @aioresponses()
    def test_put_timeout(self, mocked):
        """Test put request with timeout."""
        with self.assertRaises(PvApiConnectionError):
            ret = self.loop.run_until_complete(self.request.put('http://127.0.0.1/5', {'a': 'b', 'c': 'd'}))

    @aioresponses()
    def test_delete_status_200(self, mocked):
        """Test delete request with status 200"""
        mocked.delete('http://127.0.0.1/1',
                      status=200,
                      headers={'content-type': 'application/json'})
        ret = self.loop.run_until_complete(self.request.delete('http://127.0.0.1/1'))
        self.assertIsNone(ret)

    @aioresponses()
    def test_delete_status_204(self, mocked):
        """Test delete request with status 204"""
        mocked.delete('http://127.0.0.1/2', body='{"title": "test"}',
                      status=204,
                      headers={'content-type': 'application/json'})
        ret = self.loop.run_until_complete(self.request.delete('http://127.0.0.1/2'))
        self.assertTrue(ret)

    @aioresponses()
    def test_delete_wrong_status(self, mocked):
        """Test delete request with wrong status"""
        mocked.delete('http://127.0.0.1/3', body='{"title": "test"}',
                      status=202,
                      headers={'content-type': 'application/json'})
        with self.assertRaises(PvApiResponseStatusError):
            ret = self.loop.run_until_complete(self.request.delete('http://127.0.0.1/3'))

    @aioresponses()
    def test_delete_timeout(self, mocked):
        """Test delete request with timeout"""
        with self.assertRaises(PvApiConnectionError):
            ret = self.loop.run_until_complete(self.request.delete('http://127.0.0.1/5'))
