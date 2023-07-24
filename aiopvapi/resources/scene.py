"""Scene class managing all scenes."""

from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.helpers.api_base import ApiResource
from aiopvapi.helpers.tools import join_path
from aiopvapi.helpers.constants import (
    ATTR_SCENE,
    ATTR_ROOM_ID,
    ATTR_ROOM_IDS,
    ATTR_SCENE_ID,
    ATTR_SHADE_IDS,
)

import logging

_LOGGER = logging.getLogger(__name__)


class Scene(ApiResource):
    """Powerview Scene class."""

    api_endpoint = "scenes"

    def __init__(self, raw_data: dict, request: AioRequest) -> None:
        if ATTR_SCENE in raw_data:
            raw_data = raw_data.get(ATTR_SCENE)
        super().__init__(request, self.api_endpoint, raw_data)

    @property
    def room_id(self):
        """Return the room id."""
        if self.api_version >= 3:
            return self._raw_data.get(ATTR_ROOM_IDS)[0]
        return self._raw_data.get(ATTR_ROOM_ID)

    async def activate(self) -> list[int]:
        """Activate this scene."""
        if self.request.api_version >= 3:
            resource_path = join_path(self.base_path, str(self.id), "activate")
            _val = await self.request.put(resource_path)
        else:
            _val = await self.request.get(
                self.base_path, params={ATTR_SCENE_ID: self._id}
            )
            # v2 returns format {'sceneIds': ids} so flattening the list to align v3
            _val = _val.get(ATTR_SHADE_IDS)
        # should return an array of ID's that belong to the scene
        return _val
