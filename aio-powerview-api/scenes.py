import asyncio

import logging

from .aiorequest import AioRequest
from . import decode_base64

LOGGER = logging.getLogger("__name__")


class Scenes:
    def __init__(self, hub_ip, aio_request: AioRequest):
        self.request = aio_request
        self._scenes_path = "{}/scenes".format(hub_ip)

    @staticmethod
    def sanitize_scenes(scenes):
        try:
            for scene in scenes['sceneData']:
                scene['name'] = decode_base64(scene['name'])
        except KeyError:
            LOGGER.debug("no scene data available")

    @asyncio.coroutine
    def get_scenes(self):
        scenes = yield from self.request.get(self._scenes_path)
        return scenes

    @asyncio.coroutine
    def activate_scene(self, scene_id):
        self.request.get(self._scenes_path, {"sceneid": scene_id})
