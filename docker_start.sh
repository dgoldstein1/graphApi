#!/bin/sh

# copy mounted data if it exist
mkdir -p $GRAPH_DATA_PATH
cp -r $GRAPH_DATA_PATH/* .

# poll save endpoint
save_graph_poll() {
  ENDPOINT="http://localhost:5000/save"
  printenv
  while true
  do
    sleep $GRAPH_SAVE_INTERVAL
    curl -s -o /tmp/current_graph_data $ENDPOINT
    mv /tmp/current_graph_data $GRAPH_DATA_PATH
  done
}

# start cron job
save_graph_poll &

# start flask app
flask run --host=0.0.0.0
