"""Scenes class managing all scene data."""

import asyncio
import logging

import binascii
from aiopvapi.helpers.api_base import ApiEntryPoint
from aiopvapi.helpers.constants import URL_SCENES, ATTR_NAME, ATTR_NAME_UNICODE
from aiopvapi.helpers.tools import base64_to_unicode, get_base_path, \
    unicode_to_base64

_LOGGER = logging.getLogger("__name__")
ATTR_SCENE_DATA = 'sceneData'

SCENE_ROOM_ID = 'roomId'
SCENE_ID = 'id'
SCENE_ORDER = 'order'
SCENE_ICON_ID = 'iconId'
SCENE_COLOR_ID = 'colorId'


class Scenes(ApiEntryPoint):
    def __init__(self, hub_ip, loop, websession=None):
        ApiEntryPoint.__init__(self, loop, websession,
                               get_base_path(hub_ip, URL_SCENES))

    @staticmethod
    def sanitize_resources(scenes: dict):
        """Cleans up incoming scene data

        :param scenes: The dict with scene data to be sanitized.
        :returns: Cleaned up scene dict.
        """
        try:
            for scene in scenes[ATTR_SCENE_DATA]:
                try:
                    scene[ATTR_NAME_UNICODE] = base64_to_unicode(
                        scene[ATTR_NAME])
                except binascii.Error:
                    pass
            return scenes
        except (KeyError, TypeError):
            _LOGGER.debug("no scene data available")
            return None

    async def create_scene(self, room_id, name,
                           color_id=0, icon_id=0):
        """Creates am empty scene.

        Scenemembers need to be added after the scene has been created.

        :returns: A json object including scene id.
        """
        name = unicode_to_base64(name)
        _data = {"scene":
                     {SCENE_ROOM_ID: room_id,
                      ATTR_NAME: name,
                      SCENE_COLOR_ID: color_id,
                      SCENE_ICON_ID: icon_id
                      }}
        _response, status = await self.request.post(
            self._base_path, data=_data)
        if status == 200 or status == 201:
            _LOGGER.debug("Scene successfully created")
            return _response
        else:
            _LOGGER.error("Error creating scene")
            return None
