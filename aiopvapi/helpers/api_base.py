import logging
from typing import List

from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.helpers.constants import ATTR_ID, ATTR_NAME_UNICODE, ATTR_NAME
from aiopvapi.helpers.tools import join_path, get_base_path

_LOGGER = logging.getLogger(__name__)


class ApiBase:
    def __init__(self, request: AioRequest, base_path):
        self.request = request
        self._base_path = get_base_path(request.hub_ip, base_path)


class ApiResource(ApiBase):
    """Represent a single PowerView resource,
    i.e. a scene, a shade or a room."""

    def __init__(self, request, api_endpoint, raw_data=None):
        super().__init__(request, api_endpoint)
        if raw_data:
            self._id = raw_data.get(ATTR_ID)
        self._raw_data = raw_data
        self._resource_path = join_path(self._base_path, str(self._id))

    async def delete(self):
        """Deletes a resource."""
        return await self.request.delete(self._resource_path)

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
        self._raw_data = dict(data)


class ApiEntryPoint(ApiBase):
    @staticmethod
    def sanitize_resources(resource):
        raise NotImplemented

    async def get_resources(self) -> dict:
        """Get a list of resources.

        :raises PvApiError when an error occurs.
        """
        resources = await self.request.get(self._base_path)
        return self.sanitize_resources(resources)

    async def get_instances(self) -> List[ApiResource]:
        """Returns a list of resource instances."""
        raw = await self.get_resources()
        return self._factory(raw)

    def _factory(self, raw):
        """Converts raw incoming data to a list of resource instances"""
        raise NotImplemented
