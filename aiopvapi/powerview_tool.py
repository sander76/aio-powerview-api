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
    def __init__(self, hub_ip, _loop, session):
        self._connection_data = {ATTR_HUB_IP: hub_ip,
                                 ATTR_LOOP: _loop,
                                 ATTR_WEB_SESSION: session
                                 }

        self._rooms = Rooms(hub_ip, _loop, session)
        self._shades = Shades(hub_ip, _loop, session)
        self._scenes = Scenes(hub_ip, _loop, session)
        self._scene_members = SceneMembers(hub_ip, _loop, session)

    @asyncio.coroutine
    def create_scene(self, scenename, roomId):
        result = None
        _newscene = yield from self._scenes.create_scene(roomId, scenename)
        if _newscene:
            result = Scene(_newscene, **self._connection_data)
        return result

    @asyncio.coroutine
    def get_scenes(self):
        _scenes = yield from self._scenes.get_resources()
        return _scenes

    @asyncio.coroutine
    def activate_scene(self, scene_id):
        result = None
        _scene = yield from self.get_scene(scene_id)
        if _scene:
            result = yield from _scene.activate()
        return result

    @asyncio.coroutine
    def delete_scene(self, scene_id):
        result = None
        _scene = yield from self.get_scene(scene_id)
        if _scene:
            result = yield from _scene.delete()

        return result

    @asyncio.coroutine
    def create_room(self, roomname):
        _newroom = yield from self._rooms.create_room(roomname)
        if _newroom:
            return Room(_newroom, **self._connection_data)
        return None

    @asyncio.coroutine
    def get_rooms(self):
        _rooms = yield from self._rooms.get_resources()
        return _rooms

    @asyncio.coroutine
    def delete_room(self, room_id):
        _result = None
        _room = yield from self.get_room(room_id)
        if _room:
            _result = yield from _room.delete()

        return _result

    @asyncio.coroutine
    def create_scene_member(self, scene_id, shade_id, shade_position):
        _scene_member = yield from self._scene_members.create_scene_member(
            shade_position, scene_id, shade_id)
        return _scene_member

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

    @asyncio.coroutine
    def open_shade(self, shadeId):
        _result = None
        shade = yield from self.get_shade(shadeId)
        if shade:
            _result = yield from shade.open()
        return _result

    @asyncio.coroutine
    def move_shade(self, shadeId, position1=None, position2=None):
        result = None
        shade = yield from self.get_shade(shadeId)
        if shade:
            result = yield from shade.move_to(position1=position1,
                                              position2=position2)
        return result

    @asyncio.coroutine
    def close_shade(self, shadeId):
        result = None
        shade = yield from self.get_shade(shadeId)
        if shade:
            result = yield from shade.close()
        return result

    @asyncio.coroutine
    def get_room(self, roomId):
        new_room = None
        _rooms = yield from self._rooms.get_resources()
        if _rooms:
            for _room in _rooms[ATTR_ROOM_DATA]:
                if _room[ATTR_ID] == roomId:
                    new_room = Room(_room, **self._connection_data)
                    break
        return new_room

    @asyncio.coroutine
    def get_scene(self, sceneId):
        new_scene = None
        _scenes = yield from self._scenes.get_resources()
        if _scenes:
            for _scene in _scenes[ATTR_SCENE_DATA]:
                if _scene[ATTR_ID] == sceneId:
                    new_scene = Scene(_scene, **self._connection_data)
                    break
        return new_scene

    @asyncio.coroutine
    def get_shade(self, shadeId):
        new_shade = None
        _shades = yield from self._shades.get_resources()
        if _shades:
            for _shade in _shades[ATTR_SHADE_DATA]:
                if _shade[ATTR_ID] == shadeId:
                    new_shade = Shade(_shade, **self._connection_data)
                    break

        return new_shade



# if __name__ == "__main__":
#     logging.basicConfig(level=logging.DEBUG)
#     import aiohttp
#     import pprint
#
#     _hub = "192.168.0.118"
#     _shade_id = 9518
#
#     _loop = asyncio.get_event_loop()
#     session = aiohttp.ClientSession(loop=_loop)
#     _loop = asyncio.get_event_loop()
#
#     # pv = PowerViewCommands(_hub, loop, session, _shade_id, 'test',
#     #                            'no_location')
#
#     # result = loop.run_until_complete(pv.move_shade(_shade_id, position1=30000))
#     # result = loop.run_until_complete(
#     # result = loop.run_until_complete(pv.create_scene('test', 36422))
#     # result = loop.run_until_complete(pv.get_rooms())
#     # result = loop.run_until_complete(pv.delete_room(56953))
#     result = _loop.run_until_complete(
#         pv.create_room_scene_scene_member_move("test1", "test_scene",
#                                                _shade_id, 30000))
#
#     # result = loop.run_until_complete(pv.activate)
#
#     # result = loop.run_until_complete(
#     #     pv.create_scene_member(23010,9518,{'position1':30000,'posKind1':1})
#     # )
#     # result = loop.run_until_complete(pv.get_shade(9518))
#     # loop.run_until_complete(pv.delete_scene(45892))
#     # loop.run_until_complete(pv.get_scenes())
#
#     session.close()
