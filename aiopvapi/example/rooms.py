"""Room example."""

from aiopvapi.helpers.aiorequest import AioRequest, PvApiError
from aiopvapi.rooms import Rooms


class ExampleRooms:  # noqa: D101
    def __init__(self, hub_ip) -> None:  # noqa: D107
        self.request = AioRequest(hub_ip)
        self.raw_rooms = []
        self.rooms = []
        self._shades_entry_point = Rooms(self.request)

    async def get_raw_rooms(self):  # noqa: D102
        try:
            self.raw_rooms = await self._shades_entry_point.get_resources()
        except PvApiError:  # noqa: TRY302
            raise

    async def get_rooms(self):  # noqa: D102
        self.rooms = await self._shades_entry_point.get_instances()

    async def get_room(self, room_id):  # noqa: D102
        return await self._shades_entry_point.get_instance(room_id)
