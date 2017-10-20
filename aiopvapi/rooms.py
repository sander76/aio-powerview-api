"""Room class managing all room data."""

import asyncio
import logging

from aiopvapi.helpers.api_base import ApiEntryPoint
from aiopvapi.helpers.constants import ATTR_NAME, ATTR_COLOR_ID, ATTR_ICON_ID, \
    ATTR_NAME_UNICODE, URL_ROOMS, ATTR_ROOM
from aiopvapi.helpers.tools import base64_to_unicode, get_base_path, \
    unicode_to_base64

_LOGGER = logging.getLogger("__name__")

ATTR_ROOM_DATA = 'roomData'


class Rooms(ApiEntryPoint):
    def __init__(self, hub_ip, loop, websession=None):
        super().__init__(loop, websession, get_base_path(hub_ip, URL_ROOMS))

    @staticmethod
    def sanitize_resources(resource):
        """Cleans up incoming room data

        :param rooms: The dict with scene data to be sanitized.
        :return: Cleaned up room dict.
        """
        try:
            for room in resource[ATTR_ROOM_DATA]:
                room[ATTR_NAME_UNICODE] = base64_to_unicode(room[ATTR_NAME])
            return resource
        except (KeyError, TypeError):
            _LOGGER.debug("no roomdata available")
            return None

    @asyncio.coroutine
    def create_room(self, name, color_id=0, icon_id=0):
        name = unicode_to_base64(name)
        data = {
            ATTR_ROOM: {
                ATTR_NAME: name,
                ATTR_COLOR_ID: color_id,
                ATTR_ICON_ID: icon_id
            }
        }
        _result, _status = yield from self.request.post(self._base_path,
                                                        data=data)
        if _status == 201:
            _LOGGER.info("Room successfully created.")
            return _result
        else:
            _LOGGER.error("Error creating room.")
            return None
