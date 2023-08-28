"""Scenes class managing all scene data."""

import logging

from aiopvapi.helpers.api_base import ApiEntryPoint
from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.helpers.constants import (
    ATTR_SCENE_ID,
    ATTR_SHADE_ID,
    ATTR_POSITIONS,
    SCENE_MEMBER_DATA,
)
from aiopvapi.resources.scene_member import ATTR_SCENE_MEMBER, SceneMember

from aiopvapi.resources.model import PowerviewData

_LOGGER = logging.getLogger("__name__")


class SceneMembers(ApiEntryPoint):
    """A scene member is a device, like a shade, being a member
    of a specific scene."""

    api_endpoint = "scenemembers"

    def __init__(self, request: AioRequest) -> None:
        super().__init__(request, self.api_endpoint)

    async def create_scene_member(self, shade_position, scene_id, shade_id):
        """Adds a shade to an existing scene"""

        data = {
            ATTR_SCENE_MEMBER: {
                ATTR_POSITIONS: shade_position,
                ATTR_SCENE_ID: scene_id,
                ATTR_SHADE_ID: shade_id,
            }
        }
        return await self.request.post(self.base_path, data=data)

    def _resource_factory(self, raw):
        return SceneMember(raw, self.request)

    def _loop_raw(self, raw):
        if self.api_version < 3:
            raw = raw[SCENE_MEMBER_DATA]

        for _raw in raw:
            yield _raw

    def _get_to_actual_data(self, raw):
        if self.api_version >= 3:
            return raw
        return raw.get(SCENE_MEMBER_DATA)

    async def get_scene_members_old(self, scene_id):
        """Return all scene members for a particular Scene ID."""

        return await self.get_instances(sceneId=scene_id)

    async def delete_shade_from_scene(self, shade_id, scene_id):
        """Delete a shade from a scene."""
        return await self.request.delete(
            self.base_path,
            params={ATTR_SCENE_ID: scene_id, ATTR_SHADE_ID: shade_id},
        )

    async def get_scene_members(self) -> PowerviewData:
        """Get a list of scene members.

        :raises PvApiError when an error occurs.
        """
        resources = await self.get_resources()
        if self.api_version < 3:
            resources = resources[SCENE_MEMBER_DATA]

        # return array of scenes attached to a shade
        processed = {
            entry["shadeId"]: SceneMember(entry, self.request) for entry in resources
        }

        _LOGGER.debug("Raw scene_member data: %s", resources)
        return PowerviewData(raw=resources, processed=processed)
