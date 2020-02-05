import server
import requests
import re
from flask import send_file, request, jsonify
import logging
import sys


def serveMetrics():
    """serve prometheus metrics"""
    # get prom metrics
    localMetricsUrl = "{}:{}".format(server.app.config["METRICS_HOST"],
                                     server.app.config["METRICS_PORT"])
    metrics = requests.get(localMetricsUrl).content
    # parse out number of nodes and edges
    info = server.g.info().replace(" ", "")
    infoAsList = re.split('\n|:', info)
    nNodes = infoAsList[infoAsList.index("Nodes") + 1]
    nEdges = infoAsList[infoAsList.index("Edges") + 1]
    # add in as prom metric
    metrics += """
# HELP Number of nodes
# TYPE number_of_nodes counter
number_of_nodes {}
# HELP Number of edges
# TYPE number_of_edges counter
number_of_edges {}
    """.format(nNodes, nEdges)
    return metrics


def serveDocs():
    """Serves docs to browser"""
    return send_file("../api/index.html")


def info():
    """renders graph info to browser"""
    return server.g.info()


def save():
    """saves graph and serves as file stream"""
    return send_file(server.g.save(), as_attachment=True)


# CORE API
def postEdges():
    node = request.args.get("node")
    # parse arguments
    if (node is None):
        return _errOut(422, "The query parameter 'node' is required")
    try:
        node = int(node)
        if node > server.MAX_INT:
            return _errOut(
                422,
                "Integers over {} are not supported".format(server.MAX_INT))
    except ValueError:
        return _errOut(
            422, "Node '{}' could not be converted to an integer".format(node))

    # add in nodes
    body = request.get_json()
    if (isinstance(body["neighbors"], list) == False):
        return _errOut(
            422, "'neighbors' must be an array but got '{}'".format(
                body["neighbors"]))

    # assert that each neighbor is valid int
    neighborsToAdd = []
    for n in body["neighbors"]:
        try:
            nodeInt = int(n)
            if nodeInt > server.MAX_INT:
                return _errOut(
                    422,
                    "Integers over {} are not supported. Passed {}".format(
                        server.MAX_INT, nodeInt))
            # else, is valid int
            neighborsToAdd.append(nodeInt)
        except ValueError:
            return _errOut(
                422,
                "Node '{}' could not be converted to an integer".format(n))

    # get or add nodes
    err = None
    newNodes = []
    try:
        newNodes = server.g.addNeighbors(node, neighborsToAdd)
    except RuntimeError as e:
        err = _errOut(404,
                      "Node '{}' was not found or does not exist".format(node))

    if err is not None:
        return err
    return jsonify({"neighborsAdded": newNodes})


def getNeighbors():
    """adds neighbor nodes to graph. Returns {error: on error}"""
    node = request.args.get("node")
    # parse arguments
    if (node is None):
        return _errOut(422, "The query parameter 'node' is required")

    try:
        node = int(node)
        if node > server.MAX_INT:
            return _errOut(
                422,
                "Integers over {} are not supported".format(server.MAX_INT))
    except ValueError:
        return _errOut(
            422, "Node '{}' could not be converted to an integer".format(node))

    neighborsToAdd = []
    # parse limit
    limit = request.args.get("limit")
    if limit is not None:
        try:
            limit = int(limit)
        except ValueError as e:
            return _errOut(500,
                           "Could not parse limit {}: {}".format(limit, e))
    # no limit passed, set default
    else:
        limit = server.DEFAULT_LIMIT
    # get or add nodes
    err = None
    try:
        neighbors = server.g.getNeighbors(node, limit)
    except RuntimeError as e:
        err = _errOut(404,
                      "Node '{}' was not found or does not exist".format(node))

    if err is not None:
        return err
    return jsonify(neighbors)


def shortestPath():
    """gets shortest path between two nodes"""
    start = request.args.get("start")
    end = request.args.get("end")
    # parse arguments
    if (start is None or end is None):
        return _errOut(422,
                       "The query parameters 'start' and 'end' are required")
    try:
        start = int(start)
        end = int(end)
        if start > server.MAX_INT or end > server.MAX_INT:
            return _errOut(
                422,
                "Integers over {} are not supported".format(server.MAX_INT))
    except ValueError:
        return _errOut(
            422,
            "Nodes '{}' and '{}' could not be converted to integers".format(
                start, end))

    # get shortest path
    try:
        path = server.g.shortestPath(start, end, server.SHORTEST_PATH_TIMEOUT)
    except IndexError as e:
        # no such path
        return _errOut(500, e.message)
    except RuntimeError as e:
        # nodes do not exist
        return _errOut(
            500, "Could not find given start and end values: " + e.message)
    except:
        logging.error(sys.exc_info()[0])
        return _errOut(500, "Unexpected error occured, see logs")
    return jsonify(path)


def _errOut(code, error):
    logging.error(error)
    return jsonify(code=code, error=error), code
