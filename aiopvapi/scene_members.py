"""Scenes class managing all scene data."""

import logging

from aiopvapi.helpers.api_base import ApiEntryPoint
from aiopvapi.helpers.constants import ATTR_SCENE_ID, \
    ATTR_SHADE_ID, ATTR_POSITION_DATA
from aiopvapi.resources.scene_member import ATTR_SCENE_MEMBER

_LOGGER = logging.getLogger("__name__")


class SceneMembers(ApiEntryPoint):
    """A scene member is a device, like a shade, being a member
    of a specific scene."""

    api_path = 'api/scenemembers'

    def __init__(self, request):
        super().__init__(request, self.api_path)

    async def create_scene_member(self, shade_position, scene_id, shade_id):
        """Adds a shade to an existing scene"""

        data = {
            ATTR_SCENE_MEMBER: {
                ATTR_POSITION_DATA: shade_position,
                ATTR_SCENE_ID: scene_id,
                ATTR_SHADE_ID: shade_id
            }
        }
        return await self.request.post(self._base_path, data=data)
