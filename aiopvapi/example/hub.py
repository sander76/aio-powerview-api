from pprint import pprint

from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.hub import Hub


async def get_firmware(hub_ip):
    request = AioRequest(hub_ip)
    hub = Hub(request)
    await hub.query_firmware()

    print("MAIN PROCESSOR")
    print(hub.main_processor_version)

    print("RADIO")
    print(hub.radio_version)


async def get_user_data(hub_ip):
    request = AioRequest(hub_ip)
    hub = Hub(request)
    await hub.query_firmware()

    print("UserData")
    print("hub name: {}".format(hub.hub_name))
    pprint(hub._raw)
