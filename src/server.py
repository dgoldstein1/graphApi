from flask import Flask, request, jsonify, send_file, redirect
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
	pass

@app.route('/shortestPath')
def shortestPath():
	"""gets shortest path between two nodes"""
	pass


if __name__ == '__main__':
	app.run()