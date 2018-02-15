from aiopvapi.rooms import Rooms

from tests.fake_server import TestFakeServer


class TestRooms(TestFakeServer):

    def test_get_resources_200(self):
        """Test get resources with status 200."""

        async def go():
            await self.start_fake_server()
            rooms = Rooms(self.request)
            resources = await rooms.get_resources()
            return resources

        resources = self.loop.run_until_complete(go())
        self.assertEqual(2, len(resources['roomIds']))
        self.assertEqual(2, len(resources['roomData']))
        self.assertEqual('Repeaters',
                         resources['roomData'][0]['name_unicode'])
        self.assertEqual('Dining Room',
                         resources['roomData'][1]['name_unicode'])

    # def test_get_resources_201(self):
    #     """Test get resources with wrong status."""
    #     mocked.get('http://127.0.0.1/api/rooms',
    #                body=RETURN_VALUE,
    #                status=201,
    #                headers={'content-type': 'application/json'})
    #
    #     with self.assertRaises(PvApiResponseStatusError):
    #         resources = self.loop.run_until_complete(
    #             self.rooms.get_resources())
    #
    #
    def test_create_room_201(self):
        """Tests create new room."""

        async def go():
            await self.start_fake_server()
            rooms = Rooms(self.request)
            response = await rooms.create_room(
                'New room', color_id=1, icon_id=2)
            return response

        resp = self.loop.run_until_complete(go())
        self.assertEqual(resp['id'], 1)
        self.assertEqual(resp['name'], 'TmV3IHJvb20=')



    # def test_create_room_202(self):
    #     """Tests create new room with wrong status code."""
    #     mocked.post('http://127.0.0.1/api/rooms',
    #                 body='"ok"',
    #                 status=202,
    #                 headers={'content-type': 'application/json'})
    #     with self.assertRaises(PvApiResponseStatusError):
    #         resp = self.loop.run_until_complete(
    #             self.rooms.create_room('New room', color_id=1, icon_id=2))
