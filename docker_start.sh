#!/bin/sh

# poll save endpoint
save_graph_poll() {
  ENDPOINT="http://localhost:5000/save"
  TMP_STORE="/tmp/current_graph_data"
  printenv
  while true
  do
    sleep $GRAPH_SAVE_INTERVAL
    curl -s -o $TMP_STORE $ENDPOINT
    # mv $TMP_STORE $GRAPH_DATA_PATH/
  done
}

# start cron job
save_graph_poll &

# start flask app
flask run --host=0.0.0.0
