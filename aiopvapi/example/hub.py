"""Hub example."""

from pprint import pprint

from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.hub import Hub


async def get_firmware(hub_ip):  # noqa: D103
    request = AioRequest(hub_ip)
    hub = Hub(request)
    await hub.query_firmware()

    print("MAIN PROCESSOR")  # noqa: T201
    print(hub.main_processor_version)  # noqa: T201

    print("RADIO")  # noqa: T201
    print(hub.radio_version)  # noqa: T201


async def get_user_data(hub_ip):  # noqa: D103
    request = AioRequest(hub_ip)
    hub = Hub(request)
    await hub.query_firmware()

    print("UserData")  # noqa: T201
    print(f"hub name: {hub.hub_name}")  # noqa: T201
    pprint(hub._raw)  # noqa: SLF001, T203
