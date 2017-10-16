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

ATTR_OPEN = 'open'
ATTR_CLOSE = 'close'


class PowerViewCommands:
    def __init__(self, hub_ip, _loop, session):
        self._connection_data = {ATTR_HUB_IP: hub_ip,
                                 ATTR_LOOP: _loop,
                                 ATTR_WEB_SESSION: session
                                 }

        self._rooms = Rooms(hub_ip, _loop, session)
        self._shades = Shades(hub_ip, _loop, session)
        self._scenes = Scenes(hub_ip, _loop, session)
        self._scene_members = SceneMembers(hub_ip, _loop, session)

    async def create_scene(self, scenename, roomId):
        _newscene = await self._scenes.create_scene(roomId, scenename)
        if _newscene:
            return Scene(_newscene, **self._connection_data)
        return None

    async def get_scenes(self):
        return await self._scenes.get_resources()

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

    async def create_room(self, roomname):
        _newroom = await self._rooms.create_room(roomname)
        if _newroom:
            return Room(_newroom, **self._connection_data)
        return None

    async def get_shades(self):
        return await self._shades.get_resources()

    async def get_rooms(self):
        return await self._rooms.get_resources()

    async def delete_room(self, room_id):
        room = await self.get_room(room_id)
        if room:
            return await room.delete()
        return None

    async def create_scene_member(self, scene_id, shade_id, shade_position):
        return await self._scene_members.create_scene_member(
            shade_position, scene_id, shade_id)

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

    async def open_shade(self, shadeId):
        shade = await self.get_shade(shadeId)
        if shade:
            return await shade.open()
        return None

    async def move_shade(self, shadeId, position1=None, position2=None):
        shade = await self.get_shade(shadeId)
        if shade:
            return await shade.move_to(position1=position1,
                                       position2=position2)
        return None

    async def close_shade(self, shadeId):
        shade = await self.get_shade(shadeId)
        if shade:
            return await shade.close()
        return None

    async def get_room(self, roomId):
        _rooms = await self._rooms.get_resources()
        if _rooms:
            for _room in _rooms[ATTR_ROOM_DATA]:
                if _room[ATTR_ID] == roomId:
                    return Room(_room, **self._connection_data)
        return None

    async def get_scene(self, sceneId):
        _scenes = await self._scenes.get_resources()
        if _scenes:
            for _scene in _scenes[ATTR_SCENE_DATA]:
                if _scene[ATTR_ID] == sceneId:
                    return Scene(_scene, **self._connection_data)
        return None

    async def get_shade(self, shadeId):
        _shades = await self._shades.get_resources()
        if _shades:
            for _shade in _shades[ATTR_SHADE_DATA]:
                if _shade[ATTR_ID] == shadeId:
                    return Shade(_shade, **self._connection_data)
        return None