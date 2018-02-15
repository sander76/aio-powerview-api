from json.decoder import JSONDecodeError

from aiopvapi.helpers.aiorequest import PvApiConnectionError, \
    PvApiResponseStatusError
from tests.fake_server import TestFakeServer, make_url


class TestAioRequest(TestFakeServer):

    def test_get_status_200(self):
        """Test get with status 200."""

        async def go():
            await self.start_fake_server()
            return await self.request.get(make_url('test_get_status_200'))

        ret = self.loop.run_until_complete(go())

        self.assertEqual({'title': 'test'}, ret)

    def test_get_wrong_status(self):
        """Test get with some other status."""

        async def go():
            await self.start_fake_server()
            return await self.request.get(make_url('wrong_status'))

        with self.assertRaises(PvApiResponseStatusError):
            ret = self.loop.run_until_complete(go())

    def test_get_invalid_json(self):
        """Test get with invalid Json."""

        async def go():
            await self.start_fake_server()
            return await self.request.get(make_url('invalid_json'))

        with self.assertRaises(JSONDecodeError):
            ret = self.loop.run_until_complete(go())

    def test_get_timeout(self):
        """Test get timeout."""

        async def go():
            await self.start_fake_server()
            return await self.request.get(make_url('get_timeout'))

        with self.assertRaises(PvApiConnectionError):
            ret = self.loop.run_until_complete(go())

    def test_post_status_200(self):
        """Test good post requests (200)."""

        async def go():
            await self.start_fake_server()
            return await self.request.post(make_url('post_status_200'),
                                           {'a': 'b', 'c': 'd'})

        ret = self.loop.run_until_complete(go())
        self.assertEqual({'a': 'b', 'c': 'd'}, ret)

    def test_post_status_201(self):
        """Test good post requests (201)."""

        async def go():
            await self.start_fake_server()
            return await self.request.post(make_url('post_status_201'),
                                           {'a': 'b', 'c': 'd'})

        ret = self.loop.run_until_complete(go())
        self.assertEqual({'a': 'b', 'c': 'd'}, ret)

    #
    # def test_post_wrong_status(self):
    #     """Test post request with wrong status."""
    #     mocked.post('http://127.0.0.1/3', body='{"title": "test"}',
    #                 status=202,
    #                 headers={'content-type': 'application/json'})
    #     with self.assertRaises(PvApiResponseStatusError):
    #         ret = self.loop.run_until_complete(
    #             self.request.post('http://127.0.0.1/3', {'a': 'b', 'c': 'd'}))
    #
    #
    # def test_post_broken_json(self):
    #     """Test post request with broken JSON."""
    #     mocked.post('http://127.0.0.1/4', body='{"title": "test}',
    #                 status=200,
    #                 headers={'content-type': 'application/json'})
    #     with self.assertRaises(JSONDecodeError):
    #         ret = self.loop.run_until_complete(
    #             self.request.post('http://127.0.0.1/4', {'a': 'b', 'c': 'd'}))
    #
    #
    # def test_post_timeot(self):
    #     """Test post timeout."""
    #     with self.assertRaises(PvApiConnectionError):
    #         ret = self.loop.run_until_complete(
    #             self.request.post('http://127.0.0.1/5', {'a': 'b', 'c': 'd'}))
    #
    #
    # def test_put_status_200(self):
    #     """Test good put requests (200)."""
    #     mocked.put('http://127.0.0.1/1', body='{"title": "test"}',
    #                status=200,
    #                headers={'content-type': 'application/json'})
    #     ret = self.loop.run_until_complete(
    #         self.request.put('http://127.0.0.1/1', {'a': 'b', 'c': 'd'}))
    #     self.assertEqual({'title': 'test'}, ret)
    #
    #
    # def test_put_wrong_status(self):
    #     """Test put request with wrong status."""
    #     mocked.put('http://127.0.0.1/2', body='{"title": "test"}',
    #                status=201,
    #                headers={'content-type': 'application/json'})
    #     with self.assertRaises(PvApiResponseStatusError):
    #         ret = self.loop.run_until_complete(
    #             self.request.put('http://127.0.0.1/2', {'a': 'b', 'c': 'd'}))
    #
    #
    # def test_put_broken_json(self):
    #     """Test put request with broken JSON."""
    #     mocked.put('http://127.0.0.1/4', body='{"title": "test}',
    #                status=200,
    #                headers={'content-type': 'application/json'})
    #     with self.assertRaises(JSONDecodeError):
    #         ret = self.loop.run_until_complete(
    #             self.request.put('http://127.0.0.1/4', {'a': 'b', 'c': 'd'}))
    #
    #
    # def test_put_timeout(self):
    #     """Test put request with timeout."""
    #     with self.assertRaises(PvApiConnectionError):
    #         ret = self.loop.run_until_complete(
    #             self.request.put('http://127.0.0.1/5', {'a': 'b', 'c': 'd'}))
    #
    #
    # def test_delete_status_200(self):
    #     """Test delete request with status 200"""
    #     mocked.delete('http://127.0.0.1/1',
    #                   status=200,
    #                   headers={'content-type': 'application/json'})
    #     ret = self.loop.run_until_complete(
    #         self.request.delete('http://127.0.0.1/1'))
    #     self.assertIsNone(ret)
    #
    #
    # def test_delete_status_204(self):
    #     """Test delete request with status 204"""
    #     mocked.delete('http://127.0.0.1/2', body='{"title": "test"}',
    #                   status=204,
    #                   headers={'content-type': 'application/json'})
    #     ret = self.loop.run_until_complete(
    #         self.request.delete('http://127.0.0.1/2'))
    #     self.assertTrue(ret)
    #
    #
    # def test_delete_wrong_status(self):
    #     """Test delete request with wrong status"""
    #     mocked.delete('http://127.0.0.1/3', body='{"title": "test"}',
    #                   status=202,
    #                   headers={'content-type': 'application/json'})
    #     with self.assertRaises(PvApiResponseStatusError):
    #         ret = self.loop.run_until_complete(
    #             self.request.delete('http://127.0.0.1/3'))
    #
    #
    # def test_delete_timeout(self):
    #     """Test delete request with timeout"""
    #     with self.assertRaises(PvApiConnectionError):
    #         ret = self.loop.run_until_complete(
    #             self.request.delete('http://127.0.0.1/5'))
