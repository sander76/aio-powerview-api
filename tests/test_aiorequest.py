import unittest
import aiohttp
import asyncio
from mocket.mocket import mocketize
from mocket.mockhttp import Entry
from aiopvapi.helpers.aiorequest import AioRequest


class TestAioRequest(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.websession = aiohttp.ClientSession(loop=self.loop)
        self.request = AioRequest(self.loop, self.websession, timeout=.1)

    def tearDown(self):
        self.websession.close()

    @mocketize
    def test_get_status_200(self):
        """Test get with status 200."""
        Entry.single_register(Entry.GET, 'http://127.0.0.1/1',
                               body='{"title": "test"}',
                               status=200,
                               headers={'content-type': 'application/json'})

        ret = self.loop.run_until_complete(self.request.get('http://127.0.0.1/1'))
        self.assertEqual({'title': 'test'}, ret)

    @mocketize
    def test_get_wrong_status(self):
        """Test get with some other status."""
        Entry.single_register(Entry.GET, 'http://127.0.0.1/2',
                               status=201)
        ret = self.loop.run_until_complete(self.request.get('http://127.0.0.1/2'))
        self.assertIsNone(ret)

    @mocketize
    def test_get_invalid_json(self):
        """Test get with invalid Json."""
        Entry.single_register(Entry.GET, 'http://127.0.0.1/3',
                               body='{"title": "test}',
                               status=200,
                               headers={'content-type': 'application/json'})
        ret = self.loop.run_until_complete(self.request.get('http://127.0.0.1/3'))
        self.assertIsNone(ret)

    @mocketize
    def test_get_timeout(self):
        """Test get timeout."""
        ret = self.loop.run_until_complete(self.request.get('http://127.0.0.1/4'))
        self.assertIsNone(ret)


    @mocketize
    def test_post_status_200(self):
        """Test good post requests (200)."""
        Entry.single_register(Entry.POST, 'http://127.0.0.1/1', body='{"title": "test"}',
                               status=200,
                               headers={'content-type': 'application/json'})
        ret = self.loop.run_until_complete(self.request.post('http://127.0.0.1/1', {'a': 'b', 'c':'d'}))
        self.assertEqual(({'title':'test'}, 200), ret)

    @mocketize
    def test_post_status_201(self):
        """Test good post requests (201)."""
        Entry.single_register(Entry.POST, 'http://127.0.0.1/2', body='{"title": "test"}',
                               status=201,
                               headers={'content-type': 'application/json'})
        ret = self.loop.run_until_complete(self.request.post('http://127.0.0.1/2', {'a': 'b', 'c': 'd'}))
        self.assertEqual(({'title': 'test'}, 201), ret)

    @mocketize
    def test_post_wrong_status(self):
        """Test post request with wrong status."""
        Entry.single_register(Entry.POST, 'http://127.0.0.1/3', body='{"title": "test"}',
                               status=202,
                               headers={'content-type': 'application/json'})
        ret = self.loop.run_until_complete(self.request.post('http://127.0.0.1/3', {'a': 'b', 'c': 'd'}))
        self.assertEqual((None, 202), ret)

    @mocketize
    def test_post_broken_json(self):
        """Test post request with broken JSON."""
        Entry.single_register(Entry.POST, 'http://127.0.0.1/4', body='{"title": "test}',
                               status=200,
                               headers={'content-type': 'application/json'})
        ret = self.loop.run_until_complete(self.request.post('http://127.0.0.1/4', {'a': 'b', 'c': 'd'}))
        self.assertEqual((None, 200), ret)

    @mocketize
    def test_post_timeot(self):
        """Test post timeout."""
        ret = self.loop.run_until_complete(self.request.post('http://127.0.0.1/5', {'a': 'b', 'c': 'd'}))
        self.assertEqual((None, None), ret)

    @mocketize
    def test_put_status_200(self):
        """Test good put requests (200)."""
        Entry.single_register(Entry.PUT, 'http://127.0.0.1/1', body='{"title": "test"}',
                               status=200,
                               headers={'content-type': 'application/json'})
        ret = self.loop.run_until_complete(self.request.put('http://127.0.0.1/1', {'a': 'b', 'c': 'd'}))
        self.assertEqual(({'title': 'test'}, 200), ret)

    @mocketize
    def test_put_wrong_status(self):
        """Test put request with wrong status."""
        Entry.single_register(Entry.PUT, 'http://127.0.0.1/2', body='{"title": "test"}',
                               status=201,
                               headers={'content-type': 'application/json'})
        ret = self.loop.run_until_complete(self.request.put('http://127.0.0.1/2', {'a': 'b', 'c': 'd'}))
        self.assertEqual((None, 201), ret)

    @mocketize
    def test_put_broken_json(self):
        """Test put request with broken JSON."""
        Entry.single_register(Entry.PUT, 'http://127.0.0.1/4', body='{"title": "test}',
                               status=200,
                               headers={'content-type': 'application/json'})
        ret = self.loop.run_until_complete(self.request.put('http://127.0.0.1/4', {'a': 'b', 'c': 'd'}))
        self.assertEqual((None, 200), ret)

    @mocketize
    def test_put_timeout(self):
        """Test put request with timeout."""
        ret = self.loop.run_until_complete(self.request.put('http://127.0.0.1/5', {'a': 'b', 'c': 'd'}))
        self.assertEqual((None, None), ret)

    @mocketize
    def test_delete_status_200(self):
        """Test delete request with status 200"""
        Entry.single_register(Entry.DELETE, 'http://127.0.0.1/1', body='{"title": "test"}',
                               status=200,
                               headers={'content-type': 'application/json'})
        ret = self.loop.run_until_complete(self.request.delete('http://127.0.0.1/1'))
        self.assertEqual(200, ret)

    @mocketize
    def test_delete_status_204(self):
        """Test delete request with status 204"""
        Entry.single_register(Entry.DELETE, 'http://127.0.0.1/2', body='{"title": "test"}',
                               status=204,
                               headers={'content-type': 'application/json'})
        ret = self.loop.run_until_complete(self.request.delete('http://127.0.0.1/2'))
        self.assertEqual(204, ret)

    @mocketize
    def test_delete_wrong_status(self):
        """Test delete request with wrong status"""

        Entry.single_register(Entry.DELETE, 'http://127.0.0.1/3', body='{"title": "test"}',
                               status=202,
                               headers={'content-type': 'application/json'})
        ret = self.loop.run_until_complete(self.request.delete('http://127.0.0.1/3'))
        self.assertEqual(202, ret)

    @mocketize
    def test_delete_timeout(self):
        """Test delete request with timeout"""
        ret = self.loop.run_until_complete(self.request.delete('http://127.0.0.1/5'))
        self.assertEqual(False, ret)
