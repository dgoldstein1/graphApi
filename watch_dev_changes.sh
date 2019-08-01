#!/bin/bash
while true; do

inotifywait -e modify,create,delete -r ./ && \
	clear && \
	yapf -ri ./**/*.py && \
	coverage run -m pytest
done
