import cmd, sys

import asyncio

import aiohttp

from aiopvapi.helpers.constants import ATTR_SHADE_ID, ATTR_NAME_UNICODE, \
    ATTR_ID
from aiopvapi.rooms import Rooms
from aiopvapi.scenes import Scenes
from aiopvapi.shades import Shades, ATTR_SHADE_DATA

ip_address = '192.168.2.4'


class PvCli(cmd.Cmd):
    def __init__(self):
        self._current_shade = None

    def setup(self, ip_address):
        loop = asyncio.get_event_loop()
        session = aiohttp.ClientSession(loop=loop)
        self._shades = Shades(ip_address, loop, session)
        self._rooms = Rooms(ip_address, loop, session)
        self._scenes = Scenes(ip_address, loop, session)

    def do_set_ip_address(self,arg):
        _ip = str(parse(arg)[0])
        self.setup(_ip)

    def do_list_shades(self):
        _shades = self._shades.get_resources()
        for _shade in _shades[ATTR_SHADE_DATA]:
            print("{:<20}{}".format(_shade[ATTR_NAME_UNICODE],_shade[ATTR_ID]))


def parse(arg):
    return arg.split()