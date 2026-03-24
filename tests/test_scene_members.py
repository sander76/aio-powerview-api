import asyncio
import unittest
from unittest import mock

from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.resources.scene_member import SceneMember
from aiopvapi.scene_members import SceneMembers
from tests.fake_server import TestFakeServer


def AsyncMock(*args, **kwargs):
    m = mock.MagicMock(*args, **kwargs)

    async def mock_coro(*args, **kwargs):
        return m(*args, **kwargs)

    mock_coro.mock = m
    return mock_coro


class TestSceneMembers(unittest.TestCase):

    def setUp(self):
        self.fake_ip = '123.123.123.123'

    @mock.patch('aiopvapi.helpers.aiorequest.AioRequest.check_response', new=AsyncMock())
    def test_remove_shade_from_scene(self):
        """Tests create new scene."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        request = AioRequest(self.fake_ip, loop)

        _del_mock = AsyncMock(return_value=None)

        request.websession.delete = _del_mock

        async def go():
            scene_members = SceneMembers(request)
            await scene_members.delete_shade_from_scene(1234, 5678)

        resp = loop.run_until_complete(go())
        _del_mock.mock.assert_called_once_with(
            'http://{}/api/sceneMembers'.format(self.fake_ip),
            params={"sceneId": 5678,
                    'shadeId': 1234})


class TestGetSceneMembers(TestFakeServer):

    def test_get_scene_members_keyed_by_id(self):
        """processed is keyed by scene member id, not shadeId."""

        async def go():
            await self.start_fake_server()
            scene_members = SceneMembers(self.request)
            return await scene_members.get_scene_members()

        data = self.loop.run_until_complete(go())
        self.assertIn(101, data.processed)
        self.assertIn(102, data.processed)
        self.assertIn(103, data.processed)

    def test_get_scene_members_returns_scene_member_instances(self):
        """Each value in processed is a SceneMember."""

        async def go():
            await self.start_fake_server()
            scene_members = SceneMembers(self.request)
            return await scene_members.get_scene_members()

        data = self.loop.run_until_complete(go())
        for member in data.processed.values():
            self.assertIsInstance(member, SceneMember)

    def test_get_scene_members_preserves_all_memberships_for_shade_in_multiple_scenes(self):
        """A shade appearing in multiple scenes produces distinct entries, not overwrites."""

        async def go():
            await self.start_fake_server()
            scene_members = SceneMembers(self.request)
            return await scene_members.get_scene_members()

        data = self.loop.run_until_complete(go())
        # shade 49988 appears in both scene 37217 (id=101) and scene 64533 (id=102)
        self.assertEqual(data.processed[101].shade_id, 49988)
        self.assertEqual(data.processed[101].scene_id, 37217)
        self.assertEqual(data.processed[102].shade_id, 49988)
        self.assertEqual(data.processed[102].scene_id, 64533)

    def test_get_scene_members_count(self):
        """All three scene members are present in processed."""

        async def go():
            await self.start_fake_server()
            scene_members = SceneMembers(self.request)
            return await scene_members.get_scene_members()

        data = self.loop.run_until_complete(go())
        self.assertEqual(3, len(data.processed))
