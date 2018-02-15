import unittest
from unittest.mock import Mock

import aiohttp
import asyncio

from aiopvapi.helpers.aiorequest import PvApiResponseStatusError, AioRequest
from aiopvapi.helpers.api_base import ApiResource
from tests.fake_server import TestFakeServer, FAKE_BASE_URL


class TestApiResource(TestFakeServer):

    def get_resource_raw_data(self):
        return {'id': 1}

    def get_resource_uri(self):
        return 'http://{}/base/1'.format(FAKE_BASE_URL)

    def get_resource(self):
        """Get the resource being tested."""
        _request = Mock()
        _request.hub_ip = FAKE_BASE_URL
        return ApiResource(_request, 'base', self.get_resource_raw_data())

    def setUp(self):
        super().setUp()
        self.resource = self.get_resource()

    def test_id_property(self):
        """Test id property."""
        self.assertEqual(self.get_resource_raw_data()['id'], self.resource.id)
        # Try to replace raw data, id shouldn't change!
        self.resource.raw_data = {'id': 2}
        self.assertEqual(self.get_resource_raw_data()['id'], self.resource.id)

    def test_full_path(self):
        self.assertEqual(
            self.resource._base_path, 'http://{}/base'.format(FAKE_BASE_URL))

    def test_name_property(self):
        """Test name property."""
        self.assertEqual('', self.resource.name)
        self.resource.raw_data = {'name': 'Name'}
        self.assertEqual('Name', self.resource.name)
        self.resource.raw_data = {'name': 'Name',
                                  'name_unicode': 'Name Unicode'}
        self.assertEqual('Name Unicode', self.resource.name)

    def test_raw_data_property(self):
        """Test raw_data getter/setter."""
        self.assertEqual(self.get_resource_raw_data(), self.resource.raw_data)
        # Set new raw data
        data = {'name': 'name'}
        self.resource.raw_data = data
        self.assertEqual({'name': 'name'}, self.resource.raw_data)
        # Try to change the original data, resource should have made a copy!
        data['name'] = 'no name'
        self.assertEqual({'name': 'name'}, self.resource.raw_data)

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
