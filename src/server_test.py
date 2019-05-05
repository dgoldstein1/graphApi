import os
import unittest
 
from server import app
from HTMLParser import HTMLParser
 
class TestServer(unittest.TestCase):
 
    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config["METRICS_PORT"] = 8001
        self.app = app.test_client()
        self.assertEqual(app.debug, False)

    def test_serve_docs(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data)
        try:
        	HTMLParser().feed(response.data)
       	except:
       		self.fail("Could not parse docs")


    def test_metrics(self):
    	# assert that it redirects
    	try:
    		response = self.app.get('/metrics', follow_redirects=True)
    	except RuntimeError as e:
    		self.assertEqual(e.message, "Following external redirects is not supported.")
 