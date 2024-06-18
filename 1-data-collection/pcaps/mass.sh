#!/bin/bash

# Initialize variables
WEBSITES_LIST_FILE_NAME="websites.txt"
SELENIUM_HOST=""
SELENIUM_PORT=""
NETWORK_INTERFACE=""
THREAD_ID=$$ # Unique identifier for this thread using the process ID

# Function to display usage
usage() {
    echo "Usage: $0 [-f <websites_list_file>] -i <network_interface> -h <selenium_host> -p <selenium_port>"
    exit 1
}

# Parse command line arguments
while getopts "f:h:p:i:" opt; do
    case ${opt} in
    f)
        WEBSITES_LIST_FILE_NAME=$OPTARG
        ;;
    h)
        SELENIUM_HOST=$OPTARG
        ;;
    p)
        SELENIUM_PORT=$OPTARG
        ;;
    i)
        NETWORK_INTERFACE=$OPTARG
        ;;
    *)
        usage
        ;;
    esac
done

# Check if host, port, and network interface arguments are provided
if [ -z "$SELENIUM_HOST" ] || [ -z "$SELENIUM_PORT" ] || [ -z "$NETWORK_INTERFACE" ]; then
    usage
fi

# Read the websites from the file and shuffle them.
mapfile -t websites < <(shuf "$WEBSITES_LIST_FILE_NAME")

source /home/lemonshushu/vpn-wf/venv/bin/activate

# Iterate over the websites.
while true; do
    for website in "${websites[@]}"; do
        echo "[$i][$(date)] Capturing $website"

        # Start capturing with a unique identifier for this thread.
        ./capture.sh "$NETWORK_INTERFACE" "$website" firefox "$THREAD_ID" &

        # Capture the PID file name.
        PID_FILE="/tmp/tcpdump_pid_$website_$NETWORK_INTERFACE_$THREAD_ID"

        # Use selenium to visit the website.
        python visit_website.py "https://$website" "$SELENIUM_HOST" "$SELENIUM_PORT" &
        driver_pid=$!
        echo "driver_pid: $driver_pid"

        wait $driver_pid

        # Kill the specific tcpdump session.
        if [ -f $PID_FILE ]; then
            TCPDUMP_PID=$(cat $PID_FILE)
            kill $TCPDUMP_PID
            rm $PID_FILE
            # Remove the .incomplete postfix after capturing is finished.
            for file in ./pcaps/$website/*-$THREAD_ID-firefox.pcap.incomplete; do
                mv "$file" "${file%.incomplete}"
            done
        else
            echo "PID file for $website not found!"
        fi

        # Sleep for 3 secs with countdown
        for i in {3..1}; do
            echo -n "$i "
            sleep 1
        done
    done
done
