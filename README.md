# graphApi
RESTful graph API written in C++ to handle billions of nodes through the Stanford Network Analysis Platform (SNAP)


## Setup

- Install or set the python version to `2.7`
- Install the (Snap python package manually)[https://snap.stanford.edu/snappy/index.html#download]
- Install dependencies
```sh
pip install -r requirements.txt
```

- Run tests to make sure everything is configured correctly
```sh
python -m unittest discover src "*_test.py"
```

## Run

```sh
export FLASK_APP=src/server.py
flask run
```


## Generating New Documentation

```sh
pip install PyYAML
python api/swagger-yaml-to-html.py < api/swagger.yml > api/index.html
```
