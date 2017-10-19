import asyncio

import aiohttp
import logging

from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.helpers.constants import ATTR_ID, ATTR_NAME_UNICODE, ATTR_NAME
from aiopvapi.helpers.tools import join_path

_LOGGER = logging.getLogger(__name__)


class ApiBase:
    def __init__(self, loop, websession, base_path):
        if websession is None:
            _LOGGER.debug("No session defined. Creating a new one")
            websession = aiohttp.ClientSession(loop=loop)
        self.request = AioRequest(loop, websession)
        self._base_path = base_path


class ApiEntryPoint(ApiBase):
    def __init__(self, loop, websession, base_path):
        ApiBase.__init__(self, loop, websession, base_path)
        # self._base_path = base_path

    @staticmethod
    def sanitize_resources(resource):
        raise NotImplemented

    @asyncio.coroutine
    def get_resources(self):
        """Get a list of resources. """
        resources = yield from self.request.get(self._base_path)

        return self.sanitize_resources(resources)


class ApiResource(ApiBase):
    def __init__(self, loop, websession, base_path, raw_data=None):
        ApiBase.__init__(self, loop, websession,base_path)
        self._id = raw_data.get(ATTR_ID)
        self._raw_data = raw_data
        self._resource_path = join_path(base_path, str(self._id))

    @asyncio.coroutine
    def delete(self):
        """Deletes a scene from a shade"""
        _val = yield from self.request.delete(
            self._resource_path)
        if _val == 200 or _val == 204:
            return True
        return False

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        _name = self._raw_data.get(ATTR_NAME_UNICODE)
        if _name:
            return _name
        _name = self._raw_data.get(ATTR_NAME)
        if _name:
            return _name
        return ''

    @property
    def raw_data(self):
        return self._raw_data

    @raw_data.setter
    def raw_data(self, data):
        self._raw_data = data
