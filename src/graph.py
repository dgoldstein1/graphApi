import snap
import logging
import signal
import random
import datetime
import os
import random
import sys
import time
import copy


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
                .format(e, path))

    def g(self):
        return self.g

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

    def shortestPath(self, a, b, n=1, timeout=3000, directed=False):
        """
            - gets shortest path(s) between two nodes
            - return array of nodes or failure
        """
        shortestPathLen = snap.GetShortPath(self.g, a, b, True)
        # make sure that there is a path before going on
        if (shortestPathLen == -1):
            raise IndexError("No such path from {} to {}".format(a, b))

        paths = []
        dpf = False
        execTime = 0
        g = snap.GetBfsTree(self.g, a, True, False)
        for x in range(0, n):
            p, pTime = ([], 0)
            if directed:
                (p, pTime) = self.shortestPathDir(a, b, dpf,
                                                  timeout - execTime, g)
            else:
                (p, pTime) = self.shortestPathUndir(a, b, dpf,
                                                    timeout - execTime, g)
            # stopping condition, no more paths
            if p == []: return paths
            # direct path found. Edge condition since do
            # not add destination node to excluded node
            if len(p) == 2: dpf = True
            # add to list of paths
            paths.append(copy.copy(p))
            # accumulate exec time
            execTime = execTime + pTime
            if (execTime * 1000) > timeout: return paths
            # removes nodes currently in use in path
            [g.DelNode(n) for n in p[1:len(p) - 1]]
        return paths

    def _hasStoppingCondition(self, a, b, shortestDist, dpf, i):
        """
        helper for determing stopping condition. If there is one, returns
        expected path at that point
        returns (Bool,path)
        """
        if shortestDist == -1: return (True, [])
        if shortestDist == 0: return (True, [a])
        if shortestDist == 1:
            if dpf and i == 0: return (True, [])
            return (True, [a, b])
        return (False, [])

    def shortestPathDir(self, a, b, dpf, t, g, i=0):
        """
        shortest path in directed graph
        returns (path, execution time ms)
        """
        start = time.time()
        shortestDist = snap.GetShortPath(g, a, b, True)
        # stopping conditions
        shouldStop, p = self._hasStoppingCondition(a, b, shortestDist, dpf, i)
        if shouldStop: return (p, time.time() - start)

        # get nodes at middle hop
        nodeVec = snap.TIntV()
        midDist = int(round(shortestDist / 2))
        snap.GetNodesAtHop(g, a, midDist, nodeVec, True)
        # if odd mid distance needs to be once less
        if shortestDist % 2 is not 0: midDist = midDist + 1
        for n in nodeVec:
            # check if less or middle node
            d = snap.GetShortPath(g, n, b, True)
            if d == midDist:
                # recurse from paths of middle nodes
                (aToMid, t1) = self.shortestPathDir(a, n, dpf, t, g, i + 1)
                (midToB, t2) = self.shortestPathDir(n, b, dpf, t, g, i + 1)
                aToMid.extend(midToB[1:])
                return (aToMid, (time.time() - start) + t1 + t2)

        # unreachable code
        raise IndexError(
            "ERROR: unreachable code: a={}b={}dist={}midDist={}".format(
                a, b, shortestDist, midDist))

    def shortestPathUndir(self, a, b, dpf, t, g, i=0):
        """
        finds shortest path between two new nodes
            a: source
            b: destination
            dpf: direct path already found?
            t: timeout
        """
        start = time.time()
        shortestDist = snap.GetShortPath(g, a, b, False)
        # stopping conditions
        # stopping conditions
        shouldStop, p = self._hasStoppingCondition(a, b, shortestDist, dpf, i)
        if shouldStop: return (p, time.time() - start)

        # get lengths from n->b and n->a
        lentoB, lentoA = snap.TIntH(), snap.TIntH()
        snap.GetShortPath(g, b, lentoB, False, shortestDist * 5)
        snap.GetShortPath(g, a, lentoA, False, shortestDist * 5)
        lentoB.SortByDat()
        # find shortest middle between the two
        s = sys.maxint
        middleNode = None
        # stopping condition: no nodes left
        if len(lentoB) == 0 or len(lentoA) == 0:
            return ([], time.time() - start)
        for n in lentoB:
            if not lentoB.IsKey(n) or not lentoA.IsKey(n): continue
            if lentoB[n] < 1 or lentoA[n] < 1: continue
            l = lentoB[n] + lentoA[n]
            if l < s:
                s = l
                middleNode = n
        if middleNode is None: return ([], time.time() - start)
        # else recurse from paths of middle nodes
        (aToMid, t1) = self.shortestPathUndir(a, middleNode, dpf, t, g, i + 1)
        (midToB, t2) = self.shortestPathUndir(middleNode, b, dpf, t, g, i + 1)
        aToMid.extend(midToB[1:])
        return (aToMid, (time.time() - start) + t1 + t2)

    def nodeCentrality(self, n):
        """
            gets centrality measures for individual node returns as dict
        """
        # get degree centrality
        nNodes = float(self.g.GetNodes())
        nEdges = float(self.g.GetNI(n).GetOutDeg())
        return {
            "degree": nEdges / (nNodes - 1),
            "closeness": snap.GetClosenessCentr(self.g, n, True, True),
            "eccentricity": snap.GetNodeEcc(self.g, n, True),
        }

    def centrality(self, nResults=10):
        """
            returns top nodes for each type of centrality
                - if slow is true, will run through each node in
                  graph, getting highest nodeCentrality()
        """
        # betweeness
        nodes = snap.TIntFltH()
        edges = snap.TIntPrFltH()
        snap.GetBetweennessCentr(self.g, nodes, edges, 4, True)
        betweenessNodes = self._extractTopN(nodes, n=nResults)
        betweenessEdges = self._extractTopN(edges, n=nResults, isTPair=True)
        # page rank
        nodes = snap.TIntFltH()
        snap.GetPageRank(self.g, nodes, 0.85, 1e-4, 30)
        pageRank = self._extractTopN(nodes, n=nResults)

        return {
            'betweenessNodes': betweenessNodes,
            'betweenessEdges': betweenessEdges,
            'pageRank': pageRank,
        }

    def _extractTopN(self, tHash, n=10, asc=False, isTPair=False):
        """
        utility for extracting top n results from a hash table in format {nodeId : value}
        ascending: lowest values first?
        """
        tHash.SortByDat(asc)
        i = 0
        r = []
        for j in tHash:
            if i == n - 1: return r
            toAdd = {'val': tHash[j]}
            if isTPair:
                toAdd['start'] = j.Val1()
                toAdd['end'] = j.Val2()
            else:
                toAdd['id'] = j
            r.append(toAdd)
            i = i + 1
        return r
