"""Hub class acting as the base for the PowerView API."""

from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.helpers.api_base import ApiBase
from aiopvapi.helpers.tools import get_base_path


class Hub(ApiBase):
    def __init__(self, hub_ip,loop, websession=None):
        ApiBase.__init__(self,loop,websession)
        self.ip_address = hub_ip
        self.request = AioRequest(loop, websession)
        self._base_path = get_base_path(hub_ip,'api')