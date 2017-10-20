import asyncio

from aiopvapi.helpers.tools import get_base_path
from aiopvapi.helpers.api_base import ApiResource
from aiopvapi.helpers.constants import ATTR_SCENE_MEMBER, \
    ATTR_SCENE_ID, ATTR_SHADE_ID, URL_SCENE_MEMBERS



class SceneMember(ApiResource):
    def __init__(self, raw_data, hub_ip, loop, websession=None):
        if ATTR_SCENE_MEMBER in raw_data:
            raw_data=raw_data.get(ATTR_SCENE_MEMBER)
        super().__init__(loop, websession, raw_data)
        self._base_path = get_base_path(hub_ip, URL_SCENE_MEMBERS)

    # @property
    # def roomId(self):
    #     return self._raw_data.get(SCENE_ROOM_ID)

    # @property
    # def sceneId(self):
    #     return self._

    @asyncio.coroutine
    def delete(self):
        """Deletes a scene from a shade"""
        _val = yield from self.request.delete(
            self._base_path,
            params={ATTR_SCENE_ID: self._raw_data.get(ATTR_SCENE_ID),
                    ATTR_SHADE_ID: self._raw_data.get(ATTR_SHADE_ID)})
        if _val == 200 or _val == 204:
            return True
        return False

