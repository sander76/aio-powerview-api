"""
{ "id": 46688, "order": 0, "iconId": 0, "name": "Living room", "colorId": 7 }
"""

import asyncio

from aiopvapi.helpers.tools import get_base_path
from aiopvapi.helpers.api_base import ApiResource
from aiopvapi.helpers.constants import ATTR_ICON_ID, ATTR_COLOR_ID

ROOM_NAME = 'name'
ROOM_ID = 'id'
ROOM_ORDER = 'order'
ATTR_ROOM = 'room'


class Room(ApiResource):
    def __init__(self, raw_data, hub_ip=None, loop=None, websession=None):
        if ATTR_ROOM in raw_data:
            raw_data = raw_data.get(ATTR_ROOM)
        ApiResource.__init__(self, loop, websession,
                             get_base_path(hub_ip, 'api/rooms'), raw_data)


