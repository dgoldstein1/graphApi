import snap

class Graph:
    """high level API for accessing graph object"""
    def __init__(self):
        # create new graph
        self.g = snap.TNGraph.New()

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