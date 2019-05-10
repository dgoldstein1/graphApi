import os
import unittest

from server import app
from HTMLParser import HTMLParser


class TestServer(unittest.TestCase):

    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config["METRICS_PORT"] = 8001
        app.config["GRAPH_SAVE_PATH"] = "../out/test1.graph"
        self.app = app.test_client()
        self.assertEqual(app.debug, False)

    def test_getNeighbors(self):
        # get a normal neighbor
        response = self.app.get("/neighbors?node=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [2,3,4])

    def test_addNeighbors(self):
        # try to add non-list
        response = self.app.post("/neighbors?node=1",
                                 json={"neighbors":"NON-LIST OBJECT"})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.get_json(), {u'code': 422, u'error': u"'neighbors' must be an array but got 'NON-LIST OBJECT'"})
        # try to add a neighbor that's not an int
        response = self.app.post("/neighbors?node=1", json={"neighbors":[2, 3, "NON-INT-OBJECT"]})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.get_json(), {u'code': 422, u'error': u"Node 'NON-INT-OBJECT' could not be converted to an integer"})
        # try to add normal neighbor
        response = self.app.post("/neighbors?node=1", json={"neighbors":[2, 3, 4]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [2, 3, 4])

    def test_getNeighborsParseArgs(self):
        # assert that giving bad node fails
        response = self.app.get("/neighbors")
        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.get_json(),
            {"code": 422, "error": "The query parameter \'node\' is required"}
        )
        response = self.app.get("/neighbors?node=sldfkjsldkfj")
        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.get_json(),
            {"code": 422, "error": "Node \'sldfkjsldkfj\' could not be converted to an integer"}
        )

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
