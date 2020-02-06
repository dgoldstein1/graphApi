import unittest
import graph
import snap
import server
import handlers


class TestHandlers(unittest.TestCase):
    def test_validateInts(self):
        testTable = [{
            'name': 'is not an array',
            'n': 2093,
            'expectedOutput': False
        }, {
            'name': 'greater than MAX_INT',
            'n': [server.MAX_INT + 1],
            'expectedOutput': False
        }, {
            'name': 'less than 0',
            'n': [-1],
            'expectedOutput': False
        }, {
            'name': 'is None',
            'n': [None],
            'expectedOutput': False
        }, {
            'name': 'is an unparseable strings',
            'n': ["23fjf2=j`sdf"],
            'expectedOutput': False
        }, {
            'name': 'is valid string int',
            'n': ["23423"],
            'expectedOutput': [23423]
        }, {
            'name': 'is valid int',
            'n': [23423],
            'expectedOutput': [23423]
        }]

        for t in testTable:
            self.assertEqual(handlers.validateInts(t['n']),
                             t['expectedOutput'], t['name'])
