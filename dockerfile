from python:2.7
workdir /usr/graphApi

# install snap
run wget https://snap.stanford.edu/snappy/release/snap-4.1.0-4.1-centos6.5-x64-py2.6.tar.gz
run tar xvf snap-4.1.0-4.1-centos6.5-x64-py2.6.tar.gz 
run cd snap-4.1.0-4.1-centos6.5-x64-py2.6 && python setup.py install
# copy app and copy dependencies
copy . /usr/graphApi
run pwd && ls
run pip install -r requirements.txt

# generate documentation
run python api/swagger-yaml-to-html.py < api/swagger.yml > api/index.html

# configure app
env FLASK_APP src/server.py
env PORT 5000

# run app
cmd flask run
