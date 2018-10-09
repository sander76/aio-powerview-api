"""Room class managing all room data."""

import logging

from aiopvapi.helpers.api_base import ApiEntryPoint
from aiopvapi.helpers.constants import ATTR_NAME, ATTR_COLOR_ID, ATTR_ICON_ID, ATTR_ROOM
from aiopvapi.helpers.tools import unicode_to_base64
from aiopvapi.resources.room import Room

_LOGGER = logging.getLogger("__name__")

ATTR_ROOM_DATA = "roomData"


class Rooms(ApiEntryPoint):
    api_path = "api/rooms"

    def __init__(self, request):
        super().__init__(request, self.api_path)

    async def create_room(self, name, color_id=0, icon_id=0):
        name = unicode_to_base64(name)
        data = {
            ATTR_ROOM: {ATTR_NAME: name, ATTR_COLOR_ID: color_id, ATTR_ICON_ID: icon_id}
        }
        return await self.request.post(self._base_path, data=data)

    def _resource_factory(self, raw):
        return Room(raw, self.request)

    @staticmethod
    def _loop_raw(raw):
        for _raw in raw[ATTR_ROOM_DATA]:
            yield _raw

    @staticmethod
    def _get_to_actual_data(raw):
        return raw.get("room")
