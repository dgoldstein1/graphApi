import os
import unittest

from server import app
from HTMLParser import HTMLParser


class TestServer(unittest.TestCase):

    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config["METRICS_PORT"] = 8001
        app.config["GRAPH_SAVE_PATH"] = "../out/test.graph"
        self.app = app.test_client()
        self.assertEqual(app.debug, False)

    def test_addNeighbors(self):
        response = self.app.post("/neighbors?node=1",
                                 json={'neighbors':[2, 3, 4]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [2, 3, 4])
        # try and get neighbors of node '2'
        response = self.app.get("/neighbors?node=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_getNeighborsParseArgs(self):
        # assert that giving bad node fails
        response = self.app.get("/neighbors")
        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.data,
            '{"code": 422, "error": "The query parameter \'node\' is required"}'
        )
        response = self.app.get("/neighbors?node=sldfkjsldkfj")
        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.data,
            '{"code": 422, "error": "Node \'sldfkjsldkfj\' could not be converted to an integer"}'
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
        self.assertEqual(response.data, 'TEST\n')

    def test_metrics(self):
        # assert that it redirects
        try:
            response = self.app.get('/metrics', follow_redirects=True)
        except RuntimeError as e:
            self.assertEqual(e.message,
                             "Following external redirects is not supported.")
