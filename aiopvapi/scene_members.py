"""Scenes class managing all scene data."""

import asyncio
import logging

import aiohttp

from aiopvapi.helpers.tools import get_base_path
from aiopvapi.helpers.api_base import ApiEntryPoint
from aiopvapi.helpers.constants import URL_SCENE_MEMBERS, ATTR_SCENE_ID, \
    ATTR_SHADE_ID, ATTR_POSITION_DATA
from aiopvapi.resources.scene_member import ATTR_SCENE_MEMBER

_LOGGER = logging.getLogger("__name__")


class SceneMembers(ApiEntryPoint):
    """A scene member is a device, like a shade, being a member
    of a specific scene."""
    def __init__(self, hub_ip, loop, websession=None):
        ApiEntryPoint.__init__(self, loop, websession,
                               get_base_path(hub_ip, URL_SCENE_MEMBERS))

    async def create_scene_member(self, shade_position, scene_id, shade_id):
        """Adds a shade to an existing scene

        """
        data = {
            ATTR_SCENE_MEMBER: {
                ATTR_POSITION_DATA: shade_position,
                ATTR_SCENE_ID: scene_id,
                ATTR_SHADE_ID: shade_id
            }
        }
        _result, status = await self.request.post(self._base_path,
                                                       data=data)
        if status == 201:
            _LOGGER.info('SceneMember successfully created.')
            return _result
        else:
            _LOGGER.error('Error creating SceneMember, status: %s' % status)
            return None
