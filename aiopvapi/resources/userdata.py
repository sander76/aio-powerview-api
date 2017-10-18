import asyncio

from aiopvapi.helpers.constants import ATTR_USER_DATA
from aiopvapi.helpers.tools import get_base_path
from aiopvapi.helpers.api_base import ApiResource


class UserData(ApiResource):
    def __init__(self, raw_data, hub_ip, loop, websession=None):
        if ATTR_USER_DATA in raw_data:
            raw_data = raw_data.get(ATTR_USER_DATA)
        super().__init__(loop, websession, get_base_path(hub_ip, 'api/userdata'),
                         raw_data)
