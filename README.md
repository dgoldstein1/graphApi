# graphApi
RESTful graph API to handle analysis on billions of nodes through the Stanford Network Analysis Platform (SNAP)


## Setup

- Set the python version to `2.7`
- Install the (Snap python package manually)[https://snap.stanford.edu/snappy/index.html#download]
- Install [Flask v1](http://flask.pocoo.org/docs/1.0/installation/)
- Install dependencies
```sh
pip install -r requirements.txt
```

## Test

Run tests to make sure everything is configured correctly.
```sh
python -m unittest discover src "*_test.py"
```

See code coverage:
```sh
coverage run src/**/*.py
coverage html src/**/*.py
# open up the file htmlcov/index.html in a browser
```

## Run

```sh
export FLASK_APP=src/server.py
flask run
```

## Config

See [config](config.cfg) for a complete example of configuration settings. Relative paths start from the `src` directory.

Var | Meaning
--- | --- |
`METRICS_PORT` | Port where metrics are running on server
`GRAPH_SAVE_PATH`  | Name of file to load in and save graph. Relative path from root directory.
`SHORTEST_PATH_TIMEOUT` | Maximum time allowed in finding shortest path between two nodes.
## Code Formatting

```sh
pip install yapf
yapf -ri src/**/*.py
```

## Generating New Documentation

```sh
pip install PyYAML
python api/swagger-yaml-to-html.py < api/swagger.yml > api/index.html
```

