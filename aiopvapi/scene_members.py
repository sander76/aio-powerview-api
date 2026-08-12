"""Scenes class managing all scene data."""

import logging

from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.helpers.api_base import ApiEntryPoint
from aiopvapi.helpers.constants import (
    ATTR_ID,
    ATTR_POSITIONS,
    ATTR_SCENE_ID,
    ATTR_SHADE_ID,
    SCENE_MEMBER_DATA,
)
from aiopvapi.resources.model import PowerviewData
from aiopvapi.resources.scene import Scene
from aiopvapi.resources.scene_member import ATTR_SCENE_MEMBER, SceneMember

_LOGGER = logging.getLogger(__name__)


class SceneMembers(ApiEntryPoint):
    """A scene member is a device, like a shade, being a member of a specific scene."""

    api_endpoint = "scenemembers"

    def __init__(self, request: AioRequest) -> None:
        """Initialize SceneMembers."""
        super().__init__(request, self.api_endpoint)

    async def create_scene_member(self, shade_position, scene_id, shade_id):
        """Add a shade to an existing scene."""

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

        yield from raw

    def _get_to_actual_data(self, raw):
        if self.api_version >= 3:
            return raw
        return raw.get(SCENE_MEMBER_DATA)

    async def delete_shade_from_scene(self, shade_id, scene_id):
        """Delete a shade from a scene."""
        return await self.request.delete(
            self.base_path,
            params={ATTR_SCENE_ID: scene_id, ATTR_SHADE_ID: shade_id},
        )

    async def get_scene_members(self, **kwargs) -> PowerviewData:
        """Get a list of scene members.

        :raises PvApiError when an error occurs.
        """

        resources = await self.get_resources(**kwargs)
        if self.api_version < 3:
            resources = resources[SCENE_MEMBER_DATA]

        _LOGGER.debug("Raw scene_member data: %s", resources)

        processed = {
            entry[ATTR_ID]: SceneMember(entry, self.request) for entry in resources
        }

        return PowerviewData(raw=resources, processed=processed)


def build_shade_scene_mapping(
    scene_data: PowerviewData,
    scene_member_data: PowerviewData | None = None,
) -> tuple[dict[int, list[int]], dict[int, list[int]]]:
    """Build bidirectional shade↔scene ID mappings.

    Pass scene_member_data for gen2 hubs (from SceneMembers.get_scene_members()).
    For gen3, shadeIds are embedded in scene data and scene_member_data is not needed.

    Returns (scene_to_shade_ids, shade_to_scene_ids).
    """
    scene_to_shade_ids: dict[int, list[int]] = {}
    shade_to_scene_ids: dict[int, list[int]] = {}

    if scene_member_data is not None:
        for member in scene_member_data.raw:
            s_id = member["sceneId"]
            sh_id = member["shadeId"]
            scene_to_shade_ids.setdefault(s_id, []).append(sh_id)
            shade_to_scene_ids.setdefault(sh_id, []).append(s_id)
    else:
        for scene in scene_data.processed.values():
            if not isinstance(scene, Scene):
                continue
            for sh_id in scene.shade_ids:
                scene_to_shade_ids.setdefault(scene.id, []).append(sh_id)
                shade_to_scene_ids.setdefault(sh_id, []).append(scene.id)

    return scene_to_shade_ids, shade_to_scene_ids
