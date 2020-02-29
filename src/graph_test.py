import unittest
import graph
import logging
import snap
import os
import time


class TestGraphMethods(unittest.TestCase):
    def setUp(self):
        logging.getLogger().setLevel(logging.ERROR)

    def test_save(self):
        file = "{}/out/test1SavedGraph.edges".format(os.getcwd())
        g = graph.Graph(file)
        self.assertEqual(len(g.getGraph().nodes), 10)
        g.save()

    def test_info(self):
        # bad graph
        g = graph.Graph("../out/slkjlk jsdflkjsdft.gv we wWraph")
        output = g.info()
        print output
        self.assertTrue("Number of nodes: 0" in output)
        self.assertTrue("Number of edges: 0" in output)
        g = graph.Graph("../out/doesntexist.graph")

        g.getGraph().add_edge("1", "2")
        g.getGraph().add_edge("1", "3")
        g.getGraph().add_edge("3", "4")
        output = g.info()
        self.assertTrue("Number of nodes: 4" in output)
        self.assertTrue("Number of edges: 3" in output)

    def test_getNeighbors(self):
        g = graph.Graph("../out/doesntexist.graph")
        g.getGraph().add_edge("1", "2")
        g.getGraph().add_edge("1", "3")
        g.getGraph().add_edge("3", "4")
        # raises type error on wrong type
        with self.assertRaises(TypeError):
            g.getNeighbors(1)

        self.assertEqual(g.getNeighbors("1"), ["3", "2"])
        self.assertEqual(g.getNeighbors("2"), [])
        self.assertEqual(g.getNeighbors("3"), ["4"])
        # limit
        self.assertEqual(g.getNeighbors("1", 2), ["3", "2"])
        self.assertEqual(g.getNeighbors("1", 1), ["3"])
        self.assertEqual(g.getNeighbors("1", -1), [])
        # trying to access node that doesn't exist throws error
        with self.assertRaises(RuntimeError):
            g.getNeighbors("0")

    def test_addNeighbors(self):
        g = graph.Graph("../out/doesntexist.graph")
        # add neighbors that don't exist
        # raises type error on wrong type
        with self.assertRaises(TypeError):
            nodes = g.addNeighbors(1, [])

        with self.assertRaises(TypeError):
            nodes = g.addNeighbors("1", [2])

        nodes = g.addNeighbors("1", ["2", "3"])
        self.assertEqual(nodes, ["2", "3"])
        self.assertEqual(len(g.getGraph().nodes), 3)
        self.assertEqual(len(g.getGraph().edges), 2)
        # add neighbors that do exist
        nodes = g.addNeighbors("1", ["2", "3", "4"])
        self.assertEqual(len(g.getGraph().nodes), 4)
        self.assertEqual(len(g.getGraph().edges), 3)
        # returns only new edges
        self.assertEqual(nodes, ["4"])

    def test_shortestPath(self):
        g = graph.Graph("../out/doesntexist.graph")
        g.getGraph().add_edge("1", "2")
        g.getGraph().add_edge("1", "3")
        g.getGraph().add_edge("3", "4")
        # wrong type
        with self.assertRaises(TypeError):
            g.shortestPath("1", 2)
        # 5 isn't connected to anything
        with self.assertRaises(IndexError):
            g.shortestPath("1", "5")

        self.assertEqual(g.shortestPath("1", "2"), [["1", "2"]])
        self.assertEqual(g.shortestPath("1", "4"), [["1", "3", "4"]])
        # multiple unique paths
        g.getGraph().add_edge("1", "5")
        g.getGraph().add_edge("5", "4")
        paths = g.shortestPath("1", "4", n=2)
        self.assertTrue(["1", "3", "4"] in paths)
        self.assertTrue(["1", "5", "4"] in paths)
        # doesnt give duplicates
        paths = g.shortestPath("1", "4", n=3)
        self.assertTrue(len(paths) < 10)
        # no duplicates in direct routes
        g.getGraph().add_edge("1", "12345679")

        g.getGraph().add_edge("1", "12345678")
        g.getGraph().add_edge("12345678", "12345679")

        # doesnt give paths that dont end up at destination
        g.getGraph().add_edge("1", "6")
        g.getGraph().add_edge("6", "5")
        paths = g.shortestPath("1", "4", n=10)
        self.assertEqual(len(paths), 2)
        # doesn't give same path twice
        paths = g.shortestPath("1", "4", n=10)
        duplicates = [x for n, x in enumerate(paths) if x in paths[:n]]
        self.assertTrue(len(duplicates) == 0)
        # doesn't give same path twice (randomizes)
        for i in range(10, 10000):
            # make a bunch of paths from 1=>4
            g.getGraph().add_edge("1", str(i))
            g.getGraph().add_edge(str(i), "4")
        self.assertNotEqual(g.shortestPath("1", "4", n=4),
                            [["1", "3", "4"], ["1", "3", "4"], ["1", "3", "4"],
                             ["1", "3", "4"]])
        # timeout
        timeout = 1000
        start = time.time()
        paths = g.shortestPath("1", "4", n=500, timeout=timeout)
        execTime = (time.time() - start) * 1000
        self.assertTrue(execTime < timeout + 1000)  # add 1000ms buffer
        self.assertNotEqual(paths, [])

        g = graph.Graph("../out/doesntexist.graph")
        g.getGraph().add_edge("1", "2")
        g.getGraph().add_edge("1", "3")
        g.getGraph().add_edge("3", "4")
        g.getGraph().add_edge("4", "5")

        g.getGraph().add_edge("5", "6")
        p = g.shortestPath("1", "6", n=1, directed=True)
        self.assertEqual(p, [["1", "3", "4", "5", "6"]])

        p = g.shortestPath("1", "5", n=1, directed=True)
        self.assertEqual(p, [["1", "3", "4", "5"]])

    def test_node_centrality(self):
        file = "{}/out/test1SavedGraph.edges".format(os.getcwd())
        g = graph.Graph(file)
        with self.assertRaises(TypeError):
            g.nodeCentrality(2)

        c = g.nodeCentrality("2")
        expectedResult = {'closeness': 0.6923076923076923, 'degree': 5}
        self.assertEqual(c, expectedResult)

    def test_centrality(self):
        g = graph.Graph("../out/doesntexist.graph")
        g.getGraph().add_edge("1", "2")
        g.getGraph().add_edge("1", "3")
        g.getGraph().add_edge("3", "4")
        g.getGraph().add_edge("4", "5")

        start = time.time()
        c = g.centrality()
        execTime = (time.time() - start) * 1000
        self.assertLess(execTime, 15000)
        self.assertEqual(
            c, {
                "pageRank": [{
                    'id': "1",
                    'val': 0.11184682438205981
                }, {
                    'id': "2",
                    'val': 0.15938145155157013
                }, {
                    'id': "3",
                    'val': 0.15938145155157013
                }, {
                    'id': "4",
                    'val': 0.247320578151483
                }, {
                    'id': "5",
                    'val': 0.322069694363317
                }]
            })
