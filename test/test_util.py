import unittest
from chalktalk import util
from datetime import datetime
import json


class TestUtil(unittest.TestCase):

    def test_valid_uuid(self):
        self.assertTrue(util.valid_uuid('1daededb-f85c-44fa-a152-dd7915d30a62'))
        # completely invalid
        self.assertFalse(util.valid_uuid('kek'))
        # no dashes
        self.assertFalse(util.valid_uuid('1daededbf85c44faa152dd7915d30a62'))
        # g at the start (not valid hex char)
        self.assertFalse(util.valid_uuid('gdaededb-f85c-44fa-a152-dd7915d30a62'))

    def test_valid_semester(self):
        self.assertTrue(util.valid_semester('H2016'))
        self.assertTrue(util.valid_semester('V1996'))
        
        self.assertFalse(util.valid_semester('blah'))
        self.assertFalse(util.valid_semester('X1996'))
        self.assertFalse(util.valid_semester('V96'))
        self.assertFalse(util.valid_semester('V996'))

    def test_get_semester(self):
        groups = [
            '''
            {
                "url": "http://wiki.math.ntnu.no/tma4240",
                "membership": {
                  "fsroles": [
                    "STUDENT"
                  ],
                  "active": true,
                  "notAfter": "2016-12-14T23:00:00Z",
                  "basic": "member",
                  "displayName": "Student",
                  "subjectRelations": "undervisning"
                },
                "parent": "fc:org:ntnu.no",
                "type": "fc:fs:emne",
                "displayName": "Statistikk",
                "id": "fc:fs:fs:emne:ntnu.no:TMA4240:1"
            }
            ''',
            '''
            {
            "url": "http://item.ntnu.no/courses/ttm4100/",
            "membership": {
              "fsroles": [
                "STUDENT"
              ],
              "active": true,
              "displayName": "Student",
              "basic": "member"
            },
            "parent": "fc:org:ntnu.no",
            "type": "fc:fs:emne",
            "displayName": "Kommunikasjon - Tjenester og nett",
            "id": "fc:fs:fs:emne:ntnu.no:TTM4100:1"
            }
            '''
        ]
        self.assertEqual('H2016', util.get_semester(json.loads(groups[0])))
        self.assertEqual('V2017', util.get_semester(json.loads(groups[1])))

    def test_get_lecturedates(self):
        start = datetime(2017, 1, 15)
        end = datetime(2017, 2, 10)
        weekdays = ['monday', 'friday']
        result = [datetime(2017, 1, 16),
                  datetime(2017, 1, 20),
                  datetime(2017, 1, 23),
                  datetime(2017, 1, 27),
                  datetime(2017, 1, 30),
                  datetime(2017, 2, 3),
                  datetime(2017, 2, 6),
                  datetime(2017, 2, 10)]

        self.assertEqual(util.get_lecturedates(start, end, weekdays), result)

