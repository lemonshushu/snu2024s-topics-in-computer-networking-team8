#!/bin/bash

# Function to display usage
usage() {
    echo "Usage: $0 <network_interface> <website> <browser> <thread_id>"
    exit 1
}

# Check if the required arguments are provided
if [ "$#" -ne 4 ]; then
    usage
fi

# Arguments
NETWORK_INTERFACE=$1
WEBSITE=$2
BROWSER=$3
THREAD_ID=$4

# Create the directory if it does not already exist.
[ -d ./pcaps/$WEBSITE ] || mkdir -pv ./pcaps/$WEBSITE

# Create the file name with a unique identifier for the thread.
fname="$WEBSITE-$(date +'%m-%d-%y_%T')-$THREAD_ID"

if [ ! -z "$BROWSER" ]; then
    fname="$fname-$BROWSER"
    echo "PCAPs in ./pcaps/$WEBSITE: " $(ls -ltr ./pcaps/$WEBSITE/ | grep "$WEBSITE.pcap$" | wc -l)
else
    echo "PCAPs in ./pcaps/$WEBSITE: " $(ls -ltr ./pcaps/$WEBSITE/ | grep ".pcap$" | wc -l)
fi

# Append .incomplete while capturing.
tcpdump -vv -i $NETWORK_INTERFACE -w ./pcaps/$WEBSITE/$fname.pcap.incomplete &
TCPDUMP_PID=$!

echo $TCPDUMP_PID >/tmp/tcpdump_pid_$WEBSITE_$NETWORK_INTERFACE_$THREAD_ID
