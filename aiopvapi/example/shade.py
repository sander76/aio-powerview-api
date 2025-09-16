"""Example shades."""

from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.resources.shade import factory
from aiopvapi.shades import Shades, ATTR_SHADE_DATA


class ExampleShade:  # noqa: D101
    def __init__(self, hub_ip) -> None:  # noqa: D107
        self.request = AioRequest(hub_ip)
        self.shades = []
        self._shades_entry_point = Shades(self.request)

    async def get_shades(self):  # noqa: D102
        _shades = await self._shades_entry_point.get_resources()
        for shade in _shades[ATTR_SHADE_DATA]:
            self.shades.append(factory(shade, self.request))

    async def get_shade(self, shade_id):  # noqa: D102
        return await self._shades_entry_point.get_instance(shade_id)

        # {
        #   "shade": {
        #     "id": 65396,
        #     "type": 6,
        #     "batteryStatus": 0,
        #     "batteryStrength": 0,
        #     "roomId": 34274,
        #     "firmware": {
        #       "revision": 1,
        #       "subRevision": 8,
        #       "build": 1944
        #     },
        #     "motor": {
        #       "revision": 0,
        #       "subRevision": 0,
        #       "build": 336
        #     },
        #     "name": "RmFtaWx5IFJpZ2h0",
        #     "groupId": 11497,
        #     "signalStrength": 4,
        #     "capabilities": 0,
        #     "batteryKind": 2,
        #     "smartPowerSupply": {
        #       "status": 0,
        #       "id": 0,
        #       "port": 0
        #     },
        #     "positions": {
        #       "posKind1": 1,
        #       "position1": 582
        #     },
        #     "timedOut": true
        #   }
        # }