from flask import Flask, request, jsonify, send_file, redirect
from flask_restful import Resource, Api
from json import dumps
from flask_prometheus import monitor 

# flask setup
app = Flask(__name__)
app.config.from_pyfile('../config.cfg')
api = Api(app)
monitor(app, port=app.config["METRICS_PORT"])

class ServeDocs(Resource):
	"""Serves docs to browser"""
	def get(self):
		return send_file("../api/index.html")

class ServeMetrics(Resource):
	"""server prometheus metrics"""
	def get(self):
		return redirect("http://127.0.0.1:{}".format(app.config["METRICS_PORT"]))

class Neighbors(Resource):
	"""adds neighbor nodes to graph. Returns {error: on error}"""
	def get(self):
		pass

	def post(self):
		pass

class ShortestPath(Resource):
	"""gets shortest path between two nodes"""
	def get(self, a, b):
		pass

class SaveAndDownload(Resource):
	"""saves graph and serves as file stream"""
	def get(self):
		return send_file(app.config["GRAPH_SAVE_PATH"], as_attachment=True)
    
# monitoring
api.add_resource(ServeDocs, '/')
api.add_resource(ServeMetrics, '/metrics')
# core api
api.add_resource(SaveAndDownload, "/save")
api.add_resource(Neighbors, '/neighbors')
api.add_resource(ShortestPath, '/shortestPath')

if __name__ == '__main__':
    app.run()