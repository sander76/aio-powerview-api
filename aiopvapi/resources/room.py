"""Powerview Room type."""

from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.helpers.api_base import ApiResource
from aiopvapi.helpers.constants import ATTR_ROOM


class Room(ApiResource):
    """Powerview Rooms."""

    api_endpoint = "rooms"

    def __init__(self, raw_data: dict, request: AioRequest) -> None:
        """Initialize the rooms."""
        if ATTR_ROOM in raw_data:
            raw_data = raw_data.get(ATTR_ROOM)
        super().__init__(request, self.api_endpoint, raw_data)
