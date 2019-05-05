from flask import Flask, request, jsonify, send_file, redirect, Response
from flask_restful import Resource, Api
from json import dumps
from flask_prometheus import monitor 
from threading import Lock
import graph
import time

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
	if (node is None):
		return _returnError(422, "The query parameter 'node' is required")
	return "test"

@app.route('/shortestPath')
def shortestPath():
	"""gets shortest path between two nodes"""
	pass

def _returnError(code, error):
	return dumps({'code':code, 'error':error}), code, {'ContentType':'application/json'}

if __name__ == '__main__':
	app.run(debug=True)