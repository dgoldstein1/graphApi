from flask import Flask, request, jsonify, send_file, redirect, Response
from flask_restful import Resource, Api
from json import dumps
from flask_prometheus import monitor
import graph
import time
import logging
import json
import os

# flask setup
app = Flask(__name__)
app.config.from_pyfile('../config.cfg')
monitor(app, port=app.config["METRICS_PORT"])
SHORTEST_PATH_TIMEOUT = int(app.config["SHORTEST_PATH_TIMEOUT"])
MAX_INT = 999999999.0
# graph setup
file = "{}/{}".format(os.getcwd(),app.config["GRAPH_SAVE_PATH"])
g = graph.Graph(file)

#########
## api ##
#########


@app.route('/metrics')
def serveMetrics():
    """server prometheus metrics"""
    return redirect("{}:{}".format(app.config["HOST"],
                                   app.config["METRICS_PORT"]))


@app.route('/')
def serveDocs():
    """Serves docs to browser"""
    return send_file("../api/index.html")


@app.route('/save')
def save():
    """saves graph and serves as file stream"""
    return send_file(g.save(), as_attachment=True)


@app.route('/edges', methods=['POST'])
def edges():
    node = request.args.get("node")
    # parse arguments
    if (node is None):
        return _errOut(422, "The query parameter 'node' is required")
    try:
        node = int(node)
        if node > MAX_INT:
            return _errOut(
                422, "Integers over {} are not supported".format(MAX_INT))
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
            if nodeInt > MAX_INT:
                return _errOut(
                    422,
                    "Integers over {} are not supported. Passed {}".format(
                        MAX_INT, nodeInt))
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
        newNodes = g.addNeighbors(node, neighborsToAdd)
    except RuntimeError as e:
        err = _errOut(404,
                      "Node '{}' was not found or does not exist".format(node))

    if err is not None:
        return err
    return jsonify({"neighborsAdded": newNodes})


@app.route('/neighbors')
def neighbors():
    """adds neighbor nodes to graph. Returns {error: on error}"""
    node = request.args.get("node")
    # parse arguments
    if (node is None):
        return _errOut(422, "The query parameter 'node' is required")

    try:
        node = int(node)
        if node > MAX_INT:
            return _errOut(
                422, "Integers over {} are not supported".format(MAX_INT))
    except ValueError:
        return _errOut(
            422, "Node '{}' could not be converted to an integer".format(node))

    neighborsToAdd = []

    # get or add nodes
    err = None
    try:
        neighbors = g.getNeighbors(node)
    except RuntimeError as e:
        err = _errOut(404,
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
        return _errOut(422,
                       "The query parameters 'start' and 'end' are required")
    try:
        start = int(start)
        end = int(end)
        if start > MAX_INT or end > MAX_INT:
            return _errOut(
                422, "Integers over {} are not supported".format(MAX_INT))
    except ValueError:
        return _errOut(
            422,
            "Nodes '{}' and '{}' could not be converted to integers".format(
                start, end))

    # get shortest path
    err = None
    try:
        path = g.shortestPath(start, end, SHORTEST_PATH_TIMEOUT)
    except IndexError as e:
        err = _errOut(500, e.message)
    if err is not None:
        return err
    return jsonify(path)


def _errOut(code, error):
    logging.error(error)
    return jsonify(code=code, error=error), code


if __name__ == '__main__':
    app.run(debug=True)
