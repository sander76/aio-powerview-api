import logging

from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.helpers.api_base import ApiResource
from aiopvapi.helpers.constants import ATTR_POSITION_DATA, \
    ATTR_SHADE, ATTR_TYPE, ATTR_ID, ATTR_ROOM_ID
from aiopvapi.helpers.position import Position

_LOGGER = logging.getLogger(__name__)

BOTTOM_UP_TILT = None


class Shade(ApiResource):
    api_path = 'api/shades'

    def __init__(self, raw_data: dict, request: AioRequest):
        if ATTR_SHADE in raw_data:
            raw_data = raw_data.get(ATTR_SHADE)
        super().__init__(request, self.api_path,
                         raw_data)
        self._shade_position = Position(raw_data.get(ATTR_TYPE))

    async def refresh(self):
        """Get raw data from the hub and update the shade instance"""
        raw_data = await self.request.get(self._resource_path,
                                          {'refresh': 'true'})
        if raw_data:
            self._raw_data = raw_data[ATTR_SHADE]
            if ATTR_POSITION_DATA in raw_data[ATTR_SHADE]:
                self._shade_position.refresh(
                    raw_data[ATTR_SHADE][ATTR_POSITION_DATA])

    def _create_shade_data(self, position_data=None, room_id=None):
        """Create a shade data object to be sent to the hub"""
        base = {ATTR_SHADE: {ATTR_ID: self.id}}
        if position_data:
            base[ATTR_SHADE][ATTR_POSITION_DATA] = position_data
        if room_id:
            base[ATTR_SHADE][ATTR_ROOM_ID] = room_id
        return base

    async def move_to(self, position1=None, position2=None):
        """Moves the shade to a specific position.

        Next to move to there are method for move_tilt_to and
        tilt_to
        """
        data = self._create_shade_data(self._shade_position.get_move_data(
            position1, position2))
        return await self._move(data)

    def get_move_data(self, position1, position2):
        """Return a dict with move data."""
        return self._shade_position.get_move_data(position1, position2)

    async def _move(self, position_data):
        result = await self.request.put(self._resource_path,
                                        data=position_data)
        return result

    async def close(self):
        data = self._create_shade_data(
            position_data=self._shade_position.close_data)
        return await self._move(data)

    async def open(self):
        data = self._create_shade_data(
            position_data=self._shade_position.open_data)
        return await self._move(data)

    async def jog(self):
        await self.request.put(self._resource_path,
                               {"shade": {"motion": "jog"}})

    async def add_shade_to_room(self, room_id):
        data = self._create_shade_data(room_id=room_id)
        return await self.request.put(self._resource_path, data)
