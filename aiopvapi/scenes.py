"""Scenes class managing all scene data."""

import logging

from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.helpers.api_base import ApiEntryPoint
from aiopvapi.helpers.constants import (
    ATTR_ID,
    ATTR_NAME,
    ATTR_ROOM_ID,
    ATTR_ICON_ID,
    ATTR_COLOR_ID,
    ATTR_SCENE_DATA,
)
from aiopvapi.helpers.tools import unicode_to_base64
from aiopvapi.resources.model import PowerviewData
from aiopvapi.resources.scene import Scene

_LOGGER = logging.getLogger(__name__)


class Scenes(ApiEntryPoint):
    """Powerview Scenes"""

    api_endpoint = "scenes"

    def __init__(self, request: AioRequest) -> None:
        super().__init__(request, self.api_endpoint)

    def _resource_factory(self, raw):
        return Scene(raw, self.request)

    def _loop_raw(self, raw):
        if self.api_version < 3:
            raw = raw[ATTR_SCENE_DATA]

        for _raw in raw:
            yield _raw

    def _get_to_actual_data(self, raw):
        if self.api_version >= 3:
            return raw
        return raw.get("scene")

    async def get_scenes_old(self) -> dict:
        """Get a list of scenes.

        :raises PvApiError when an error occurs.
        """
        resources = await self.get_resources()
        if self.api_version < 3:
            return resources[ATTR_SCENE_DATA]
        return resources

    async def get_scenes(self, **kwargs) -> PowerviewData:
        """Get a list of scenes.

        :raises PvApiError when an error occurs.
        """
        resources = await self.get_resources(**kwargs)
        if self.api_version < 3:
            resources = resources[ATTR_SCENE_DATA]
            
        _LOGGER.debug("Raw scenes data: %s", resources)

        # return array of scenes attached to a shade
        processed = {entry[ATTR_ID]: Scene(entry, self.request) for entry in resources}

        return PowerviewData(raw=resources, processed=processed)

    async def create_scene(self, room_id, name, color_id=0, icon_id=0):
        """Creates an empty scene.

        Scenemembers need to be added after the scene has been created.

        :returns: A json object including scene id.
        """
        name = unicode_to_base64(name)
        _data = {
            "scene": {
                ATTR_ROOM_ID: room_id,
                ATTR_NAME: name,
                ATTR_COLOR_ID: color_id,
                ATTR_ICON_ID: icon_id,
            }
        }
        _response = await self.request.post(self.base_path, data=_data)
        return _response
