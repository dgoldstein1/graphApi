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
                                          timeout - execTime)
            # stopping condition, no more paths
            if p == []: return paths
            # direct path found. Edge condition since do
            # not add destination node to excluded node
            if len(p) == 2: directPathFound = True
            # add to list of paths
            paths.append(p)
            # accumulate exec time
            execTime = execTime + pTime
            if execTime > timeout: return paths
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
        start = time.time()
        execTime = 0
        path = [a]
        currentNode = a
        # # recurse over neighbors to get full path, max iterations is shortest path
        # while currentNode != b:
        #     lenCurrToN = snap.TIntH()
        #     snap.GetShortPath(self.g, currentNode, lenCurrToN, True, 1000)
        #     # sort shortest path ascending
        #     lenCurrToN.SortByDat()
        #     # recurse until a new node is found
        #     nextNodeFound = False
        #     for n in lenCurrToN:
        #         isValidNodeInList = (n != currentNode
        #                              and n not in doNotUseNodes)
        #         # break on direct path found, cannot put dest in doNotUseNodes
        #         isNotAlreadyFoundDirectPath = (directPathFound and path == [a]
        #                                        and n == b)
        #         # node found is both are true
        #         if (isValidNodeInList and isValidNodeInList):
        #             path.append(n)
        #             currentNode = n
        #             nextNodeFound = True
        #         else:
        #             continue
        #         # break if node found
        #         break
        #     # new node not found, breaking conditions
        #     if nextNodeFound is False: return ([], execTime)
        #     # prepare to iterate again
        #     lenCurrToN.Clr()
        # return (path, execTime)

        while currentNode != b:
            nextNode = None
            shortest = sys.maxint
            # find shortest of neighbors
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

    def common(self, n1, n2, timeout=3000):
        """
            takes page rank of subgraph of network for two nodes,
            returns array of relveant nodes, sorted by relevance
        """
        # add edges for each node in short paths
        # paths = self.shortestPath(n1, n2, timeout=timeout)
        # paths.extend(self.shortestPath(n2, n1, timeout=timeout))
        # # flatten path into nodes
        # nodes = [item for sublist in paths for item in sublist]
        # # expand to neighbors for bigger graph
        # for n in nodes:
        #     edges = self.g.GetNI(n).GetOutEdges()
        #     print edges

        # # snap.GetSubGraph(self.g, snap.TIntV.GetV(0,1,2,3,4))
        # print nodes

        return []

    def g(self):
        return self.g
