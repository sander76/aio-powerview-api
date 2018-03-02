from aiopvapi.resources.scene import Scene
from aiopvapi.scenes import Scenes
from tests.fake_server import TestFakeServer


class TestScenes(TestFakeServer):

    def test_get_resources_200(self):
        """Test get resources with status 200."""

        async def go():
            await self.start_fake_server()
            scenes = Scenes(self.request)
            res = await scenes.get_resources()
            return res

        resources = self.loop.run_until_complete(go())

        self.assertEqual(2, len(resources['sceneIds']))
        self.assertEqual(2, len(resources['sceneData']))
        self.assertEqual('Dining Vanes Open',
                         resources['sceneData'][0]['name_unicode'])
        self.assertEqual('Master Open',
                         resources['sceneData'][1]['name_unicode'])

    # def test_get_resources_201(self, mocked):
    #     """Test get resources with wrong status."""
    #     mocked.get('http://127.0.0.1/api/scenes',
    #                body=RETURN_VALUE,
    #                status=201,
    #                headers={'content-type': 'application/json'})
    #     with self.assertRaises(PvApiResponseStatusError):
    #         resources = self.loop.run_until_complete(
    #             self.scenes.get_resources())

    def test_create_scene_201(self):
        """Tests create new scene."""

        async def go():
            await self.start_fake_server()
            scenes = Scenes(self.request)
            res = await scenes.create_scene(
                12372, 'New scene', color_id=1, icon_id=2)
            return res
        resp = self.loop.run_until_complete(go())
        self.assertEqual({"scene": {"roomId": 12372, "name": "TmV3IHNjZW5l",
                                    "colorId": 1, "iconId": 2}},
                         resp)

    def test_get_instance(self):
        async def go():
            await self.start_fake_server()
            scenes = Scenes(self.request)
            response = await scenes.get_instance(43436)
            return response

        resp = self.loop.run_until_complete(go())
        self.assertIsInstance(resp, Scene)
        self.assertEqual(resp.name, 'Test')

    # def test_create_scene_202(self, mocked):
    #     """Tests create new scene with wrong status code."""
    #     mocked.post('http://127.0.0.1/api/scenes',
    #                 body='"ok"',
    #                 status=202,
    #                 headers={'content-type': 'application/json'})
    #     with self.assertRaises(PvApiResponseStatusError):
    #         resp = self.loop.run_until_complete(
    #             self.scenes.create_scene(12372, 'New scene', color_id=1,
    #                                      icon_id=2))
