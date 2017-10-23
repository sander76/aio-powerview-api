import asyncio

import logging
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
    def __init__(self, hub_ip, loop, session):
        self._connection_data = {ATTR_HUB_IP: hub_ip,
                                 ATTR_LOOP: loop,
                                 ATTR_WEB_SESSION: session
                                 }

        self._rooms = Rooms(hub_ip, loop, session)
        self._shades = Shades(hub_ip, loop, session)
        self._scenes = Scenes(hub_ip, loop, session)
        self._scene_members = SceneMembers(hub_ip, loop, session)
        # Cache of all shades connected to the system
        # shadeId -> Shade
        self._shades_cache = None

    # Scenes ###################################################

    @asyncio.coroutine
    def get_scenes(self):
        scenes = yield from self._scenes.get_resources()
        if scenes:
            return [Scene(scene, **self._connection_data) for scene in scenes[ATTR_SCENE_DATA]]
        return None

    @asyncio.coroutine
    def get_scene(self, sceneId):
        _scenes = yield from self._scenes.get_resources()
        if _scenes:
            for _scene in _scenes[ATTR_SCENE_DATA]:
                if _scene[ATTR_ID] == sceneId:
                    return Scene(_scene, **self._connection_data)
        return None

    @asyncio.coroutine
    def create_scene(self, scenename, roomId):
        _newscene = yield from self._scenes.create_scene(roomId, scenename)
        if _newscene:
            return Scene(_newscene, **self._connection_data)
        return None

    @asyncio.coroutine
    def activate_scene(self, scene_id):
        _scene = yield from self.get_scene(scene_id)
        if _scene:
            return (yield from _scene.activate())
        return None

    @asyncio.coroutine
    def delete_scene(self, scene_id):
        _scene = yield from self.get_scene(scene_id)
        if _scene:
            return (yield from _scene.delete())
        return None

    # Rooms ###################################################

    @asyncio.coroutine
    def get_rooms(self):
        return (yield from self._rooms.get_resources())

    @asyncio.coroutine
    def get_room(self, roomId):
        _rooms = yield from self._rooms.get_resources()
        if _rooms:
            for _room in _rooms[ATTR_ROOM_DATA]:
                if _room[ATTR_ID] == roomId:
                    return Room(_room, **self._connection_data)
        return None

    @asyncio.coroutine
    def create_room(self, roomname):
        _newroom = yield from self._rooms.create_room(roomname)
        if _newroom:
            return Room(_newroom, **self._connection_data)
        return None

    @asyncio.coroutine
    def delete_room(self, room_id):
        room = yield from self.get_room(room_id)
        if room:
            return (yield from room.delete())
        return None

    # Shades ###################################################

    @asyncio.coroutine
    def _refresh_shades_cache(self):
        self._shades_cache = {}
        shade_resources = yield from self._scenes.get_resources()
        if shade_resources:
            self._shades_cache = {shade[ATTR_ID]: Shade(shade, **self._connection_data)
                                  for shade in shade_resources[ATTR_SHADE_DATA]}

    @asyncio.coroutine
    def get_shades(self):
        if self._shades_cache is None:
            yield from self._refresh_shades_cache()
        return list(self._shades_cache.values())

    @asyncio.coroutine
    def get_shade(self, shadeId):
        if self._shades_cache is None or shadeId not in self._shades_cache:
            _LOGGER.debug("Shade with id=%d is not in the cache. "
                          "Refreshing the cache.", shadeId)
            yield from self._refresh_shades_cache()
        # Returns shade or None
        return self._shades_cache.get(shadeId)

    @asyncio.coroutine
    def open_shade(self, shadeId):
        shade = yield from self.get_shade(shadeId)
        if shade:
            return (yield from shade.open())
        return None

    @asyncio.coroutine
    def move_shade(self, shadeId, position1=None, position2=None):
        shade = yield from self.get_shade(shadeId)
        if shade:
            return (yield from shade.move_to(position1=position1,
                                             position2=position2))
        return None

    @asyncio.coroutine
    def close_shade(self, shadeId):
        shade = yield from self.get_shade(shadeId)
        if shade:
            return (yield from shade.close())
        return None

    # Misc ###################################################

    @asyncio.coroutine
    def create_scene_member(self, scene_id, shade_id, shade_position):
        return (yield from self._scene_members.create_scene_member(
            shade_position, scene_id, shade_id))

    @asyncio.coroutine
    def create_room_scene_scene_member_move(
            self, room_name=None, scene_name=None,
            shade_id=None, position1=None, position2=None):
        """Creates a room, scene and adds a shade to the scene using a position
        object."""
        _result = None

        _room = yield from self.create_room(room_name)
        yield from asyncio.sleep(3)
        _shade = yield from self.get_shade(shade_id)
        if _room and _shade:
            _scene = yield from self.create_scene(scene_name, _room.id)
            yield from asyncio.sleep(3)
            if _scene:
                yield from asyncio.sleep(3)

                _position = _shade.get_move_data(position1, position2)
                _result = yield from self.create_scene_member(
                    _scene.id, shade_id, _position)
                if _result:
                    return _scene
        return _result
