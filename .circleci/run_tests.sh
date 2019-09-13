#!/bin/bash


echo "CIRCLE_TAG=$CIRCLE_TAG"

export GRAPH_SAVE_PATH="$(pwd)/out/test1.graph"
coverage run -m pytest
