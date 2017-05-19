from aiopvapi.aiorequest import AioRequest
from aiopvapi.rooms import Rooms
from .scenes import Scenes

class Hub:
    def __init__(self, hub_ip, loop, websession):
        self.ip_address = hub_ip
        self.request = AioRequest(loop, websession)
        self._base_path = "http://{}/api".format(hub_ip)
        self._user_path = "{}/userdata/".format(self._base_path)
        self._times_path = "{}/times".format(self._base_path)

        self.scenes = Scenes(self._base_path,self.request)
        self.rooms = Rooms(self._base_path,self.request)
