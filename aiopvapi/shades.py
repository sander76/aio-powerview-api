"""Scenes class managing all scene data."""

import logging

from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.helpers.api_base import ApiEntryPoint
from aiopvapi.helpers.constants import (
    ATTR_ID,
    ATTR_NAME,
    ATTR_NAME_UNICODE,
    ATTR_SHADE_DATA,
)
from aiopvapi.helpers.tools import base64_to_unicode
from aiopvapi.resources import shade

from aiopvapi.resources.model import PowerviewData


_LOGGER = logging.getLogger(__name__)


class Shades(ApiEntryPoint):
    """Shades entry point"""

    api_endpoint = "shades"

    def __init__(self, request: AioRequest) -> None:
        super().__init__(request, self.api_endpoint)

    def _sanitize_resources(self, resources: dict) -> dict | None:
        """Cleans up incoming shade data

        :param resources: The dict with shade data to be sanitized.
        :returns: Cleaned up shade dict.
        """
        if self.api_version < 3:
            resources = resources[ATTR_SHADE_DATA]

        try:
            for _shade in resources:
                _name = _shade.get(ATTR_NAME)
                if _name:
                    _shade[ATTR_NAME_UNICODE] = base64_to_unicode(_name)
            return resources
        except (KeyError, TypeError):
            _LOGGER.debug("No shade data available")
            return None

    def _resource_factory(self, raw):
        return shade.factory(raw, self.request)

    def _loop_raw(self, raw):
        if self.api_version < 3:
            raw = raw[ATTR_SHADE_DATA]

        for _raw in raw:
            yield _raw

    def _get_to_actual_data(self, raw):
        if self.api_version >= 3:
            return raw
        return raw.get("shade")

    async def get_shades(self) -> PowerviewData:
        """Get a list of shades.

        :returns PowerviewData object
        :raises PvApiError when an error occurs.
        """
        resources = await self.get_resources()
        if self.api_version < 3:
            resources = resources[ATTR_SHADE_DATA]

        _LOGGER.debug("Raw shades data: %s", resources)

        processed = {
            entry[ATTR_ID]: shade.factory(entry, self.request) for entry in resources
        }

        _LOGGER.debug("Raw shades data: %s", resources)
        return PowerviewData(raw=resources, processed=processed)

        # async def get_shade(self, shade_id: int):

    #     _url = '{}/{}'.format(self.api_path, shade_id)
    #     _raw = await self.request.get(_url)
    #     return shade.factory(_raw, self.request)
