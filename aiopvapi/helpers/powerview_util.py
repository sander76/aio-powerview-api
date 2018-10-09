from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.resources.room import Room
from aiopvapi.resources.scene import Scene
from aiopvapi.resources.shade import BaseShade
from aiopvapi.rooms import Rooms
from aiopvapi.scene_members import SceneMembers
from aiopvapi.scenes import Scenes
from aiopvapi.shades import Shades


class ResourceNotFoundException(Exception):
    """Exception raised when a resource is not found."""


class PowerViewUtil:
    """A PowerView helper class for basic hub operations."""

    def __init__(self, hub_ip, loop_, session):
        self.request = AioRequest(hub_ip, loop=loop_, websession=session)
        self._scenes_entry_point = Scenes(self.request)
        self._rooms_entry_point = Rooms(self.request)
        self._shades_entry_point = Shades(self.request)
        self._scene_members_entry_point = SceneMembers(self.request)
        self.scenes = []  # A list of scene instances
        self.shades = []  # A list of shade instances
        self.rooms = []  # A list of room instances

    async def get_scenes(self):
        """Query the hub for a list of scene instances."""
        self.scenes = await self._scenes_entry_point.get_instances()

    async def create_scene(self, scene_name, room_id) -> Scene:
        """Create a scene and returns the scene object.

        :raises PvApiError when something is wrong with the hub.
        """
        _raw = await self._scenes_entry_point.create_scene(room_id, scene_name)
        result = Scene(_raw, self.request)
        self.scenes.append(result)
        return result

    async def get_shades(self):
        """Query the hub for a list and shade instances."""
        self.shades = await self._shades_entry_point.get_instances()

    async def get_scene(self, scene_id, from_cache=True) -> Scene:
        """Get a scene resource instance.

        :raises a ResourceNotFoundException when no scene found.
        :raises a PvApiError when something is wrong with the hub.
        """
        if not from_cache:
            await self.get_scenes()
        for _scene in self.scenes:
            if _scene.id == scene_id:
                return _scene
        raise ResourceNotFoundException("Scene not found scene_id: {}".format(scene_id))

    async def get_room(self, room_id, from_cache=True) -> Room:
        """Get a scene resource instance.

        :raises a ResourceNotFoundException when no scene found.
        :raises a PvApiError when something is wrong with the hub.
        """
        if not from_cache:
            await self.get_rooms()
        for _room in self.rooms:
            if _room.id == room_id:
                return _room
        raise ResourceNotFoundException("Room not found. Id: {}".format(room_id))

    async def get_shade(self, shade_id, from_cache=True) -> BaseShade:
        """Get a shade instance based on shade id."""
        if not from_cache:
            await self.get_shades()
        for _shade in self.shades:
            if _shade.id == shade_id:
                return _shade
        raise ResourceNotFoundException("Shade not found. Id: {}".format(shade_id))

    async def get_rooms(self):
        """Query the hub for a list of room instances."""
        self.rooms = await self._rooms_entry_point.get_instances()

    async def open_shade(self, shade_id):
        """Open a shade."""
        _shade = await self.get_shade(shade_id)
        await _shade.open()

    async def close_shade(self, shade_id):
        """Close a shade."""
        _shade = await self.get_shade(shade_id)
        await _shade.close()

    async def activate_scene(self, scene_id: int):
        """Activate a scene

        :param scene_id: Scene id.
        :return:
        """

        _scene = await self.get_scene(scene_id)
        await _scene.activate()

    async def delete_scene(self, scene_id: int):
        """Delete a scene

        :param scene_id:
        :return:
        """
        _scene = await self.get_scene(scene_id, from_cache=False)
        return await _scene.delete()

    async def add_shade_to_scene(self, shade_id, scene_id, position=None):
        """Add a shade to a scene."""
        if position is None:
            _shade = await self.get_shade(shade_id)
            position = await _shade.get_current_position()

        await (SceneMembers(self.request)).create_scene_member(
            position, scene_id, shade_id
        )

    async def remove_shade_from_scene(self, shade_id, scene_id):
        """Remove a shade from a scene"""
        await self._scene_members_entry_point.delete_shade_from_scene(
            shade_id, scene_id
        )
