"""Scenes class managing all scene data."""

import logging

from aiopvapi.helpers.api_base import ApiEntryPoint
from aiopvapi.helpers.constants import ATTR_NAME, URL_SHADES, ATTR_NAME_UNICODE
from aiopvapi.helpers.tools import base64_to_unicode, get_base_path

LOGGER = logging.getLogger("__name__")

ATTR_SHADE_DATA = 'shadeData'


class Shades(ApiEntryPoint):
    def __init__(self, hub_ip, loop, websession=None):
        ApiEntryPoint.__init__(self, loop, websession,
                               get_base_path(hub_ip, URL_SHADES))

    @staticmethod
    def sanitize_resources(resource: dict):
        """Cleans up incoming scene data

        :param scenes: The dict with scene data to be sanitized.
        :returns: Cleaned up scene dict.
        """
        try:
            for shade in resource[ATTR_SHADE_DATA]:
                shade[ATTR_NAME_UNICODE] = base64_to_unicode(shade[ATTR_NAME])
            return resource
        except (KeyError, TypeError):
            LOGGER.debug("no shade data available")
            return None
