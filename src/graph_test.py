import unittest
import graph
import logging
import snap
import os


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
        print output
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
        self.assertEqual(g.shortestPath(1, 2), [1, 2])
        self.assertEqual(g.shortestPath(1, 4), [1, 3, 4])

    def test_g(self):
        g = graph.Graph("../out/doesntexist.graph").g()
        # creates new graph on bad filename
        self.assertIsNotNone(g)
        self.assertEqual(g.GetNodes(), 0)
        # reads in graph from legit file
        file = "{}/out/test1.graph".format(os.getcwd())
        g = graph.Graph(file).g()
        self.assertNotEqual(g.GetNodes(), 0)
