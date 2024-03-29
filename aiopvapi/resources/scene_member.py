"""Class for managing scene members."""

from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.helpers.api_base import ApiResource
from aiopvapi.helpers.constants import (
    ATTR_SCENE_MEMBER,
    ATTR_SCENE_ID,
    ATTR_SHADE_ID,
)


class SceneMember(ApiResource):
    """Shades belonging to a scene."""

    api_endpoint = "scenemembers"

    def __init__(self, raw_data: dict, request: AioRequest) -> None:
        if ATTR_SCENE_MEMBER in raw_data:
            raw_data = raw_data.get(ATTR_SCENE_MEMBER)
        super().__init__(request, self.api_endpoint, raw_data)

    @property
    def scene_id(self) -> str:
        """Return scene id of the scene"""
        return self._raw_data.get(ATTR_SCENE_ID)

    @property
    def shade_id(self) -> str:
        """Return shade id of scene members"""
        return self._raw_data.get(ATTR_SHADE_ID)

    async def delete(self):
        """Deletes a scene from a shade"""
        _val = await self.request.delete(
            self.base_path,
            params={
                ATTR_SCENE_ID: self._raw_data.get(ATTR_SCENE_ID),
                ATTR_SHADE_ID: self._raw_data.get(ATTR_SHADE_ID),
            },
        )
        return _val
