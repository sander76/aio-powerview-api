"""Room class managing all room data."""

import logging

from aiopvapi.helpers.api_base import ApiEntryPoint
from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.helpers.constants import (
    ATTR_ID,
    ATTR_NAME,
    ATTR_COLOR_ID,
    ATTR_ICON_ID,
    ATTR_ROOM,
    ATTR_ROOM_DATA,
)
from aiopvapi.helpers.tools import unicode_to_base64
from aiopvapi.resources.room import Room

from aiopvapi.resources.model import PowerviewData

_LOGGER = logging.getLogger(__name__)


class Rooms(ApiEntryPoint):
    """Rooms entry point"""

    api_endpoint = "rooms"

    def __init__(self, request: AioRequest) -> None:
        super().__init__(request, self.api_endpoint)

    async def create_room(self, name, color_id=0, icon_id=0):
        """Create a room on the hub"""
        name = unicode_to_base64(name)
        data = {
            ATTR_ROOM: {ATTR_NAME: name, ATTR_COLOR_ID: color_id, ATTR_ICON_ID: icon_id}
        }
        return await self.request.post(self.base_path, data=data)

    def _resource_factory(self, raw):
        return Room(raw, self.request)

    def _loop_raw(self, raw):
        if self.api_version < 3:
            raw = raw[ATTR_ROOM_DATA]

        for _raw in raw:
            yield _raw

    def _get_to_actual_data(self, raw):
        if self.api_version >= 3:
            return raw
        return raw.get("room")

    async def get_rooms(self) -> PowerviewData:
        """Get a list of rooms.

        :returns PowerviewData object
        :raises PvApiError when an error occurs.
        """
        resources = await self.get_resources()
        if self.api_version < 3:
            resources = resources[ATTR_ROOM_DATA]

        processed = {entry[ATTR_ID]: Room(entry, self.request) for entry in resources}

        _LOGGER.debug("Raw room data: %s", resources)
        return PowerviewData(raw=resources, processed=processed)
