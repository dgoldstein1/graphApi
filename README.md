# graphApi
RESTful graph API to handle analysis on billions of nodes through the Stanford Network Analysis Platform (SNAP)

[![Maintainability](https://api.codeclimate.com/v1/badges/59f598369253217244bc/maintainability)](https://codeclimate.com/github/dgoldstein1/graphApi/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/59f598369253217244bc/test_coverage)](https://codeclimate.com/github/dgoldstein1/graphApi/test_coverage)
[![CircleCI](https://circleci.com/gh/dgoldstein1/graphApi.svg?style=svg)](https://circleci.com/gh/dgoldstein1/graphApi)

## Setup

- Set the python version to `2.7`
- Install the (Snap python package manually)[https://snap.stanford.edu/snappy/index.html#download]
- Install [Flask v1](http://flask.pocoo.org/docs/1.0/installation/)
- Install dependencies
```sh
sudo pip install pipenv

```

## Test

Run tests to make sure everything is configured correctly.
```sh
pytest
```

See code coverage:
```sh
coverage run -m pytest
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
yapf -ri ./**/*.py
```

## Generating New Documentation

```sh
pip install PyYAML
python api/swagger-yaml-to-html.py < api/swagger.yml > api/index.html
```
