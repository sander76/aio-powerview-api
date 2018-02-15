"""Scenes class managing all scene data."""

import logging

from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.helpers.api_base import ApiEntryPoint
from aiopvapi.helpers.constants import ATTR_NAME, ATTR_NAME_UNICODE
from aiopvapi.helpers.tools import base64_to_unicode

LOGGER = logging.getLogger("__name__")

ATTR_SHADE_DATA = 'shadeData'


class Shades(ApiEntryPoint):
    api_path = 'api/shades'

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
                shade[ATTR_NAME_UNICODE] = base64_to_unicode(shade[ATTR_NAME])
            return resource
        except (KeyError, TypeError):
            LOGGER.debug("no shade data available")
            return None
