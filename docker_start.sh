#!/bin/sh

# poll save endpoint
save_graph_poll() {
  ENDPOINT="http://localhost:5000/save"
  printenv
  while true
  do
    curl -s -o temp.graph $ENDPOINT
    sleep $GRAPH_SAVE_INTERVAL
  done
}

# start cron job
save_graph_poll &

# start flask app
flask run --host=0.0.0.0
