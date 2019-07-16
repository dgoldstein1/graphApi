#!/bin/bash
while true; do

inotifywait -e modify,create,delete -r ./ && \
	clear && \
	python -m unittest discover src "*_test.py"
done
