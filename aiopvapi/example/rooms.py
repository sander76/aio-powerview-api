from aiopvapi.helpers.aiorequest import AioRequest, PvApiError
from aiopvapi.rooms import Rooms


class ExampleRooms:
    def __init__(self, hub_ip):
        self.request = AioRequest(hub_ip)
        self.raw_rooms = []
        self.rooms = []
        self._shades_entry_point = Rooms(self.request)

    async def get_raw_rooms(self):
        try:
            self.raw_rooms = await self._shades_entry_point.get_resources()
        except PvApiError:
            raise

    async def get_rooms(self):
        self.rooms = await self._shades_entry_point.get_instances()

    async def get_room(self, room_id):
        room = await self._shades_entry_point.get_instance(room_id)
        return room
