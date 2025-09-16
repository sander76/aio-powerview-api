"""Scene Example."""

from aiopvapi.helpers.aiorequest import AioRequest, PvApiError
from aiopvapi.scene_members import SceneMembers


class ExampleSceneMembers:
    """An example."""

    def __init__(self, hub_ip) -> None:  # noqa: D107
        self.request = AioRequest(hub_ip)
        self.raw_scene_members = []
        self.scene_members = []
        self._scene_members_entry_point = SceneMembers(self.request)

    async def get_raw_rooms(self):
        """Get raw rooms."""

        try:
            self.raw_scene_members = (
                await self._scene_members_entry_point.get_resources()
            )
        except PvApiError:  # noqa: TRY302
            raise

    async def get_rooms(self):
        """Return rooms."""
        self.scene_members = await self._scene_members_entry_point.get_instances()
