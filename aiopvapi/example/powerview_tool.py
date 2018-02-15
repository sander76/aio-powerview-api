import asyncio
import logging

from aiopvapi.helpers.aiorequest import AioRequest, PvApiError
from aiopvapi.helpers.constants import ATTR_ID
from aiopvapi.resources.room import Room
from aiopvapi.resources.scene import Scene
from aiopvapi.resources.shade import Shade
from aiopvapi.rooms import Rooms, ATTR_ROOM_DATA
from aiopvapi.scene_members import SceneMembers
from aiopvapi.scenes import Scenes, ATTR_SCENE_DATA
from aiopvapi.shades import Shades, ATTR_SHADE_DATA

ATTR_HUB_IP = 'hub_ip'
ATTR_LOOP = 'loop'
ATTR_WEB_SESSION = 'websession'

_LOGGER = logging.getLogger(__name__)


class PowerViewCommands:
    def __init__(self, hub_ip, loop=None, session=None):
        """
        :param hub_ip: ip address of the powerview hub
        :param loop: asyncio loop
        :param session: aiohttp Client session (aiohttp.ClientSession())
        """

        self.request = AioRequest(hub_ip, loop, session)

        self._rooms = Rooms(self.request)
        self._shades = Shades(self.request)
        self._scenes = Scenes(self.request)
        self._scene_members = SceneMembers(self.request)
        # Cache of all shades connected to the system
        # shadeId -> Shade
        self._shades_cache = None

    # Scenes ###################################################

    async def get_scenes(self):
        try:
            scenes = await self._scenes.get_resources()
            return [Scene(scene, self.request) for scene in
                    scenes[ATTR_SCENE_DATA]]
        except PvApiError as err:
            print(err)

    async def get_scene(self, sceneId: int):
        scenes = (await self.get_scenes()) or []
        for scene in scenes:
            if scene.id == sceneId:
                return scene
        return None

    async def create_scene(self, scenename:str, roomId:int):
        _newscene = await self._scenes.create_scene(roomId, scenename)
        if _newscene:
            return Scene(_newscene, self.request)
        return None

    async def activate_scene(self, scene_id):
        _scene = await self.get_scene(scene_id)
        if _scene:
            return await _scene.activate()
        return None

    async def delete_scene(self, scene_id):
        _scene = await self.get_scene(scene_id)
        if _scene:
            return await _scene.delete()
        return None

    # Rooms ###################################################

    async def get_rooms(self):
        rooms = await self._rooms.get_resources()
        if rooms:
            return [Room(room, self.request) for room in
                    rooms[ATTR_ROOM_DATA]]
        return None

    async def get_room(self, roomId):
        rooms = (await self.get_rooms()) or []
        for room in rooms:
            if room.id == roomId:
                return room
        return None

    async def create_room(self, roomname):
        _newroom = await self._rooms.create_room(roomname)
        if _newroom:
            return Room(_newroom, self.request)
        return None

    async def delete_room(self, room_id):
        room = await self.get_room(room_id)
        if room:
            return await room.delete()
        return None

    # Shades ###################################################

    async def _refresh_shades_cache(self):
        self._shades_cache = {}
        shade_resources = await self._shades.get_resources()
        if shade_resources:
            self._shades_cache = {
                shade[ATTR_ID]: Shade(shade, self.request)
                for shade in shade_resources[ATTR_SHADE_DATA]}

    async def get_shades(self):
        if self._shades_cache is None:
            await self._refresh_shades_cache()
        return list(self._shades_cache.values())

    async def get_shade(self, shadeId):
        if self._shades_cache is None or shadeId not in self._shades_cache:
            _LOGGER.debug("Shade with id=%d is not in the cache. "
                          "Refreshing the cache.", shadeId)
            await self._refresh_shades_cache()
        # Returns shade or None
        return self._shades_cache.get(shadeId)

    async def open_shade(self, shadeId):
        shade = await self.get_shade(shadeId)
        if shade:
            return await shade.open()
        return None

    async def move_shade(self, shadeId, position1=None, position2=None):
        shade = await self.get_shade(shadeId)
        if shade:
            return (await shade.move_to(position1=position1,
                                        position2=position2))
        return None

    async def close_shade(self, shadeId):
        shade = await self.get_shade(shadeId)
        if shade:
            return await shade.close()
        return None

    # Misc ###################################################

    async def create_scene_member(self, scene_id, shade_id, shade_position):
        return (await self._scene_members.create_scene_member(
            shade_position, scene_id, shade_id))

    async def create_room_scene_scene_member_move(
            self, room_name=None, scene_name=None,
            shade_id=None, position1=None, position2=None):
        """Creates a room, scene and adds a shade to the scene using a position
        object."""
        _result = None

        _room = await self.create_room(room_name)
        await asyncio.sleep(3)
        _shade = await self.get_shade(shade_id)
        if _room and _shade:
            _scene = await self.create_scene(scene_name, _room.id)
            await asyncio.sleep(3)
            if _scene:
                await asyncio.sleep(3)

                _position = _shade.get_move_data(position1, position2)
                _result = await self.create_scene_member(
                    _scene.id, shade_id, _position)
                if _result:
                    return _scene
        return _result
