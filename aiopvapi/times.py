import asyncio



# class Times(ApiEntryPoint):
#     def __init__(self, hub_ip, loop, websession=None):
#         ApiEntryPoint.__init__(self, loop, websession)
#         self._times_path = "{}api/times".format(hub_ip)
#
#     @asyncio.coroutine
#     def get_resources(self):
#         """Get a times resource.
#
#         :returns: A json object.
#         """
#         _time = yield from self.request.get(self._times_path)
#         return _time
