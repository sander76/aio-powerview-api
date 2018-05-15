import asyncio
import unittest
from unittest import mock

from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.scene_members import SceneMembers


def AsyncMock(*args, **kwargs):
    m = mock.MagicMock(*args, **kwargs)

    async def mock_coro(*args, **kwargs):
        return m(*args, **kwargs)

    mock_coro.mock = m
    return mock_coro


class TestSceneMembers(unittest.TestCase):

    def setUp(self):
        self.fake_ip = '123.123.123.123'

    @mock.patch('aiopvapi.helpers.aiorequest.check_response', new=AsyncMock())
    def test_remove_shade_from_scene(self):
        """Tests create new scene."""
        loop = asyncio.get_event_loop()
        request = AioRequest(self.fake_ip, loop)

        _del_mock = AsyncMock(return_value=None)

        request.websession.delete = _del_mock

        async def go():
            scene_members = SceneMembers(request)
            await scene_members.delete_shade_from_scene(1234, 5678)

        resp = loop.run_until_complete(go())
        _del_mock.mock.assert_called_once_with(
            'http://{}/api/scenemembers'.format(self.fake_ip),
            params={"sceneId": 5678,
                    'shadeId': 1234})
