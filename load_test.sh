#!/bin/bash

# makes increasing number of concurrent requests
# to see when the server will break

for (( i = 3; i < 6; i++ )); do
	echo "making $((i**10)) requests"
	for (( j = 0; j < $((i ** 10)); j++ )); do
		curl -s -d '{"neighbors" : [1,5,3,4,6,3,3,6,2,2,5,34,26,235,2]}'  \
		-H "Content-Type: application/json"  \
		-X POST "http://localhost:5000/edges?node=$RANDOM" > /dev/null & 
	done
	echo "sleeping for $((i)) seconds"
	sleep $((i * 10))
done