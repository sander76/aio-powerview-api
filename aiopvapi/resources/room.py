"""
{ "id": 46688, "order": 0, "iconId": 0, "name": "Living room", "colorId": 7 }
"""

from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.helpers.api_base import ApiResource
from aiopvapi.helpers.constants import ATTR_ROOM


class Room(ApiResource):
    api_path = "api/rooms"

    def __init__(self, raw_data: dict, request: AioRequest):
        if ATTR_ROOM in raw_data:
            raw_data = raw_data.get(ATTR_ROOM)
        super().__init__(request, self.api_path, raw_data)
