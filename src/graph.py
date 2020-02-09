import snap
import logging
import sys
import signal
from contextlib import contextmanager
import random
import datetime
import os
import random


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

    def shortestPath(self, a, b, n=1, forceUnique=False):
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
        for x in range(0, n):
            p = self._shortestPath(a, b, shortestPathLen, nodesInUse)
            # stopping condition: path lengths are greater than shortest path
            if (len(p) != shortestPathLen + 1):
                return paths
            paths.append(p)
            # gather more nodesInUse to force unique
            if forceUnique:
                nodesInUse.extend(p[1:len(p) - 1])
                nodesInUse = list(set(nodesInUse))
        return paths

    def _shortestPath(self, a, b, shortestPathLen, doNotUseNodes):
        """
        finds shortest path between two new nodes
            a: source
            b: destination
            shortestPathLen: length of desired shortest path
            doNotUseNodes: array of nodes not to use
        """
        path = [a]
        currentNode = a
        # recurse over neighbors to get full path, max iterations is shortest path
        for i in xrange(0, shortestPathLen):
            shortest = sys.maxint
            possibleNextNodes = []
            for neighbor in self.getNeighbors(currentNode):
                # get dist to end node
                distToEnd = snap.GetShortPath(self.g, neighbor, b, True)
                # update if less than current min
                if distToEnd != -1 and distToEnd <= shortest and neighbor not in doNotUseNodes:
                    # same length, add to possible next nodes
                    if distToEnd == shortest:
                        possibleNextNodes.append(neighbor)
                    else:  # new shortest found
                        possibleNextNodes = [neighbor]
                        shortest = distToEnd
            # get random next node from list
            if len(possibleNextNodes) == 0: return path
            currentNode = random.choice(possibleNextNodes)
            path.append(currentNode)
        return path

    @contextmanager
    def _timeout(self, time):
        # Register a function to raise a MemoryError on the signal.
        signal.signal(signal.SIGALRM, self._raise_timeout)
        # Schedule the signal to be sent after ``time``.
        signal.alarm(time)

        try:
            yield
        except MemoryError:
            pass
        finally:
            # Unregister the signal so it won't be triggered
            # if the timeout is not reached.
            signal.signal(signal.SIGALRM, signal.SIG_IGN)

    def _raise_timeout(self, signum, frame):
        raise MemoryError

    def g(self):
        return self.g
