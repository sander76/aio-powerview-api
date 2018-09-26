"""Scenes class managing all scene data."""

import logging

from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.helpers.api_base import ApiEntryPoint
from aiopvapi.helpers.constants import (
    ATTR_NAME,
    ATTR_ROOM_ID,
    ATTR_ICON_ID,
    ATTR_COLOR_ID,
)
from aiopvapi.helpers.tools import unicode_to_base64
from aiopvapi.resources.scene import Scene

_LOGGER = logging.getLogger("__name__")
ATTR_SCENE_DATA = "sceneData"


class Scenes(ApiEntryPoint):
    api_path = "api/scenes"

    def __init__(self, request: AioRequest):
        super().__init__(request, self.api_path)

    def _resource_factory(self, raw):
        return Scene(raw, self.request)

    @staticmethod
    def _loop_raw(raw):
        for _raw in raw[ATTR_SCENE_DATA]:
            yield _raw

    @staticmethod
    def _get_to_actual_data(raw):
        return raw.get("scene")

    async def create_scene(self, room_id, name, color_id=0, icon_id=0):
        """Creates am empty scene.

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
        _response = await self.request.post(self._base_path, data=_data)
        return _response
