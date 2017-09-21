import asyncio

from aiopvapi.helpers.tools import get_base_path
from aiopvapi.helpers.api_base import ApiResource
ATTR_USER_DATA = 'user'

class UserData(ApiResource):
    def __init__(self, raw_data, hub_ip, loop, websession=None):
        if ATTR_USER_DATA in raw_data:
            raw_data = raw_data.get(ATTR_USER_DATA)
        ApiResource.__init__(self, loop, websession, raw_data)
        self._base_path = get_base_path(hub_ip, 'api/userdata')
