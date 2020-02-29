import server
import requests
from flask import send_file, request, jsonify
import logging


def serveMetrics():
    """serve prometheus metrics"""
    # get prom metrics
    localMetricsUrl = "{}:{}".format(server.app.config["METRICS_HOST"],
                                     server.app.config["METRICS_PORT"])
    metrics = requests.get(localMetricsUrl).content
    info = server.g.info()
    # add in as prom metric
    metrics += """
# HELP Number of nodes
# TYPE number_of_nodes counter
number_of_nodes {}
# HELP Number of edges
# TYPE number_of_edges counter
number_of_edges {}
average_degree {}
    """.format(info['nNodes'], info['nEdges'], info['avgDegree'])
    return metrics


def serveDocs():
    """Serves docs to browser"""
    return send_file("../api/index.html")


def info():
    """renders graph info to browser"""
    return jsonify(server.g.info())


def save():
    """saves graph and serves as file stream"""
    return send_file(server.g.save(), as_attachment=True)


# CORE API
def postEdges():
    # deconstruct validated arrays
    node = str(request.args.get("node"))
    neighborsToAdd = [str(n) for n in request.get_json().get("neighbors")]

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
    validatedNodes = validateInts(
        [request.args.get("limit") or server.DEFAULT_LIMIT])
    if validatedNodes.get('error') is not None:
        return _errOut(422, validatedNodes.get('error'))
    [limit] = validatedNodes.get('validInts')
    node = str(request.args.get("node"))
    try:
        neighbors = server.g.getNeighbors(node, limit)
    except RuntimeError:
        return _errOut(
            404, "Node '{}' was not found or does not exist".format(node))
    return jsonify(neighbors)


def shortestPath():
    """gets shortest path between two nodes"""
    validatedNodes = validateInts([
        request.args.get("n") or 1,
        request.args.get("timeout") or 3000,
    ])
    if validatedNodes.get('error') is not None:
        return _errOut(422, validatedNodes.get('error'))
    [n, timeout] = validatedNodes.get('validInts')
    start = str(request.args.get("start"))
    end = str(request.args.get("end"))

    # get shortest path
    try:
        path = server.g.shortestPath(
            start,
            end,
            n,
            timeout,
            request.args.get("directed") == "true",
        )
    except IndexError as e:
        # no such path
        return _errOut(500, str(e))
    except RuntimeError as e:
        # nodes do not exist
        return _errOut(500,
                       "Could not find given start and end values: " + str(e))
    return jsonify(path)


def centrality():
    resp = {}
    try:
        for n in request.get_json():
            resp[n] = server.g.nodeCentrality(str(n))
    except TypeError as e:
        return _errOut(500, str(e))
    return jsonify(resp)


def top():
    r = validateInts([request.args.get("n") or 10])
    if r.get("error") is not None:
        return _errOut(422, r.get("error"))
    [n] = r.get('validInts')
    return jsonify(server.g.centrality(n))


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
