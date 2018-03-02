from aiopvapi.resources.shade import BaseShade
from aiopvapi.shades import Shades
from tests.fake_server import TestFakeServer


class TestShades(TestFakeServer):

    def test_get_resources_200(self):
        """Test get resources with status 200."""

        async def go():
            await self.start_fake_server()
            shades = Shades(self.request)
            res = await shades.get_resources()
            return res

        resources = self.loop.run_until_complete(go())
        self.assertEqual(2, len(resources['shadeIds']))
        self.assertEqual(2, len(resources['shadeData']))
        self.assertEqual('Right',
                         resources['shadeData'][0]['name_unicode'])
        self.assertEqual('Patio Doors',
                         resources['shadeData'][1]['name_unicode'])

    def test_get_instance(self):
        async def go():
            await self.start_fake_server()
            shades = Shades(self.request)
            response = await shades.get_instance(11155)
            return response

        resp = self.loop.run_until_complete(go())
        self.assertIsInstance(resp, BaseShade)
        self.assertEqual(resp.name, 'Shade 1')
    # def test_get_resources_201(self):
    #     """Test get resources with wrong status."""
    #     mocked.get('http://127.0.0.1/api/shades',
    #                body=RETURN_VALUE,
    #                status=201,
    #                headers={'content-type': 'application/json'})
    #     with self.assertRaises(PvApiResponseStatusError):
    #         resources = self.loop.run_until_complete(self.shades.get_resources())
