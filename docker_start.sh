#!/bin/sh

# poll save endpoint
save_graph_poll() {
  ENDPOINT="http://localhost:5000/save"
  while true
  do
    sleep $GRAPH_SAVE_INTERVAL
    curl -s $ENDPOINT | wc -c
  done
}

# start cron job
save_graph_poll &

# start flask app
printenv
echo "/data : "
ls -lh /data
flask run --host=0.0.0.0
