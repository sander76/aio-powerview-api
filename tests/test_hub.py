from unittest.mock import MagicMock
import json

import pytest

from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.hub import Version, Hub
from tests.test_scene_members import AsyncMock
from tests.fake_server import TestFakeServer, FAKE_BASE_URL, USER_DATA_VALUE


@pytest.fixture
def fake_aiorequest():
    request = AioRequest("127.0.0.1", websession=MagicMock())
    request.api_version = 2
    request.get = AsyncMock()
    request.put = AsyncMock()
    return request


def test_version():
    version1 = Version(123, 456, 789)
    assert version1._revision == 123
    assert version1._sub_revision == 456
    assert version1._build == 789

    version2 = Version(123, 456, 789)

    assert version1 == version2

    version3 = Version(456, 123, 789)

    assert not version1 == version3

    version1 = Version("abc", "def", "ghi")
    version2 = Version("abc", "def", "ghi")
    assert version1 == version2


class TestHub_v2(TestFakeServer):
    def test_hub_init(self):
        async def go():
            await self.start_fake_server()
            hub = Hub(self.request)
            await hub.query_firmware()
            return hub

        hub = self.loop.run_until_complete(go())

        assert hub.base_path == "http://" + FAKE_BASE_URL + "/api"

        # self.request.get.mock.assert_called_once_with(FAKE_BASE_URL + "/userdata")
        data = json.loads(USER_DATA_VALUE)

        assert hub.main_processor_info == data["userData"]["firmware"]["mainProcessor"]
        assert hub.main_processor_version == Version(2, 0, 395)  # "REVISION: 2 SUB_REVISION: 0 BUILD: 395"
        assert hub.radio_version == [Version(2, 0, 1307)]  # ["REVISION: 2 SUB_REVISION: 0 BUILD: 1307"]
        assert hub.ssid == "cisco789"
        assert hub.name == "Hubby"


class TestHub_v3(TestFakeServer):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.api_version = 3

    def test_hub_init(self):
        async def go():
            await self.start_fake_server(api_version=3)
            hub = Hub(self.request)
            await hub.query_firmware()
            return hub

        hub = self.loop.run_until_complete(go())

        assert hub.base_path == "http://" + FAKE_BASE_URL + "/home"

        # self.request.get.mock.assert_called_once_with(FAKE_BASE_URL + "/userdata")
        data = json.loads(USER_DATA_VALUE)

        assert hub.main_processor_info == data["userData"]["firmware"]["mainProcessor"]
        assert hub.main_processor_version == Version(2, 0, 395)  # "REVISION: 2 SUB_REVISION: 0 BUILD: 395"
        assert hub.radio_version == [Version(2, 0, 1307)]  # ["REVISION: 2 SUB_REVISION: 0 BUILD: 1307"]
        assert hub.ssid == "cisco789"
        assert hub.name == "00:26:74:af:fd:ae"
