import unittest
from mock import Mock

import Main
import requests

class BaseAvailableTestCase(unittest.TestCase):
    def setUp(self):
        mockResponse = {
                            "id": "8",
                            "name": "test",
                            "steps": 10,
                            "nextMeeting": {
                                "from": "2016-07-20T17:45:00.000Z",
                                "to": "2016-07-20T18:30:00.000Z"
                            },
                            "available": True
                        }
        mockGet = Mock()
        mockGet.get.return_value = mockResponse
        requests.get = mockGet.get

class BaseOccupiedTestCase(unittest.TestCase):
        def setUp(self):
            mockResponse = {
                            "id": "8",
                            "name": "test",
                            "steps": 10,
                            "nextMeeting": {
                                "from": "2016-07-20T17:45:00.000Z",
                                "to": "2016-07-20T18:30:00.000Z"
                            },
                            "available": False
                        }
            mockGet = Mock()
            mockGet.get.return_value = mockResponse
            requests.get = mockGet.get

class RoomIsAvailableTestCase(BaseAvailableTestCase):
    def runTest(self):
        id = "8"
        isAvailable = Main.get_room_status(id)
        self.assertEqual(True, isAvailable, "Room should be available")

class RoomIsOccupiedTestCase(BaseOccupiedTestCase):
    def runTest(self):
        id = "8"
        isAvailable = Main.get_room_status(id)
        self.assertEqual(False, isAvailable, "Room should be occupied")


if __name__ == '__main__':
    unittest.main()