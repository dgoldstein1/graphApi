import snap
import logging
import sys
import signal
import random
import datetime
import os
import random
import time


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
            logging.warn(
                "Exception loading graph '{}' at path '{}'. Creating new graph."
                .format(e.message, path))

    def info(self):
        """
            create new file with random name
            returns string info on success
            raises IOError error on failure
        """
        file = "graph-info-{}.txt".format(random.randint(0, 100000))
        # write to file
        description = "Information for {} at {}.".format(
            self.path, datetime.datetime.now())
        snap.PrintInfo(self.g, "Python type PNGraph", file, True)
        # read back file to string
        info = open(file, 'r').read()
        # remove temp file
        os.remove(file)
        return info

    def save(self):
        """overwrites files at path with current graph"""
        FOut = snap.TFOut(self.path)
        self.g.Save(FOut)
        FOut.Flush()
        return self.path

    def getNeighbors(self, node=0, limit=10000):
        """
            - finds node
            - returns all edges from that node
        """
        nodes = []
        i = 0
        for n in self.g.GetNI(node).GetOutEdges():
            if i >= limit:
                return nodes
            nodes.append(n)
            i = i + 1
        return nodes

    def addNeighbors(self, node, neighbors=[]):
        """
            - creates node if does not exist
            - adds an array of nodes to given node
            - returns [new nodes added]
        """
        # add node if does not exist
        if (self.g.IsNode(node) == False):
            self.g.AddNode(node)

        newNodes = []
        # add neighbor nodes with edge to this node
        for n in neighbors:
            # add node if does not exist
            if (self.g.IsNode(n) == False):
                self.g.AddNode(n)
                newNodes.append(n)
            # add edge
            self.g.AddEdge(node, n)
        return newNodes

    def shortestPath(self, a, b, n=1, timeout=3000):
        """
            - gets shortest path(s) between two nodes
            - return array of nodes or failure
        """
        shortestPathLen = snap.GetShortPath(self.g, a, b, True)
        # make sure that there is a path before going on
        if (shortestPathLen == -1):
            raise IndexError("No such path from {} to {}".format(a, b))

        paths = []
        nodesInUse = []
        directPathFound = False
        execTime = 0
        for x in range(0, n):
            p, pTime = self._shortestPath(a, b, nodesInUse, directPathFound,
                                          timeout / n)
            # accumulate exec time
            execTime = execTime + pTime
            if execTime > timeout: return paths
            # stopping condition, no more paths
            if p == []: return paths
            # direct path found. Edge condition since do
            # not add destination node to excluded node
            if len(p) == 2: directPathFound = True
            # add to list of paths
            paths.append(p)
            # gather more nodesInUse to force unique
            nodesInUse.extend(p[1:len(p) - 1])
        return paths

    def _shortestPath(self, a, b, doNotUseNodes, directPathFound, timeout):
        """
        finds shortest path between two new nodes
            a: source
            b: destination
            doNotUseNodes: array of nodes not to use
        """
        execTime = 0
        path = [a]
        currentNode = a
        # recurse over neighbors to get full path, max iterations is shortest path
        while currentNode != b:
            nextNode = None
            shortest = sys.maxint
            # find shortest of neighbors
            start = time.time()
            for neighbor in self.getNeighbors(currentNode):
                distToEnd = snap.GetShortPath(self.g, neighbor, b, True)
                # update if new shortest in available nodes
                if (distToEnd != -1 and distToEnd < shortest
                        and neighbor not in doNotUseNodes):
                    # do not update if direct path and direct path already found
                    if directPathFound and path == [a] and neighbor == b: break
                    nextNode = neighbor
                    shortest = distToEnd
            # stopping condition
            if nextNode is None: return ([], execTime)
            # continue traversal
            path.append(nextNode)
            currentNode = nextNode
            # add execution time
            execTime = execTime + (time.time() - start) * 1000
            if execTime > timeout: return ([], execTime)
        return (path, execTime)

    def g(self):
        return self.g
