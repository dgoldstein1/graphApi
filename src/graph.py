import snap
import logging

class Graph:
    """high level API for accessing graph object"""
    def __init__(self, path = ""):
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



    def addNeighbors(self, node = "", neighbors = []):
        """
            - creates node if does not exist
            - adds an array of nodes to given node
            - returns success
        """
        
        pass


    def getShortestPath(self, a = "", b = "", timeout = 10000):
        """
            - gets shortest path between two nodes within timeout
            - return array of nodes or failure
        """
        pass

    def g(self):
        return self.g