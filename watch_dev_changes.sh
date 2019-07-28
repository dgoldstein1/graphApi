#!/bin/bash
while true; do

inotifywait -e modify,create,delete -r ./ && \
	clear && \
	yapf -ri ./**/*.py && \
	python -m unittest discover src "*_test.py"
done
