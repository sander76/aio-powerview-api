"""Scenes class managing all scene data."""

import logging

from aiopvapi.helpers.api_base import ApiEntryPoint
from aiopvapi.helpers.constants import ATTR_SCENE_ID, ATTR_SHADE_ID, ATTR_POSITION_DATA
from aiopvapi.resources.scene_member import ATTR_SCENE_MEMBER, SceneMember

_LOGGER = logging.getLogger("__name__")

SCENE_MEMBER_DATA = "sceneMemberData"


class SceneMembers(ApiEntryPoint):
    """A scene member is a device, like a shade, being a member
    of a specific scene."""

    api_path = "api/scenemembers"

    def __init__(self, request):
        super().__init__(request, self.api_path)

    async def create_scene_member(self, shade_position, scene_id, shade_id):
        """Adds a shade to an existing scene"""

        data = {
            ATTR_SCENE_MEMBER: {
                ATTR_POSITION_DATA: shade_position,
                ATTR_SCENE_ID: scene_id,
                ATTR_SHADE_ID: shade_id,
            }
        }
        return await self.request.post(self._base_path, data=data)

    def _resource_factory(self, raw):
        return SceneMember(raw, self.request)

    @staticmethod
    def _loop_raw(raw):
        for _raw in raw[SCENE_MEMBER_DATA]:
            yield _raw

    @staticmethod
    def _get_to_actual_data(raw):
        return raw.get("scenemember")

    async def get_scene_members(self, scene_id):
        """Return all scene members for a particular Scene ID."""

        return await self.get_instances(sceneId=scene_id)

    async def delete_shade_from_scene(self, shade_id, scene_id):
        """Delete a shade from a scene."""
        return await self.request.delete(
            self._base_path, params={ATTR_SCENE_ID: scene_id, ATTR_SHADE_ID: shade_id}
        )
