#!/bin/bash

# Get NUM_THREADS from command line.
if [ $# -eq 1 ]; then
    NUM_THREADS=$1
else
    echo "Usage: $0 <num_threads>"
fi

cd pcaps

for i in $(seq 1 $NUM_THREADS); do
    NETWORK_NAME=gluetun$i
    commander_port=$((4444 + $i))

    ./mass.sh -i $NETWORK_NAME -h localhost -p $commander_port &

    sleep 5
done