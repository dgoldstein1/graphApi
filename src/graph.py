import snap
import logging
from math import ceil, log


class Graph:
    """high level API for accessing graph object"""
    def __init__(self, path):
        """
            - initializer
            - tries to read from graph, else initializes empty
        """
        self.path = path
        try:
            FIn = snap.TFIn(path)
            self.g = snap.TNGraph.Load(FIn)
            logging.debug("Loaded graph '{}' successfully".format(path))
        except RuntimeError as e:
            self.g = snap.TNGraph.New()
            logging.warn("Exception loading graph '{}' at path '{}'. Creating new graph.".format(e.message, path))


    def getNeighbors(self, node = 0):
        """
            - finds node
            - returns all edges from that node
        """
        return [n for n in self.g.GetNI(node).GetOutEdges()]

    def addNeighbors(self, node, neighbors = []):
        """
            - creates node if does not exist
            - adds an array of nodes to given node
            - returns success
        """
        # add node if does not exist
        if (self.g.IsNode(node) == False):
            self.g.AddNode(node)

        # add neighbor nodes with edge to this node
        for n in neighbors:
            # add node if does not exist
            if (self.g.IsNode(n) == False):
                self.g.AddNode(n)            
            # add edge
            self.g.AddEdge(node, n)

    def shortestPath(self, a, b, timeout = 10000):
        """
            - gets shortest path between two nodes within timeout
            - return array of nodes or failure
        """
        pass

    def g(self):
        return self.g