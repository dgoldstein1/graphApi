import unittest

from server import app
from HTMLParser import HTMLParser

MAX_INT = 999999999.0


class TestServer(unittest.TestCase):

    # executed prior to each test
    def setUp(self):
        app.config["GRAPH_SAVE_PATH"] = "../out/test1.graph"
        self.app = app.test_client()
        self.assertEqual(app.debug, False)

    def test_getInfo(self):
        response = self.app.get("/info")
        self.assertEqual(response.status_code, 200)
        info = response.get_data(as_text=True)
        print info
        self.assertTrue("Nodes:                    14499" in info)
        self.assertTrue("Edges:                    18238" in info)

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
        # does not get more than limit
        response = self.app.get("/neighbors?node=2&limit=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [17, 33])

    def test_addEdges(self):
        # try to add normal neighbor
        response = self.app.post("/edges?node=1001",
                                 json={"neighbors": [1002, 1003, 1004, 1006]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"neighborsAdded": []})

    def test_getShortestPath(self):
        # no end given
        response = self.app.get("/shortestPath?start=3")
        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.get_json(), {
                u'code': 422,
                u'error':
                u"could not convert [u'3', None, 1, 3000] to an integer"
            })
        # end node doesn't exist
        response = self.app.get("/shortestPath?start=3&end=350000")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json(), {
            u'code': 500,
            u'error': u'No such path from 3 to 350000'
        })

        # normal path
        response = self.app.get("/shortestPath?start=3&end=35")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [[3, 31, 35]])
        # multiple paths
        response = self.app.get("/shortestPath?start=3&end=35&n=3")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.get_json()), 3)

        # nodes dont exist
        response = self.app.get("/shortestPath?start=23524234&end=324345")
        self.assertEqual(response.status_code, 500)
        expectedResponse = {
            u'code':
            500,
            u'error':
            u'Could not find given start and end values: Execution stopped: Graph->IsNode(StartNId), file ../../snap/snap-core/bfsdfs.h, line 104'
        }
        self.assertEqual(response.get_json(), expectedResponse)
        # parses args correctly
        response = self.app.get(
            "/shortestPath?start=3&end=35&n=5&directed=true")
        self.assertEqual(response.status_code, 200)

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
        response = self.app.get('/metrics', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # assert contains normal prom metrics
        self.assertTrue(
            "HELP python_info Python platform information" in response.data)
        # assert that contains mix in
        self.assertTrue("Number of nodes" in response.data)

    def test_centrality(self):
        # get centrality for a bunch existing / non-existing edges
        response = self.app.post("/centrality", json=[9, 19, 30, 99999])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {})
