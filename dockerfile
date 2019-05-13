from python:2.7

# install snap
run wget https://snap.stanford.edu/snappy/release/snap-4.1.0-4.1-centos6.5-x64-py2.6.tar.gz -o snap.tar.gz
run tar zxvf snap.tar.gz
run cd snap
run python setup.py install

# install dependencies
run pip install -r requirements.txt

# configure app
ENV FLASK_APP src/server.py
ENV PORT 5000

# run app
CMD flask run