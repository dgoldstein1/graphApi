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
    validatedNodes = validateInts([request.args.get("node")])
    validatedNeighbors = validateInts(request.get_json().get("neighbors"))
    error = validatedNodes.get('error') or validatedNeighbors.get('error')
    if error is not None:
        return _errOut(422, error)

    # deconstruct validated arrays
    [node] = validatedNodes.get('validInts')
    neighborsToAdd = validatedNeighbors.get('validInts')

    # get or add nodes
    newNodes = []
    try:
        newNodes = server.g.addNeighbors(node, neighborsToAdd)
    except RuntimeError:
        return _errOut(
            404, "Node '{}' was not found or does not exist".format(node))
    return jsonify({"neighborsAdded": newNodes})


def getNeighbors():
    """adds neighbor nodes to graph. Returns {error: on error}"""
    validatedNodes = validateInts([
        request.args.get("node"),
        request.args.get("limit") or server.DEFAULT_LIMIT
    ])
    if validatedNodes.get('error') is not None:
        return _errOut(422, validatedNodes.get('error'))
    [node, limit] = validatedNodes.get('validInts')
    try:
        neighbors = server.g.getNeighbors(node, limit)
    except RuntimeError:
        return _errOut(
            404, "Node '{}' was not found or does not exist".format(node))
    return jsonify(neighbors)


def shortestPath():
    """gets shortest path between two nodes"""
    validatedNodes = validateInts(
        [request.args.get("start"),
         request.args.get("end")])
    if validatedNodes.get('error') is not None:
        return _errOut(422, validatedNodes.get('error'))
    [start, end] = validatedNodes.get('validInts')
    # get shortest path
    try:
        path = server.g.shortestPath(start, end)
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


def validateInts(n):
    """
    Validates integer.
        Takes in array of anything (usually strings)
        returns {error : string, validInts : array int}
    """
    if type(n) is not list:
        return {'error': 'internal error: {} is not of type "list"'.format(n)}
    # validate each int in list
    validInts = []
    for i in range(0, len(n)):
        try:
            validInts.append(int(n[i]))
        except (TypeError, ValueError):
            return {'error': 'could not convert {} to an integer'.format(n)}
        ## assert in range
        if validInts[i] > server.MAX_INT or validInts[i] < 0:
            return {
                'error':
                '{} is not in range 0 - {}'.format(validInts[i],
                                                   server.MAX_INT)
            }
    return {'validInts': validInts}


def _errOut(code, error):
    logging.error(error)
    return jsonify(code=code, error=error), code