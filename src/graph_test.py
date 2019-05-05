import unittest
import graph
import logging
import snap
import os

class TestGraphMethods(unittest.TestCase):

	def setUp(self):
		logging.getLogger().setLevel(logging.ERROR)

	def test_getNeighbors(self):
		pass

	def test_addNeighbors(self):
		g = graph.Graph("../out/doesntexist.graph")
		# add neighbors that don't exist
		g.addNeighbors(1, [2,3])
		self.assertEqual(g.g().GetNodes(), 3)
		self.assertEqual(g.g().GetEdges(), 2)
		# add neighbors that do exist
		g.addNeighbors(1, [2,3,4])
		self.assertEqual(g.g().GetNodes(), 4)
		self.assertEqual(g.g().GetEdges(), 3)

	def test_getShortestPath(self):
		pass

	def test_g(self):
		g = graph.Graph("../out/doesntexist.graph").g()
		# creates new graph on bad filename
		self.assertIsNotNone(g)
		self.assertEqual(g.GetNodes(), 0)
		# reads in graph from legit file
		file = "{}/out/test1.graph".format(os.getcwd())
		g = graph.Graph(file).g()
		self.assertNotEqual(g.GetNodes(), 0)