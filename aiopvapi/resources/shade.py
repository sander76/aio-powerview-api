import asyncio
import json
import logging

from aiopvapi.helpers.api_base import ApiResource
from aiopvapi.helpers.constants import URL_SHADES, ATTR_POSITION_DATA, \
    ATTR_SHADE, ATTR_TYPE, ATTR_ID, ATTR_ROOM_ID
from aiopvapi.helpers.position import Position
from aiopvapi.helpers.tools import get_base_path

_LOGGER = logging.getLogger(__name__)

BOTTOM_UP_TILT = None


class Shade(ApiResource):
    def __init__(self, raw_data, hub_ip=None, loop=None, websession=None):
        if ATTR_SHADE in raw_data:
            raw_data = raw_data.get(ATTR_SHADE)
        super().__init__(loop, websession, get_base_path(hub_ip, URL_SHADES),
                         raw_data)
        self._shade_position = Position(raw_data.get(ATTR_TYPE))

    @asyncio.coroutine
    def refresh(self):
        """Get raw data from the hub and update the shade instance"""
        raw_data = yield from self.request.get(self._resource_path,
                                               {'refresh': 'true'})
        if raw_data:
            self._raw_data = raw_data[ATTR_SHADE]
            if ATTR_POSITION_DATA in raw_data[ATTR_SHADE]:
                self._shade_position.refresh(
                    raw_data[ATTR_SHADE][ATTR_POSITION_DATA])

    def _create_shade_data(self, positiondata=None, room_id=None):
        """Create a shade data object to be sent to the hub"""
        base = {ATTR_SHADE: {ATTR_ID: self.id}}
        if positiondata:
            base[ATTR_SHADE][ATTR_POSITION_DATA] = positiondata
        if room_id:
            base[ATTR_SHADE][ATTR_ROOM_ID] = room_id
        return base

    @asyncio.coroutine
    def move_to(self, position1=None, position2=None):
        """Moves the shade to a specific position.

        Next to move to there are method for move_tilt_to and
        tilt_to
        """
        data = self._create_shade_data(self._shade_position.get_move_data(
            position1, position2))
        return (yield from self._move(data))

    def get_move_data(self, position1, position2):
        """Return a dict with move data."""
        return self._shade_position.get_move_data(position1, position2)

    @asyncio.coroutine
    def _move(self, position_data):
        result = yield from self.request.put(self._resource_path,
                                             data=position_data)

    @asyncio.coroutine
    def close(self):
        data = self._create_shade_data(
            positiondata=self._shade_position.close_data)
        return (yield from self._move(data))

    @asyncio.coroutine
    def open(self):
        data = self._create_shade_data(
            positiondata=self._shade_position.open_data)
        return (yield from self._move(data))

    @asyncio.coroutine
    def jog(self):
        yield from self.request.put(self._resource_path,
                                    {"shade": {"motion": "jog"}})

    @asyncio.coroutine
    def add_shade_to_room(self, room_id):
        data = self._create_shade_data(room_id=room_id)
        return (yield from self.request.put(self._resource_path, data))
