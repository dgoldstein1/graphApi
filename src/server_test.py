import os
import unittest

from server import app
from HTMLParser import HTMLParser


class TestServer(unittest.TestCase):

    # executed prior to each test
    def setUp(self):
        app.config["GRAPH_SAVE_PATH"] = "../out/test1.graph"
        self.app = app.test_client()
        self.assertEqual(app.debug, False)

    def test_getNeighbors(self):
        # get node that doesn't exist
        response = self.app.get("/neighbors?node=1234234")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.get_json(), {
                u'code': 404,
                u'error': u"Node '1234234' was not found or does not exist"
            })
        # get normal node
        response = self.app.get("/neighbors?node=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(),
                         [9, 19, 30, 34, 53, 56, 59, 94, 97])
        # get normal node
        response = self.app.get("/neighbors?node=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [17, 33, 89, 95])

    # def test_addEdges(self):
    #     # try to add non-list
    #     response = self.app.post("/edges?node=1",
    #                              json={"neighborsAdded": "NON-LIST OBJECT"})
    #     self.assertEqual(response.status_code, 422)
    #     self.assertEqual(
    #         response.get_json(), {
    #             u'code': 422,
    #             u'error':
    #             u"'neighbors' must be an array but got 'NON-LIST OBJECT'"
    #         })
    #     # try to add a neighbor that's not an int
    #     response = self.app.post("/edges?node=1",
    #                              json={"neighborsAdded": [2, 3, "NON-INT-OBJECT"]})
    #     self.assertEqual(response.status_code, 422)
    #     self.assertEqual(
    #         response.get_json(), {
    #             u'code':
    #             422,
    #             u'error':
    #             u"Node 'NON-INT-OBJECT' could not be converted to an integer"
    #         })
    #     # try to add normal neighbor
    #     response = self.app.post("/edges?node=1001",
    #                              json={"neighborsAdded": [1002, 1003, 1004]})
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.get_json(), [1002, 1003, 1004])

    def test_getShortestPath(self):
        # no end given
        response = self.app.get("/shortestPath?start=3")
        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.get_json(), {
                u'code': 422,
                u'error':
                u"The query parameters 'start' and 'end' are required"
            })
        # bad end node
        response = self.app.get("/shortestPath?start=3&end=pjijsiji")
        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.get_json(), {
                u'code':
                422,
                u'error':
                u"Nodes '3' and 'pjijsiji' could not be converted to integers"
            })
        # end node doesn't exist
        response = self.app.get("/shortestPath?start=3&end=350000")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json(), {
            u'code': 500,
            u'error': u'No such path from 3 to 350000'
        })
        # too big int
        response = self.app.get(
            "/shortestPath?start=3&end=99999999999999999999999")
        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.get_json(), {
                u'code': 422,
                u'error': u'Integers over 999999999.0 are not supported'
            })
        # normal path
        response = self.app.get("/shortestPath?start=3&end=35")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [3, 31, 35])

    def test_getNeighborsParseArgs(self):
        # assert that giving bad node fails
        response = self.app.get("/neighbors")
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.get_json(), {
            "code": 422,
            "error": "The query parameter \'node\' is required"
        })
        response = self.app.get("/neighbors?node=sldfkjsldkfj")
        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.get_json(), {
                "code":
                422,
                "error":
                "Node \'sldfkjsldkfj\' could not be converted to an integer"
            })
        response = self.app.get("/neighbors?node=9999999999")
        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.get_json(), {
                u'code': 422,
                u'error': u'Integers over 999999999.0 are not supported'
            })

    def test_serve_docs(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data)
        try:
            HTMLParser().feed(response.data)
        except:
            self.fail("Could not parse docs")

    def test_save_positive(self):
        """attempt to save when already exists"""
        response = self.app.get('/save', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data)

    def test_metrics(self):
        # assert that it redirects
        try:
            response = self.app.get('/metrics', follow_redirects=True)
        except RuntimeError as e:
            self.assertEqual(e.message,
                             "Following external redirects is not supported.")
