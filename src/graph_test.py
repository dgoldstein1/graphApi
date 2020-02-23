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
        file = "{}/out/test1SavedTest.graph".format(os.getcwd())
        g = graph.Graph(file)
        self.assertEqual(g.g().GetNodes(), 1)
        g.save()

    def test_info(self):
        # bad graph
        g = graph.Graph("../out/slkjlk jsdflkjsdft.gv we wWraph")
        output = g.info()
        self.assertTrue("Nodes:                    0" in output)
        self.assertTrue("Edges:                    0" in output)
        g = graph.Graph("../out/doesntexist.graph")
        # reset dir
        os.listdir(".")
        for f in os.listdir("."):
            if f.startswith("graph-info-"):
                os.remove(f)

        g.g().AddNode(1)
        g.g().AddNode(2)
        g.g().AddNode(3)
        g.g().AddNode(4)
        g.g().AddEdge(1, 2)
        g.g().AddEdge(1, 3)
        g.g().AddEdge(3, 4)
        output = g.info()
        self.assertTrue("Nodes:                    4" in output)
        self.assertTrue("Edges:                    3" in output)
        # make sure no files 'graph-info-*'
        os.listdir(".")
        for f in os.listdir("."):
            self.assertFalse(f.startswith("graph-info-"))

    def test_getNeighbors(self):
        g = graph.Graph("../out/doesntexist.graph")
        g.g().AddNode(1)
        g.g().AddNode(2)
        g.g().AddNode(3)
        g.g().AddNode(4)
        g.g().AddEdge(1, 2)
        g.g().AddEdge(1, 3)
        g.g().AddEdge(3, 4)
        self.assertEqual(g.getNeighbors(1), [2, 3])
        self.assertEqual(g.getNeighbors(2), [])
        self.assertEqual(g.getNeighbors(3), [4])
        # limit
        self.assertEqual(g.getNeighbors(1, 2), [2, 3])
        self.assertEqual(g.getNeighbors(1, 1), [2])
        self.assertEqual(g.getNeighbors(1, -1), [])
        # trying to access node that doesn't exist throws error
        with self.assertRaises(RuntimeError):
            g.getNeighbors(0)

    def test_addNeighbors(self):
        g = graph.Graph("../out/doesntexist.graph")
        # add neighbors that don't exist
        nodes = g.addNeighbors(1, [2, 3])
        self.assertEqual(nodes, [2, 3])
        self.assertEqual(g.g().GetNodes(), 3)
        self.assertEqual(g.g().GetEdges(), 2)
        # add neighbors that do exist
        nodes = g.addNeighbors(1, [2, 3, 4])
        self.assertEqual(g.g().GetNodes(), 4)
        self.assertEqual(g.g().GetEdges(), 3)
        # returns only new edges
        self.assertEqual(nodes, [4])

    def test_shortestPath(self):
        g = graph.Graph("../out/doesntexist.graph")
        g.g().AddNode(1)
        g.g().AddNode(2)
        g.g().AddNode(3)
        g.g().AddNode(4)
        g.g().AddNode(5)
        g.g().AddEdge(1, 2)
        g.g().AddEdge(1, 3)
        g.g().AddEdge(3, 4)
        # 5 isn't connected to anything
        with self.assertRaises(IndexError):
            g.shortestPath(1, 5)
        self.assertEqual(g.shortestPath(1, 2), [[1, 2]])
        self.assertEqual(g.shortestPath(1, 4), [[1, 3, 4]])
        # multiple unique paths
        g.g().AddEdge(1, 5)
        g.g().AddEdge(5, 4)
        paths = g.shortestPath(1, 4, n=2)
        self.assertTrue([1, 3, 4] in paths)
        self.assertTrue([1, 5, 4] in paths)
        # doesnt give duplicates
        paths = g.shortestPath(1, 4, n=3)
        self.assertTrue(len(paths) < 10)
        # no duplicates in direct routes
        g.g().AddNode(12345679)
        g.g().AddEdge(1, 12345679)

        g.g().AddNode(12345678)
        g.g().AddEdge(1, 12345678)
        g.g().AddEdge(12345678, 12345679)

        # self.assertEqual(g.shortestPath(1, 12345679, n=10),
        #                  [[1, 12345679], [1, 12345678, 12345679]])
        # doesnt give paths that dont end up at destination
        g.g().AddNode(6)
        g.g().AddEdge(1, 6)
        g.g().AddEdge(6, 5)
        paths = g.shortestPath(1, 4, n=10)
        self.assertEqual(len(paths), 2)
        # doesn't give same path twice
        paths = g.shortestPath(1, 4, n=10)
        duplicates = [x for n, x in enumerate(paths) if x in paths[:n]]
        self.assertTrue(len(duplicates) == 0)
        # doesn't give same path twice (randomizes)
        for i in range(10, 10000):
            # make a bunch of paths from 1=>4
            g.g().AddNode(i)
            g.g().AddEdge(1, i)
            g.g().AddEdge(i, 4)
        self.assertNotEqual(g.shortestPath(1, 4, n=4),
                            [[1, 3, 4], [1, 3, 4], [1, 3, 4], [1, 3, 4]])
        # timeout
        timeout = 1000
        start = time.time()
        paths = g.shortestPath(1, 4, n=500, timeout=timeout)
        execTime = (time.time() - start) * 1000
        self.assertTrue(execTime < timeout + 1000)  # add 1000ms buffer
        self.assertNotEqual(paths, [])

        # error with too many things in hash set
        # sangamon county, illinois to daggett county, utah
        g = graph.Graph("./out/counties.graph")
        paths = g.shortestPath(284128874, 656315998, n=5)

    def test_shortest_path_dir(self):
        g = graph.Graph("../out/doesntexist.graph")
        g.g().AddNode(1)
        g.g().AddNode(2)
        g.g().AddNode(3)
        g.g().AddNode(4)
        g.g().AddNode(5)
        g.g().AddEdge(1, 2)
        g.g().AddEdge(1, 3)
        g.g().AddEdge(3, 4)
        g.g().AddEdge(4, 5)

        g.g().AddNode(6)
        g.g().AddEdge(5, 6)
        p = g.shortestPath(1, 6, n=1, directed=True)
        self.assertEqual(p, [[1, 3, 4, 5, 6]])

        p = g.shortestPath(1, 5, n=1, directed=True)
        self.assertEqual(p, [[1, 3, 4, 5]])

        g = graph.Graph("./out/counties.graph")
        paths = g.shortestPath(284128874, 656315998, n=5, directed=True)
        self.assertNotEqual(paths, [[]])

        g = graph.Graph("./out/synonyms_big.graph")
        # 760964475 = "help"
        # 90598913 = "diddley"
        paths = g.shortestPath(760964475, 90598913, n=5, directed=True)
        self.assertNotEqual(paths, [[]])

    def test_g(self):
        g = graph.Graph("../out/doesntexist.graph").g()
        # creates new graph on bad filename
        self.assertIsNotNone(g)
        self.assertEqual(g.GetNodes(), 0)
        # reads in graph from legit file
        file = "{}/out/test1.graph".format(os.getcwd())
        g = graph.Graph(file).g()
        self.assertNotEqual(g.GetNodes(), 0)

    def test_node_centrality(self):
        g = graph.Graph("./out/counties.graph")
        c = g.nodeCentrality(284128874)
        expectedResult = {
            'eccentricity': 37,
            'degree': 0.0026936026936026937,
            'closeness': 0.0591162233130638,
            'farness': 16.91583027393793
        }
        self.assertEqual(c, expectedResult)

    def test_centrality(self):
        # g = graph.Graph("./out/counties.graph")
        g = graph.Graph("../out/doesntexist.graph")
        g.g().AddNode(1)
        g.g().AddNode(2)
        g.g().AddNode(3)
        g.g().AddNode(4)
        g.g().AddNode(5)
        g.g().AddEdge(1, 2)
        g.g().AddEdge(1, 3)
        g.g().AddEdge(3, 4)
        g.g().AddEdge(4, 5)
        start = time.time()
        c = g.centrality()
        execTime = (time.time() - start) * 1000
        self.assertLess(execTime, 15000)
        expectedResult = {}
        self.assertEqual(c, expectedResult)