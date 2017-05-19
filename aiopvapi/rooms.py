import logging

from aiopvapi import decode_base64

LOGGER = logging.getLogger("__name__")

class Rooms:
    def __init__(self, base_api_ip, aio_request):
        self.request = aio_request
        self._rooms_path = "{}/rooms".format(base_api_ip)

    @staticmethod
    def sanitize_rooms(rooms):
        """Cleans up incoming room data

        :param rooms: The dict with scene data to be sanitized.
        :return: Cleaned up room dict.
        """
        try:
            for room in rooms["roomData"]:
                room["name"] = decode_base64(room["name"])
            return rooms
        except (KeyError,TypeError):
            LOGGER.debug("no roomdata available")
            return None

    def get_rooms(self):
        """Get alist of rooms.

        :returns: A json object.
        """
        rooms = yield from self.request.get(self._rooms_path)
        return Rooms.sanitize_rooms(rooms)
