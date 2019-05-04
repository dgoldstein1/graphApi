from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from json import dumps

app = Flask(__name__)
api = Api(app)

class ServeDocs(Resource):
	"""Serves docs to browser"""
	def get(self):
		pass

class serveMetrics(Resource):
	"""server prometheus metrics"""
	def get(self):
		pass

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
    

api.add_resource(ServeDocs, '/')
api.add_resource(Neighbors, '/neighbors')
api.add_resource(ShortestPath, '/shortestPath')

if __name__ == '__main__':
    app.run()