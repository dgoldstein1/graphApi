from python:2.7
workdir /usr/graphApi

# install snap
run wget https://snap.stanford.edu/snappy/release/snap-4.1.0-4.1-centos6.5-x64-py2.6.tar.gz
run tar xvf snap-4.1.0-4.1-centos6.5-x64-py2.6.tar.gz
run cd snap-4.1.0-4.1-centos6.5-x64-py2.6 && python setup.py install
# copy app and copy dependencies
copy . /usr/graphApi

run pip install -r requirements.txt
run pip install gunicorn

# generate documentation
run python api/swagger-yaml-to-html.py < api/swagger.yml > api/index.html

# configure app
env FLASK_APP src/server.py
run > config.cfg
run echo 'METRICS_PORT = 8001' >> config.cfg
run echo 'SHORTEST_PATH_TIMEOUT = 3000' >> config.cfg
run echo 'GRAPH_SAVE_PATH = "./current_graph_data"' >> config.cfg
run echo 'HOST = "0.0.0.0"' >> config.cfg
run echo 'TESTING = "False"' >> config.cfg
run echo 'DEBUG = True' >> config.cfg
run cat config.cfg

# run app
CMD cd src && gunicorn --bind 127.0.0.1:5000 server:app
