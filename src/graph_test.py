import unittest
import graph
import logging
import snap
import os

class TestGraphMethods(unittest.TestCase):

	def setUp(self):
		logging.getLogger().setLevel(logging.ERROR)

	def test_addNeighbors(self):
		pass

	def test_getShortestPath(sel):
		pass

	def test_g(self):
		# creates new graph on bad filename
		g = graph.Graph("../out/doesntexist.graph").g()
		self.assertIsNotNone(g)
		self.assertEqual(g.GetNodes(), 0)
		# reads in graph from legit file
		file = "{}/out/test1.graph".format(os.getcwd())
		g = graph.Graph(file).g()
		self.assertNotEqual(g.GetNodes(), 0)