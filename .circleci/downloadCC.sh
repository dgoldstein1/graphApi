#!/bin/sh

# Script that checks if the cc-test-reporter binary exists
# and downloads it and sets the executable bit if it doesn't
# See https://docs.codeclimate.com/docs/configuring-test-coverage#section-locations-of-pre-built-binaries
if [ ! -f cc-test-reporter ]; then
	curl -L https://codeclimate.com/downloads/test-reporter/test-reporter-latest-linux-amd64 >./cc-test-reporter
	chmod +x ./cc-test-reporter
fi
