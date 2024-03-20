"""Class containing the api base."""

import logging

from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.helpers.constants import (
    ATTR_ID,
    ATTR_NAME_UNICODE,
    ATTR_NAME,
    ATTR_PTNAME,
)
from aiopvapi.helpers.tools import (
    join_path,
    get_base_path,
    base64_to_unicode,
)

_LOGGER = logging.getLogger(__name__)


class ApiBase:
    """Api base class."""

    api_endpoint = ""

    def __init__(self, request: AioRequest, api_endpoint: str = "") -> None:
        self.request = request
        self._api_endpoint = api_endpoint
        self._raw_data = None

    @property
    def api_version(self) -> int:
        """Return the API version of the connected hub."""
        return self.request.api_version

    @property
    def api_path(self) -> str:
        """Returns the initial api call path based on the api version."""
        return self.request.api_path

    @property
    def base_path(self) -> str:
        """Returns the base path of the resource."""
        return get_base_path(
            self.request.hub_ip, join_path(self.api_path, self._api_endpoint)
        )

    @property
    def url(self) -> str:
        """Returns the url of the hub."""
        return self.base_path

    def _parse(self, *keys, converter=None, data=None):
        """Retrieve attributes from data dictionary."""
        val = data if data else self._raw_data
        try:
            for key in keys:
                val = val[key]
        except KeyError as err:
            _LOGGER.debug("Key '%s' missing", err)
            return None
        if converter:
            try:
                return converter(val)
            except UnicodeDecodeError as err:
                _LOGGER.error("UnicodeDecodeError converting '%s', err=%s", val, err)
                return None
        return val


class ApiResource(ApiBase):
    """Represent a single PowerView resource such as scene, shade or room."""

    def __init__(self, request, api_endpoint, raw_data=None) -> None:
        super().__init__(request, api_endpoint)
        self._id = "unknown" if raw_data is None else raw_data.get(ATTR_ID)
        self._raw_data = raw_data
        self._resource_path = join_path(self.base_path, str(self._id))
        _LOGGER.debug("Initializing resource path: %s", self._resource_path)

    async def delete(self):
        """Delete a resource."""
        return await self.request.delete(self._resource_path)

    @property
    def id(self):
        """The resource id."""
        return self._id

    @property
    def name(self):
        """Name of the resource.

        If conversion to unicode somehow
        didn't go well value is returned in base64 encoding.
        """
        return (
            self._raw_data.get(ATTR_PTNAME)
            or self._raw_data.get(ATTR_NAME_UNICODE)
            or self._parse(ATTR_NAME, converter=base64_to_unicode, data=self._raw_data)
            or self._raw_data.get(ATTR_NAME)
            or ""
        )
        # resource[ATTR_NAME_UNICODE] = base64_to_unicode(_name)

    @property
    def url(self) -> str:
        """Return url for the shade."""
        return self._resource_path

    @property
    def raw_data(self):
        """Raw data like received from the hub."""
        return self._raw_data

    @raw_data.setter
    def raw_data(self, data):
        self._raw_data = dict(data)


class ApiEntryPoint(ApiBase):
    """API entrypoint."""

    def __init__(self, request, api_endpoint, use_initial=True) -> None:
        super().__init__(request, api_endpoint)
        if use_initial:
            api_endpoint = join_path(self.api_path, api_endpoint)

    def _sanitize_resources(self, resources: dict):
        """Loop over incoming data looking for base64 encoded data.

        Convert found data to a readable format.
        """

        try:
            for resource in self._loop_raw(resources):
                self._sanitize_resource(resource)
        except (KeyError, TypeError):
            _LOGGER.warning("No shade data available")
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
        # resources = await self.request.get(self._base_path, **kwargs)
        # _LOGGER.warning("%s kwargs %s", self.base_path, kwargs)
        resources = await self.request.get(self.base_path, **kwargs)
        self._sanitize_resources(resources)
        return resources

    async def get_resource(self, resource_id: int) -> dict:
        """Get a single resource.

        :raises PvApiError when a hub connection occurs.
        """
        resource = await self.request.get(join_path(self.base_path, str(resource_id)))
        # resource = await self.request.get(join_path(self._base_path, str(resource_id)))
        self._sanitize_resource(self._get_to_actual_data(resource))
        return resource

    async def get_instances(self, **kwargs) -> list[ApiResource]:
        """Return a list of resource instances.

        :raises PvApiError when a hub problem occurs.
        """
        raw_resources = await self.get_resources(**kwargs)
        _instances = [
            self._resource_factory(_raw) for _raw in self._loop_raw(raw_resources)
        ]
        return _instances

    async def get_instance(self, resource_id) -> ApiResource:
        """Get a single instance of a pv resource.

        :raises PvApiError when a hub problem occurs.
        """
        raw = await self.get_resource(resource_id)
        return self._resource_factory(self._get_to_actual_data(raw))

    def _resource_factory(self, raw) -> ApiResource:
        """Convert raw data to a instantiated resource."""
        raise NotImplementedError

    def _loop_raw(self, raw):
        """Loop over raw data."""
        raise NotImplementedError

    def _get_to_actual_data(self, raw):
        """Incoming data is wrapped inside a key value pair.

        For real unknown reasons making this a necessary call.
        """
        raise NotImplementedError
