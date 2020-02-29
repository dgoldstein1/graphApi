import snap
import logging
import signal
import networkx as nx


class Graph:
    """high level API for accessing graph object"""
    def __init__(self, path):
        """
            - initializer
            - tries to read from graph, else initializes empty
        """
        self.path = path
        # long-compute time values can be saved in class
        self.pageRank = None
        try:
            self.g = nx.read_edgelist(path)
            logging.debug("Loaded graph '{}' successfully".format(path))
        except IOError as e:
            self.g = nx.DiGraph()
            logging.warn(
                "Exception loading graph '{}' at path '{}'. Creating new graph."
                .format(e, path))

    def getGraph(self):
        return self.g

    def info(self):
        """
            create new file with random name
            returns string info on success
            raises IOError error on failure
        """
        return nx.info(self.g)

    def save(self):
        """overwrites files at path with current graph"""
        nx.write_edgelist(self.g, self.path)
        return self.path

    def getNeighbors(self, node="0", limit=10000):
        """
            - finds node
            - returns all edges from that node
        """
        if type(node) is not str:
            raise TypeError("node {} must be a string".format(node))
        neighbors = []
        try:
            i = 0
            for n in self.g.neighbors(node):
                if i >= limit: break
                neighbors.append(n)
                i = i + 1
        except nx.exception.NetworkXError as e:
            raise RuntimeError(e)
        return neighbors

    def addNeighbors(self, node, neighbors=[]):
        """
            - creates node if does not exist
            - adds an array of nodes to given node
            - returns [new nodes added]
        """
        if type(node) is not str:
            raise TypeError("node {} must be a string".format(node))
        # add node if does not exist
        added = []
        for n in neighbors:
            if type(n) is not str:
                raise TypeError("node {} must be a string".format(node))
            if n not in self.g:
                self.g.add_edge(node, n)
                added.append(n)
        return added

    def shortestPath(self, a, b, n=1, timeout=3000, directed=False):
        """
            - gets shortest path(s) between two nodes
            - return array of nodes or failure
        """
        if type(a) is not str or type(b) is not str:
            raise TypeError("nodes {} and {} must be strings".format(a, b))

        paths = []
        try:
            allPaths = nx.all_shortest_paths(self.g, a, b)
            i = 0
            for p in allPaths:
                if i > n: break
                paths.append(p)
                i = i + 1
        except (nx.exception.NetworkXNoPath, nx.NodeNotFound) as e:
            raise IndexError(e)
        return paths

    def nodeCentrality(self, n):
        """
            gets centrality measures for individual node returns as dict
        """
        if type(n) is not str:
            raise TypeError("node {} must be a string".format(n))
        if n not in self.g.nodes:
            return {'error': 'node {} was not found in graph'.format(n)}
        return {
            "degree": len(list(self.g.neighbors(n))),
            "closeness": nx.closeness_centrality(self.g, n),
        }

    def centrality(self, nResults=10):
        """
            returns top nodes for each type of centrality
                - if slow is true, will run through each node in
                  graph, getting highest nodeCentrality()
        """
        # if self.nxg is None:
        #     logging.debug("loading nx graph into memory")
        #     snap.SaveEdgeList(self.g, "temp.edges")
        #     self.nxg = nx.read_edgelist("temp.edges")
        #     os.remove("temp.edges")

        if self.pageRank is None:
            pr = nx.pagerank(self.g)
            self.pageRank = self._extractTopN(pr, nResults)

        return {
            'pageRank': self.pageRank,
        }

    def _extractTopN(self, d, n=10, asc=False):
        """
        utility for extracting top n results from a hash table in format {nodeId : value}
        ascending: lowest values first?
        """
        # sort
        d = sorted(d.items(), key=lambda kv: (kv[1], kv[0]))[:n]
        # convert to good format
        for i in range(0, len(d)):
            d[i] = {"id": d[i][0], "val": d[i][1]}
        return d
