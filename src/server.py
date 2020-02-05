from flask import Flask, request, jsonify, send_file, redirect, Response
from flask_restful import Resource, Api
import requests
from json import dumps
from flask_prometheus import monitor
import graph
import handlers
import time
import logging
import json
import os
import re
import sys

# flask setup
app = Flask(__name__)
app.config.from_pyfile('../config.cfg')
monitor(app, port=app.config["METRICS_PORT"])
SHORTEST_PATH_TIMEOUT = int(app.config["SHORTEST_PATH_TIMEOUT"])
MAX_INT = 999999999.0
DEFAULT_LIMIT = 1000
# graph setup
file = os.environ['GRAPH_SAVE_PATH']
g = graph.Graph(file)

#########
## api ##
#########

# core functions
app.add_url_rule('/edges',
                 "add edges to the graph",
                 handlers.postEdges,
                 methods=["POST"])
# docs
app.add_url_rule('/', "swagger docs", handlers.serveDocs)
# metrics
app.add_url_rule('/metrics', 'prometheus metrics', handlers.serveMetrics)
app.add_url_rule('/info', 'SNAP graph info', handlers.info)
# configuration
app.add_url_rule('/save', 'export graph to file', handlers.save)


@app.route('/neighbors')
def neighbors():
    """adds neighbor nodes to graph. Returns {error: on error}"""
    node = request.args.get("node")
    # parse arguments
    if (node is None):
        return errOut(422, "The query parameter 'node' is required")

    try:
        node = int(node)
        if node > MAX_INT:
            return errOut(422,
                          "Integers over {} are not supported".format(MAX_INT))
    except ValueError:
        return errOut(
            422, "Node '{}' could not be converted to an integer".format(node))

    neighborsToAdd = []
    # parse limit
    limit = request.args.get("limit")
    if limit is not None:
        try:
            limit = int(limit)
        except ValueError as e:
            return errOut(500, "Could not parse limit {}: {}".format(limit, e))
    # no limit passed, set default
    else:
        limit = DEFAULT_LIMIT
    # get or add nodes
    err = None
    try:
        neighbors = g.getNeighbors(node, limit)
    except RuntimeError as e:
        err = errOut(404,
                     "Node '{}' was not found or does not exist".format(node))

    if err is not None:
        return err
    return jsonify(neighbors)


@app.route('/shortestPath')
def shortestPath():
    """gets shortest path between two nodes"""
    start = request.args.get("start")
    end = request.args.get("end")
    # parse arguments
    if (start is None or end is None):
        return errOut(422,
                      "The query parameters 'start' and 'end' are required")
    try:
        start = int(start)
        end = int(end)
        if start > MAX_INT or end > MAX_INT:
            return errOut(422,
                          "Integers over {} are not supported".format(MAX_INT))
    except ValueError:
        return errOut(
            422,
            "Nodes '{}' and '{}' could not be converted to integers".format(
                start, end))

    # get shortest path
    try:
        path = g.shortestPath(start, end, SHORTEST_PATH_TIMEOUT)
    except IndexError as e:
        # no such path
        return errOut(500, e.message)
    except RuntimeError as e:
        # nodes do not exist
        return errOut(
            500, "Could not find given start and end values: " + e.message)
    except:
        logging.error(sys.exc_info()[0])
        return errOut(500, "Unexpected error occured, see logs")
    return jsonify(path)


def errOut(code, error):
    logging.error(error)
    return jsonify(code=code, error=error), code


if __name__ == '__main__':
    app.run(debug=True)
