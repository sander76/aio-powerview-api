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
        super().__init__(loop, websession, base_path)

    @staticmethod
    def sanitize_resources(resource):
        raise NotImplemented

    @asyncio.coroutine
    def get_resources(self):
        """Get a list of resources. """
        resources = yield from self.request.get(self._base_path)
        return self.sanitize_resources(resources)


class ApiResource(ApiBase):
    """Represent a single PowerView resource, i.e. a scene, a shade or a room."""
    def __init__(self, loop, websession, base_path, raw_data=None):
        super().__init__(loop, websession, base_path)
        self._id = raw_data.get(ATTR_ID)
        self._raw_data = raw_data
        self._resource_path = join_path(base_path, str(self._id))

    @asyncio.coroutine
    def delete(self):
        """Deletes a resource."""
        _val = yield from self.request.delete(self._resource_path)
        return _val in [200, 204]

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._raw_data.get(ATTR_NAME_UNICODE) or \
               self._raw_data.get(ATTR_NAME) or ''

    @property
    def raw_data(self):
        return self._raw_data

    @raw_data.setter
    def raw_data(self, data):
        self._raw_data = data
