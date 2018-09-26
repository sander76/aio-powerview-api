from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.helpers.api_base import ApiResource
from aiopvapi.helpers.constants import ATTR_USER_DATA


class UserData(ApiResource):
    api_path = "api/userdata"

    def __init__(self, raw_data: dict, request: AioRequest):
        if ATTR_USER_DATA in raw_data:
            raw_data = raw_data.get(ATTR_USER_DATA)
        super().__init__(request, self.api_path, raw_data)
