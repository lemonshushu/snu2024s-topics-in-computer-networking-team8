#!/bin/bash

# Stop and remove all containers named gluetun*
for container in $(docker ps -a --format '{{.Names}}' | grep -E '^gluetun[0-9]*$'); do
    echo "Stopping and removing container $container..."
    docker stop $container
    docker rm $container
done

# Stop and remove all containers named firefox*
for container in $(docker ps -a --format '{{.Names}}' | grep -E '^firefox[0-9]*$'); do
    echo "Stopping and removing container $container..."
    docker stop $container
    docker rm $container
done

echo "All specified containers have been stopped and removed."
