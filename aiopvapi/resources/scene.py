import asyncio

from aiopvapi.helpers.tools import get_base_path
from aiopvapi.helpers.api_base import ApiResource
from aiopvapi.helpers.constants import ATTR_ICON_ID, ATTR_COLOR_ID, \
    ATTR_SCENE_ID, URL_SCENES, URL_SHADES

SCENE_NAME = 'name'
SCENE_ROOM_ID = 'roomId'
SCENE_ORDER = 'order'
ATTR_SCENE = 'scene'


class Scene(ApiResource):
    def __init__(self, raw_data, hub_ip=None, loop=None, websession=None):
        if ATTR_SCENE in raw_data:
            raw_data = raw_data.get(ATTR_SCENE)
        ApiResource.__init__(
            self, loop, websession, get_base_path(hub_ip, URL_SCENES),
            raw_data)

    @property
    def roomId(self):
        return self._raw_data.get(SCENE_ROOM_ID)

    @asyncio.coroutine
    def activate(self):
        _val = yield from self.request.get(self._base_path,
                                           params={ATTR_SCENE_ID: self._id})
        return _val

    @asyncio.coroutine
    def delete(self):
        """Deletes a scene from a shade"""
        _val = yield from self.request.delete(
            self._resource_path)
        if _val == 200 or _val == 204:
            return True
        return False
