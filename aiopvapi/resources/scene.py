from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.helpers.api_base import ApiResource
from aiopvapi.helpers.constants import ATTR_SCENE, ATTR_ROOM_ID, ATTR_SCENE_ID


class Scene(ApiResource):
    api_path = "api/scenes"

    def __init__(self, raw_data: dict, request: AioRequest):
        if ATTR_SCENE in raw_data:
            raw_data = raw_data.get(ATTR_SCENE)
        super().__init__(request, self.api_path, raw_data)

    @property
    def room_id(self):
        """Return the room id."""
        return self._raw_data.get(ATTR_ROOM_ID)

    async def activate(self):
        """Activate this scene."""
        _val = await self.request.get(self._base_path, params={ATTR_SCENE_ID: self._id})
        return _val
