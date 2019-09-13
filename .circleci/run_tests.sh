#!/bin/bash
echo "CIRCLE_BRANCH=$CIRCLE_BRANCH"

export GRAPH_SAVE_PATH="$(pwd)/out/test1.graph"


coverage run -m pytest
if [[ $? != 0 ]]; then
    echo "Tests have failed"
    exit 1
fi


if [[ "$CIRCLE_BRANCH" == "master" ]]; then
  export CC_TEST_REPORTER_ID=a16ce4a8d9e5d0398c6cbf335aafe3438b374e3cb0c1274a3eb3701cb8689c14
  curl -L https://codeclimate.com/downloads/test-reporter/test-reporter-latest-linux-amd64 > ./cc-test-reporter
  chmod +x ./cc-test-reporter
  coverage xml
  ./cc-test-reporter format-coverage coverage.xml -t coverage.py
  ./cc-test-reporter upload-coverage
fi
