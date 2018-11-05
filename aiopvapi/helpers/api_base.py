import logging
from typing import List

from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.helpers.constants import ATTR_ID, ATTR_NAME_UNICODE, ATTR_NAME
from aiopvapi.helpers.tools import join_path, get_base_path, base64_to_unicode

_LOGGER = logging.getLogger(__name__)


class ApiBase:
    """Api base class"""

    def __init__(self, request: AioRequest, base_path):
        self.request = request
        self._base_path = get_base_path(request.hub_ip, base_path)


class ApiResource(ApiBase):
    """Represent a single PowerView resource,
    i.e. a scene, a shade or a room."""

    def __init__(self, request, api_endpoint, raw_data=None):
        super().__init__(request, api_endpoint)
        self._id = "unknown"
        if raw_data:
            self._id = raw_data.get(ATTR_ID)
        self._raw_data = raw_data

        self._resource_path = join_path(self._base_path, str(self._id))
        _LOGGER.debug(
            "Initializing resource. resource path %s", self._resource_path
        )

    async def delete(self):
        """Deletes a resource."""
        return await self.request.delete(self._resource_path)

    @property
    def id(self):
        """The resource id."""
        return self._id

    @property
    def name(self):
        """Name of the resource. If conversion to unicode somehow
        didn't go well value is returned in base64 encoding."""
        return (
            self._raw_data.get(ATTR_NAME_UNICODE)
            or self._raw_data.get(ATTR_NAME)
            or ""
        )

    @property
    def raw_data(self):
        """Raw data like received from the hub."""
        return self._raw_data

    @raw_data.setter
    def raw_data(self, data):
        self._raw_data = dict(data)


class ApiEntryPoint(ApiBase):
    """API entrypoint."""

    @classmethod
    def _sanitize_resources(cls, resources):
        """Loops over incoming data looking for base64 encoded data and
        converts them to a readable format."""

        try:
            for resource in cls._loop_raw(resources):
                cls._sanitize_resource(resource)
        except (KeyError, TypeError):
            _LOGGER.debug("no shade data available")
            return None

    @classmethod
    def _sanitize_resource(cls, resource):

        _name = resource.get(ATTR_NAME)
        if _name:
            resource[ATTR_NAME_UNICODE] = base64_to_unicode(_name)

    async def get_resources(self, **kwargs) -> dict:
        """Get a list of resources.

        :raises PvApiError when an error occurs.
        """
        resources = await self.request.get(self._base_path, **kwargs)
        self._sanitize_resources(resources)
        return resources

    async def get_resource(self, resource_id: int) -> dict:
        """Get a single resource.

        :raises PvApiError when a hub connection occurs."""
        resource = await self.request.get(
            join_path(self._base_path, str(resource_id))
        )
        self._sanitize_resource(self._get_to_actual_data(resource))
        return resource

    async def get_instances(self, **kwargs) -> List[ApiResource]:
        """Returns a list of resource instances.

        :raises PvApiError when a hub problem occurs."""
        raw_resources = await self.get_resources(**kwargs)
        _instances = [
            self._resource_factory(_raw)
            for _raw in self._loop_raw(raw_resources)
        ]
        return _instances

    async def get_instance(self, resource_id) -> ApiResource:
        """Gets a single instance of a pv resource

        :raises PvApiError when a hub problem occurs."""
        raw = await self.get_resource(resource_id)
        return self._resource_factory(self._get_to_actual_data(raw))

    def _resource_factory(self, raw) -> ApiResource:
        """Converts raw data to a instantiated resource"""
        raise NotImplemented

    @staticmethod
    def _loop_raw(raw):
        """Loops over raw data"""
        raise NotImplemented

    @staticmethod
    def _get_to_actual_data(raw):
        """incoming data is wrapped inside a key value pair for real unknown
        reasons making this a necessary call."""
        raise NotImplemented
