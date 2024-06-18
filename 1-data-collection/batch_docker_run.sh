#!/bin/bash

# Get NUM_THREADS from command line.
if [ $# -eq 1 ]; then
    NUM_THREADS=$1
else
    echo "Usage: $0 <num_threads>"
    exit 1
fi

source ./.env

cd pcaps

for i in $(seq 1 $NUM_THREADS); do
    NETWORK_NAME=gluetun$i

    if [ $i -le 10 ]; then
        OPENVPN_USER=$OPENVPN_USER1
        OPENVPN_PASSWORD=$OPENVPN_PASSWORD1
    else
        OPENVPN_USER=$OPENVPN_USER2
        OPENVPN_PASSWORD=$OPENVPN_PASSWORD2
    fi

    # Check if the network exists
    if ! docker network ls | grep -q $NETWORK_NAME; then
        echo "Network $NETWORK_NAME does not exist. Creating..."
        docker network create \
            --driver bridge \
            --opt com.docker.network.bridge.name=$NETWORK_NAME \
            $NETWORK_NAME
        echo "Network $NETWORK_NAME created."
    else
        echo "Network $NETWORK_NAME already exists."
    fi

    commander_port=$((4444 + $i))
    webui_port=$((7900 + $i))

    # Check if the gluetun container exists
    if [ $(docker ps -a --format '{{.Names}}' | grep -w "gluetun$i") ]; then
        echo "Container gluetun$i already exists. Starting..."
        docker start gluetun$i
    else
        echo "Container gluetun$i does not exist. Creating..."
        docker run -d \
            --dns=1.1.1.1 \
            --cap-add=NET_ADMIN \
            --name=gluetun$i \
            --device=/dev/net/tun:/dev/net/tun \
            -v ./gluetun-data/gluetun$i:/gluetun \
            -e VPN_SERVICE_PROVIDER=protonvpn \
            -e VPN_TYPE=openvpn \
            -e OPENVPN_USER=$OPENVPN_USER \
            -e OPENVPN_PASSWORD=$OPENVPN_PASSWORD \
            -e SERVER_COUNTRIES=Japan \
            -e OPENVPN_PROTOCOL=udp \
            -e TZ=Asia/Seoul \
            --network=$NETWORK_NAME \
            -p $commander_port:4444 \
            -p $webui_port:7900 \
            --restart unless-stopped \
            ghcr.io/qdm12/gluetun:latest
    fi

done

for i in $(seq 1 $NUM_THREADS); do
    # Check if the firefox container exists
    if [ $(docker ps -a --format '{{.Names}}' | grep -w "firefox$i") ]; then
        echo "Container firefox$i already exists. Starting..."
        docker start firefox$i
    else
        echo "Container firefox$i does not exist. Creating..."
        docker run -d \
            --name=firefox$i \
            --network=container:gluetun$i \
            --shm-size=4g \
            --restart unless-stopped \
            -e SE_VNC_PASSWORD=$SE_VNC_PASSWORD \
            selenium/standalone-firefox:latest
    fi
done
