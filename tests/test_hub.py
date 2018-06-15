import asyncio
from unittest.mock import MagicMock

import pytest

from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.hub import Version, Hub
from tests.test_scene_members import AsyncMock


@pytest.fixture
def fake_aiorequest():
    request = AioRequest('127.0.0.1', websession=MagicMock())
    request.get = AsyncMock()
    request.put = AsyncMock()
    return request


def test_version():
    version1 = Version(123, 456, 789)
    assert version1._build == 123
    assert version1._revision == 456
    assert version1._sub_revision == 789

    version2 = Version(123, 456, 789)

    assert version1 == version2

    version3 = Version(456, 123, 789)

    assert not version1 == version3

    version1 = Version('abc', 'def', 'ghi')
    version2 = Version('abc', 'def', 'ghi')
    assert version1 == version2


def test_hub(fake_aiorequest):
    hub = Hub(fake_aiorequest)
    assert hub._base_path == 'http://127.0.0.1/api'
    loop = asyncio.get_event_loop()

    fake_aiorequest.get = AsyncMock(return_value={})

    loop.run_until_complete(hub.query_firmware())

    hub.request.get.mock.assert_called_once_with(
        'http://127.0.0.1/api/fwversion')
