"""Scenes class managing all scene data."""

import logging

from aiopvapi.helpers.api_base import ApiEntryPoint
from aiopvapi.helpers.tools import base64_to_unicode, get_base_path

LOGGER = logging.getLogger("__name__")

ATTR_HUB_NAME = 'hubName'
ATTR_HUB_NAME_UNICODE = 'hubNameUnicode'


class UserData(ApiEntryPoint):
    def __init__(self, hub_ip, loop, websession=None):
        super().__init__(loop, websession,get_base_path(hub_ip, 'api/userdata'))

    @staticmethod
    def sanitize_resources(resource):
        """Cleans up incoming scene data

        :param scenes: The dict with scene data to be sanitized.
        :returns: Cleaned up dict.
        """
        try:
            resource[ATTR_HUB_NAME_UNICODE] = base64_to_unicode(resource[ATTR_HUB_NAME])
            return resource
        except (KeyError, TypeError):
            LOGGER.debug("no data available")
            return None


    # @asyncio.coroutine
    # def get_resources(self):
    #     """Get userdata.
    #
    #     :returns:
    #
    #     """
    #     resource = yield from self.request.get(self._base_path)
    #
    #     return UserData.sanitize(resource)
