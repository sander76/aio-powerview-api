"""Scenes class managing all scene data."""

import logging

from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.helpers.api_base import ApiEntryPoint
from aiopvapi.helpers.tools import base64_to_unicode

LOGGER = logging.getLogger("__name__")

ATTR_HUB_NAME = "hubName"
ATTR_HUB_NAME_UNICODE = "hubNameUnicode"


class UserData(ApiEntryPoint):
    api_path = "api/userdata"

    def __init__(self, request: AioRequest):
        super().__init__(request, self.api_path)

    @staticmethod
    def sanitize_resources(resource):
        """Cleans up incoming scene data

        :param resource: The dict with scene data to be sanitized.
        :returns: Cleaned up dict.
        """
        try:
            resource[ATTR_HUB_NAME_UNICODE] = base64_to_unicode(resource[ATTR_HUB_NAME])
            return resource
        except (KeyError, TypeError):
            LOGGER.debug("no data available")
            return None
