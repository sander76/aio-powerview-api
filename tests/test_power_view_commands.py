# import unittest
# import asyncio
# import aiohttp
# import json
#
# from aioresponses import aioresponses
#
# from aiopvapi.powerview_tool import PowerViewCommands
# from aiopvapi.resources.scene import Scene
# from aiopvapi.resources.room import Room
# from aiopvapi.resources.shade import Shade
#
# SCENES_DATA = {"sceneIds": [37217, 64533], "sceneData": [
#     {"roomId": 26756, "name": "RGluaW5nIFZhbmVzIE9wZW4=", "colorId": 0, "iconId": 0, "id": 37217, "order": 1},
#     {"roomId": 12372, "name": "TWFzdGVyIE9wZW4=", "colorId": 9, "iconId": 0, "id": 64533, "order": 7}]}
#
# ROOMS_DATA = {"roomIds": [30284, 26756], "roomData": [
#     {"type": 1, "name": "UmVwZWF0ZXJz", "colorId": 15, "iconId": 0, "order": 3, "id": 30284},
#     {"order": 2, "name": "RGluaW5nIFJvb20=", "colorId": 0, "iconId": 0, "id": 26756, "type": 0}]}
#
# SHADES_DATA = {"shadeIds": [29889, 56112], "shadeData": [
#     {"id": 29889, "type": 6, "batteryStatus": 0, "batteryStrength": 0, "name": "UmlnaHQ=", "roomId": 12372,
#      "groupId": 18480,
#      "positions": {"posKind1": 1, "position1": 0}, "firmware": {"revision": 1, "subRevision": 8, "build": 1944}},
#     {"id": 56112, "type": 16, "batteryStatus": 4, "batteryStrength": 180, "name": "UGF0aW8gRG9vcnM=",
#      "roomId": 15103, "groupId": 49380, "positions": {"posKind1": 3, "position1": 65535},
#      "firmware": {"revision": 1, "subRevision": 8, "build": 1944}}]}
#
#
# class TestPowerViewCommands(unittest.TestCase):
#
#     def setUp(self):
#         self.loop = asyncio.get_event_loop()
#         self.websession = aiohttp.ClientSession(loop=self.loop)
#         self.command = PowerViewCommands('127.0.0.1', self.loop, self.websession)
#
#     def tearDown(self):
#         self.websession.close()
#
#     @aioresponses()
#     def test_get_scenes(self, mocked):
#         mocked.get('http://127.0.0.1/api/scenes',
#                    body=json.dumps(SCENES_DATA),
#                    status=200,
#                    headers={'content-type': 'application/json'})
#         scenes = self.loop.run_until_complete(self.command.get_scenes())
#         self.assertTrue(all(isinstance(scene, Scene) for scene in scenes))
#         self.assertEqual(37217, scenes[0].id)
#         self.assertEqual(64533, scenes[1].id)
#
#     @aioresponses()
#     def test_get_scene(self, mocked):
#         mocked.get('http://127.0.0.1/api/scenes',
#                    body=json.dumps(SCENES_DATA),
#                    status=200,
#                    headers={'content-type': 'application/json'})
#         scene = self.loop.run_until_complete(self.command.get_scene(37217))
#         self.assertEqual(37217, scene.id)
#         scene = self.loop.run_until_complete(self.command.get_scene(1))
#         self.assertIsNone(scene)
#
#     @aioresponses()
#     def test_create_scene(self, mocked):
#         mocked.post('http://127.0.0.1/api/scenes',
#                     body=json.dumps({'scene': SCENES_DATA['sceneData'][0]}),
#                     status=201,
#                     headers={'content-type': 'application/json'})
#         scene = self.loop.run_until_complete(self.command.create_scene('New scene', 2312))
#         self.assertTrue(isinstance(scene, Scene))
#         request = mocked.requests[('POST', 'http://127.0.0.1/api/scenes')][-1]
#         self.assertEqual({"scene": {"roomId": 2312, "name": "TmV3IHNjZW5l",
#                                     "colorId": 0, "iconId": 0}},
#                          json.loads(request.kwargs['data']))
#
#     @aioresponses()
#     def test_delete_scene(self, mocked):
#         mocked.get('http://127.0.0.1/api/scenes',
#                    body=json.dumps(SCENES_DATA),
#                    status=200,
#                    headers={'content-type': 'application/json'})
#         mocked.get('http://127.0.0.1/api/scenes',
#                    body=json.dumps(SCENES_DATA),
#                    status=200,
#                    headers={'content-type': 'application/json'})
#         mocked.delete('http://127.0.0.1/api/scenes/37217',
#                       body="",
#                       status=204,
#                       headers={'content-type': 'application/json'})
#         self.assertFalse(self.loop.run_until_complete(self.command.delete_scene(12)))
#         self.assertTrue(self.loop.run_until_complete(self.command.delete_scene(37217)))
#         self.assertFalse(self.loop.run_until_complete(self.command.delete_scene(12)))
#
#     @aioresponses()
#     def test_activate_scene(self, mocked):
#         mocked.get('http://127.0.0.1/api/scenes',
#                    body=json.dumps(SCENES_DATA),
#                    status=200, headers={'content-type': 'application/json'})
#         mocked.get('http://127.0.0.1/api/scenes',
#                    body='"ok"',
#                    status=200, headers={'content-type': 'application/json'})
#         resp = self.loop.run_until_complete(self.command.activate_scene(37217))
#         self.assertEqual('ok', resp)
#         last_request = mocked.requests[('GET', 'http://127.0.0.1/api/scenes')][-1]
#         self.assertEqual({'sceneId': 37217}, last_request.kwargs['params'])
#
#     @aioresponses()
#     def test_get_rooms(self, mocked):
#         mocked.get('http://127.0.0.1/api/rooms',
#                    body=json.dumps(ROOMS_DATA),
#                    status=200, headers={'content-type': 'application/json'})
#         rooms = self.loop.run_until_complete(self.command.get_rooms())
#         self.assertTrue(2, len(rooms))
#         self.assertTrue(all(isinstance(room, Room) for room in rooms))
#         self.assertEqual(30284, rooms[0].id)
#         self.assertEqual(26756, rooms[1].id)
#
#     @aioresponses()
#     def test_get_room(self, mocked):
#         mocked.get('http://127.0.0.1/api/rooms',
#                    body=json.dumps(ROOMS_DATA),
#                    status=200, headers={'content-type': 'application/json'})
#         room = self.loop.run_until_complete(self.command.get_room(30284))
#         self.assertEqual(30284, room.id)
#         room = self.loop.run_until_complete(self.command.get_room(1))
#         self.assertIsNone(room)
#
#     @aioresponses()
#     def test_create_room(self, mocked):
#         """Tests create new room."""
#         mocked.post('http://127.0.0.1/api/rooms',
#                     body=json.dumps({'room': ROOMS_DATA['roomData'][0]}),
#                     status=201,
#                     headers={'content-type': 'application/json'})
#         room = self.loop.run_until_complete(
#             self.command.create_room('New room'))
#         self.assertTrue(isinstance(room, Room))
#         request = mocked.requests[('POST', 'http://127.0.0.1/api/rooms')][-1]
#         self.assertEqual({"room": {"name": "TmV3IHJvb20=", "colorId": 0,
#                                    "iconId": 0}},
#                          json.loads(request.kwargs['data']))
#
#     @aioresponses()
#     def test_delete_room(self, mocked):
#         mocked.get('http://127.0.0.1/api/rooms',
#                    body=json.dumps(ROOMS_DATA),
#                    status=200,
#                    headers={'content-type': 'application/json'})
#         mocked.get('http://127.0.0.1/api/rooms',
#                    body=json.dumps(ROOMS_DATA),
#                    status=200,
#                    headers={'content-type': 'application/json'})
#         mocked.delete('http://127.0.0.1/api/rooms/26756',
#                       body="",
#                       status=204,
#                       headers={'content-type': 'application/json'})
#         self.assertTrue(self.loop.run_until_complete(self.command.delete_room(26756)))
#         self.assertFalse(self.loop.run_until_complete(self.command.delete_room(12)))
#         self.assertFalse(self.loop.run_until_complete(self.command.delete_room(12)))
#
#     def test_get_shades(self):
#         with aioresponses() as mocked:
#             mocked.get('http://127.0.0.1/api/shades',
#                        body=json.dumps(SHADES_DATA),
#                        status=200,
#                        headers={'content-type': 'application/json'})
#             shades = self.loop.run_until_complete(self.command.get_shades())
#         self.assertEqual(2, len(shades))
#         self.assertTrue(all(isinstance(scene, Shade) for scene in shades))
#         self.assertEqual(56112, shades[0].id)
#         self.assertEqual(29889, shades[1].id)
#         # Check that shades are indeed taken from the cache
#         shades = self.loop.run_until_complete(self.command.get_shades())
#         self.assertEqual(56112, shades[0].id)
#         self.assertEqual(29889, shades[1].id)
#
#     @aioresponses()
#     def test_get_shade(self, mocked):
#         mocked.get('http://127.0.0.1/api/shades',
#                    body=json.dumps(SHADES_DATA),
#                    status=200,
#                    headers={'content-type': 'application/json'})
#         shade = self.loop.run_until_complete(self.command.get_shade(10))
#         self.assertIsNone(shade)
#         shade = self.loop.run_until_complete(self.command.get_shade(29889))
#         self.assertEqual(29889, shade.id)
#
#     @aioresponses()
#     def test_open_shade(self, mocked):
#         mocked.get('http://127.0.0.1/api/shades',
#                    body=json.dumps(SHADES_DATA),
#                    status=200,
#                    headers={'content-type': 'application/json'})
#         mocked.put('http://127.0.0.1/api/shades/29889',
#                    body='"ok"',
#                    status=200,
#                    headers={'content-type': 'application/json'})
#         # Opening wrong shade
#         resp = self.loop.run_until_complete(self.command.open_shade(10))
#         self.assertIsNone(resp)
#
#         # Opening existing shade
#         resp = self.loop.run_until_complete(self.command.open_shade(29889))
#         self.assertEqual('ok', resp)
#         request = mocked.requests[('PUT', 'http://127.0.0.1/api/shades/29889')][-1]
#         self.assertEqual({"shade": {"id": 29889, "positions": {"posKind1": 1, "position1": 65535}}},
#                          json.loads(request.kwargs['data']))
#
#     @aioresponses()
#     def test_move_shade(self, mocked):
#         mocked.get('http://127.0.0.1/api/shades',
#                    body=json.dumps(SHADES_DATA),
#                    status=200,
#                    headers={'content-type': 'application/json'})
#         mocked.put('http://127.0.0.1/api/shades/29889',
#                    body='"ok"',
#                    status=200,
#                    headers={'content-type': 'application/json'})
#         resp = self.loop.run_until_complete(self.command.move_shade(29, 3000, 200))
#         self.assertIsNone(resp)
#
#         resp = self.loop.run_until_complete(self.command.move_shade(29889, 3000, 200))
#         self.assertEqual('ok', resp)
#         request = mocked.requests[('PUT', 'http://127.0.0.1/api/shades/29889')][-1]
#         self.assertEqual({"shade": {"id": 29889, "positions": {"posKind1": 1, "position1": 3000}}},
#                          json.loads(request.kwargs['data']))
#
#     @aioresponses()
#     def test_close_shade(self, mocked):
#         mocked.get('http://127.0.0.1/api/shades',
#                    body=json.dumps(SHADES_DATA),
#                    status=200,
#                    headers={'content-type': 'application/json'})
#         mocked.put('http://127.0.0.1/api/shades/29889',
#                    body='"ok"',
#                    status=200,
#                    headers={'content-type': 'application/json'})
#         # Closing wrong shade
#         resp = self.loop.run_until_complete(self.command.close_shade(29))
#         self.assertIsNone(resp)
#
#         # Closing existing shade
#         resp = self.loop.run_until_complete(self.command.close_shade(29889))
#         self.assertEqual('ok', resp)
#         last_request = mocked.requests[('PUT', 'http://127.0.0.1/api/shades/29889')][-1]
#         _val = last_request.kwargs['json']
#
#         self.assertEqual({"shade": {"id": 29889, "positions": {"posKind1": 1, "position1": 0}}},_val)
#         # self.assertEqual({"shade": {"id": 29889, "positions": {"posKind1": 1, "position1": 0}}},
#         #                  json.loads(last_request.kwargs['json']))
