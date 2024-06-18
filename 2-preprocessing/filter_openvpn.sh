#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 input_directory output_directory"
    exit 1
fi

INPUT_DIR="$1"
OUTPUT_DIR="$2"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Function to process pcap files
process_pcap() {
    local pcap_file="$1"
    local output_file="$2"

    # Skip if the output file already exists
    if [ -f "$output_file" ]; then
        echo "Skipping $pcap_file, $output_file already exists."
        return
    fi

    # Filter for OpenVPN packets (typically UDP port 1194)
    tcpdump -r "$pcap_file" 'udp port 1194' -w "$output_file"
}

export -f process_pcap
export OUTPUT_DIR

# Find and process all pcap files in the input directory and its subdirectories
find "$INPUT_DIR" -type f -name "*.pcap" | while read -r pcap_file; do
    # Create a corresponding output file path
    relative_path="${pcap_file#$INPUT_DIR/}"
    output_file="$OUTPUT_DIR/$relative_path"

    # Create the output directory if it doesn't exist
    mkdir -p "$(dirname "$output_file")"

    # Process the pcap file
    process_pcap "$pcap_file" "$output_file"
done
