from flask import Flask, request, jsonify, send_file, redirect, Response
from flask_restful import Resource, Api
import requests
from flask_prometheus import monitor
import graph
import handlers
import os

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
app.add_url_rule('/edges', "add edges", handlers.postEdges, methods=["POST"])
app.add_url_rule("/neighbors", "get neighbors", handlers.getNeighbors)
app.add_url_rule("/shortestPath", "get shortest path", handlers.shortestPath)
# docs
app.add_url_rule('/', "swagger docs", handlers.serveDocs)
# metrics
app.add_url_rule('/metrics', 'prometheus metrics', handlers.serveMetrics)
app.add_url_rule('/info', 'SNAP graph info', handlers.info)
# configuration
app.add_url_rule('/save', 'export graph to file', handlers.save)

if __name__ == '__main__':
    app.run(debug=True)
