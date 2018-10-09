from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.resources.shade import factory
from aiopvapi.shades import Shades, ATTR_SHADE_DATA


class ExampleShade:
    def __init__(self, hub_ip):
        self.request = AioRequest(hub_ip)
        self.shades = []
        self._shades_entry_point = Shades(self.request)

    async def get_shades(self):
        _shades = await self._shades_entry_point.get_resources()
        for shade in _shades[ATTR_SHADE_DATA]:
            self.shades.append(factory(shade, self.request))

    async def get_shade(self, shade_id):
        return await self._shades_entry_point.get_instance(shade_id)
