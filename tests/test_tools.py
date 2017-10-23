import unittest

from aiopvapi.helpers import tools


class TestTools(unittest.TestCase):

    def test_get_base_path(self):
        self.assertEqual('http://127.0.0.1/api/api2',
                         tools.get_base_path('127.0.0.1', 'api/api2'))
        self.assertEqual('http://127.0.0.1/api/api2',
                         tools.get_base_path('127.0.0.1/', 'api/api2'))
        self.assertEqual('http://127.0.0.1/api/api2',
                         tools.get_base_path('http://127.0.0.1', 'api/api2'))
        self.assertEqual('http://127.0.0.1/api/api2',
                         tools.get_base_path('http://127.0.0.1', '/api/api2'))
        self.assertEqual('http://127.0.0.1/api/api2',
                         tools.get_base_path('http://127.0.0.1', '/api/api2/'))
        self.assertEqual('http://127.0.0.1/api/api2',
                         tools.get_base_path('127.0.0.1', '//api/api2/'))
        self.assertEqual('http://127.0.0.1/api/api2',
                         tools.get_base_path('http://127.0.0.1', '/api//api2'))
        self.assertEqual('http://127.0.0.1/api/api2',
                         tools.get_base_path('http://127.0.0.1//', '/api//api2'))
