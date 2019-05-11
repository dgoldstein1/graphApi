from flask import Flask, request, jsonify, send_file, redirect, Response
from flask_restful import Resource, Api
from json import dumps
from flask_prometheus import monitor
from threading import Lock
import graph
import time
import logging
import json

# flask setup
app = Flask(__name__)
app.config.from_pyfile('../config.cfg')
monitor(app, port=app.config["METRICS_PORT"])
# graph setup
g = graph.Graph(app.config["GRAPH_SAVE_PATH"])
lock = Lock()

#########
## api ##
#########


@app.route('/metrics')
def serveMetrics():
    """server prometheus metrics"""
    return redirect("http://127.0.0.1:{}".format(app.config["METRICS_PORT"]))


@app.route('/')
def serveDocs():
    """Serves docs to browser"""
    return send_file("../api/index.html")


@app.route('/save')
def save():
    """saves graph and serves as file stream"""
    return send_file(app.config["GRAPH_SAVE_PATH"], as_attachment=True)


@app.route('/neighbors', methods=['POST', 'GET'])
def neighbors():
    """adds neighbor nodes to graph. Returns {error: on error}"""
    node = request.args.get("node")
    # parse arguments
    if (node is None):
        return _errOut(422, "The query parameter 'node' is required")

    try:
        node = int(node)
    except ValueError:
        return _errOut(
            422, "Node '{}' could not be converted to an integer".format(node))

    
    neighborsToAdd = []
    if (request.method == "POST"):
        body = request.get_json()
    	if (isinstance(body["neighbors"], list) == False):
			return _errOut(422, "'neighbors' must be an array but got '{}'".format(body["neighbors"]))    		
    	# assert that each neighbor is valid int
    	for n in body["neighbors"]:
			try:
			    neighborsToAdd.append(int(n))
			except ValueError:
			    return _errOut(
			        422, "Node '{}' could not be converted to an integer".format(n))


    # get or add nodes
	lock.acquire()
	err = None
    try:
    	neighbors = g.getNeighbors(node) if request.method == "GET" else g.addNeighbors(node, neighborsToAdd)
    except RuntimeError as e:
    	err = _errOut(500, "Node '{}' was not found or does not exist".format(node))

	lock.release()
	
	if err is not None:
		return err
	# else
    return jsonify(neighbors)


@app.route('/shortestPath')
def shortestPath():
    """gets shortest path between two nodes"""
    pass


def _errOut(code, error):
    logging.error(error)
    return jsonify(code=code, error=error), code


if __name__ == '__main__':
    app.run(debug=True)
