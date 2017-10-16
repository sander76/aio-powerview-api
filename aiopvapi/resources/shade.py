import asyncio
import logging

from aiopvapi.helpers.api_base import ApiResource
from aiopvapi.helpers.constants import URL_SHADES, ATTR_POSITION_DATA, \
    ATTR_SHADE, ATTR_TYPE, ATTR_ID, ATTR_ROOM_ID, URL_SCENES
from aiopvapi.helpers.position import Position
from aiopvapi.helpers.tools import get_base_path, join_path

_LOGGER = logging.getLogger(__name__)

BOTTOM_UP_TILT = None
ATTR_SHADE = 'shade'


class Shade(ApiResource):
    def __init__(self, raw_data, hub_ip=None, loop=None, websession=None):
        if ATTR_SHADE in raw_data:
            raw_data = raw_data.get(ATTR_SHADE)
        ApiResource.__init__(self, loop, websession,
                             get_base_path(hub_ip, URL_SHADES), raw_data)
        self._shade_position = Position(raw_data.get(ATTR_TYPE))

    async def refresh(self):
        """Get raw data from the hub and update the shade instance"""
        _raw_data = await self.request.get(self._resource_path,
                                                {'refresh': 'true'})
        self._update(_raw_data)

    def _update(self, raw_data):
        """Update the current shade instance with the latest raw data"""
        if raw_data:
            self._raw_data = raw_data
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

    async def move_to(self, position1=None, position2=None):
        """Moves the shade to a specific position.

        Next to move to there are method for move_tilt_to and
        tilt_to
        """
        data = self._create_shade_data(self._shade_position.get_move_data(
            position1, position2))
        _result = await self._move(data)
        return _result

    def get_move_data(self, position1, position2):
        """Return a dict with move data."""
        return self._shade_position.get_move_data(position1, position2)

    async def _move(self, position_data):
        _result, status = await self.request.put(
            self._resource_path, data=position_data)
        _LOGGER.debug("move shade returned status code %s" % status)
        if status == 200 or status == 201:
            return _result
        else:
            return None

    async def close(self):
        data = self._create_shade_data(
            positiondata=self._shade_position.close_data)
        _result = await self._move(data)
        return _result

    async def open(self):
        data = self._create_shade_data(
            positiondata=self._shade_position.open_data)
        _result = await self._move(data)
        return _result

    async def add_shade_to_room(self, room_id):
        data = self._create_shade_data(room_id=room_id)
        _result, _status = await self.request.put(self._resource_path,
                                                       data)
        if _status == 200:
            _LOGGER.info("Shade successfully added to room.")
        else:
            _LOGGER.error("Problem adding shade to room.")
        return _result
