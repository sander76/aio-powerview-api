"""Scenes class managing all scene data."""

import logging

from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.helpers.api_base import ApiEntryPoint
from aiopvapi.helpers.constants import ATTR_NAME, ATTR_NAME_UNICODE
from aiopvapi.helpers.tools import base64_to_unicode
from aiopvapi.resources import shade

LOGGER = logging.getLogger("__name__")

ATTR_SHADE_DATA = "shadeData"


class Shades(ApiEntryPoint):
    """Shades entry point"""

    api_path = "api/shades"

    def __init__(self, request: AioRequest):
        super().__init__(request, self.api_path)

    @staticmethod
    def sanitize_resources(resource: dict):
        """Cleans up incoming scene data

        :param resource: The dict with scene data to be sanitized.
        :returns: Cleaned up scene dict.
        """
        try:
            for shade in resource[ATTR_SHADE_DATA]:
                _name = shade.get(ATTR_NAME)
                if _name:
                    shade[ATTR_NAME_UNICODE] = base64_to_unicode(_name)
            return resource
        except (KeyError, TypeError):
            LOGGER.debug("no shade data available")
            return None

    def _resource_factory(self, raw):
        return shade.factory(raw, self.request)

    @staticmethod
    def _loop_raw(raw):
        for _raw in raw[ATTR_SHADE_DATA]:
            yield _raw

    @staticmethod
    def _get_to_actual_data(raw):
        return raw.get("shade")

    # async def get_shade(self, shade_id: int):
    #     _url = '{}/{}'.format(self.api_path, shade_id)
    #     _raw = await self.request.get(_url)
    #     return shade.factory(_raw, self.request)
