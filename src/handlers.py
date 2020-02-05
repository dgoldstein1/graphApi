import server
import requests
import re
from flask import send_file, request, jsonify
import logging


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
        return server.errOut(422, "The query parameter 'node' is required")
    try:
        node = int(node)
        if node > server.MAX_INT:
            return server.errOut(
                422,
                "Integers over {} are not supported".format(server.MAX_INT))
    except ValueError:
        return server.errOut(
            422, "Node '{}' could not be converted to an integer".format(node))

    # add in nodes
    body = request.get_json()
    if (isinstance(body["neighbors"], list) == False):
        return server.errOut(
            422, "'neighbors' must be an array but got '{}'".format(
                body["neighbors"]))

    # assert that each neighbor is valid int
    neighborsToAdd = []
    for n in body["neighbors"]:
        try:
            nodeInt = int(n)
            if nodeInt > server.MAX_INT:
                return server.errOut(
                    422,
                    "Integers over {} are not supported. Passed {}".format(
                        server.MAX_INT, nodeInt))
            # else, is valid int
            neighborsToAdd.append(nodeInt)
        except ValueError:
            return server.errOut(
                422,
                "Node '{}' could not be converted to an integer".format(n))

    # get or add nodes
    err = None
    newNodes = []
    try:
        newNodes = server.g.addNeighbors(node, neighborsToAdd)
    except RuntimeError as e:
        err = server.errOut(
            404, "Node '{}' was not found or does not exist".format(node))

    if err is not None:
        return err
    return jsonify({"neighborsAdded": newNodes})
