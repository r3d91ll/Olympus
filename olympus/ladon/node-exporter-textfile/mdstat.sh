#!/bin/bash

# Directory for node exporter textfile collector
TEXTFILE_COLLECTOR_DIR="/var/lib/node_exporter/textfile_collector"

# Create directory if it doesn't exist
mkdir -p "${TEXTFILE_COLLECTOR_DIR}"

# Temporary file for metrics
TMPFILE=$(mktemp)

# Get mdstat info
while read -r line; do
    if [[ "${line}" =~ ^([a-zA-Z0-9_]+)\ : ]]; then
        # Array name
        array="${BASH_REMATCH[1]}"
        
        # Get array status
        if [[ "${line}" =~ \[([0-9]+)/([0-9]+)\] ]]; then
            total="${BASH_REMATCH[2]}"
            working="${BASH_REMATCH[1]}"
            echo "node_md_disks{array=\"${array}\"} ${total}" >> "${TMPFILE}"
            echo "node_md_disks_active{array=\"${array}\"} ${working}" >> "${TMPFILE}"
        fi
        
        # Get recovery/resync status if present
        if [[ "${line}" =~ recovery\ =\ ([0-9.]+)% ]]; then
            percent="${BASH_REMATCH[1]}"
            echo "node_md_recovery_percentage{array=\"${array}\"} ${percent}" >> "${TMPFILE}"
        elif [[ "${line}" =~ resync\ =\ ([0-9.]+)% ]]; then
            percent="${BASH_REMATCH[1]}"
            echo "node_md_resync_percentage{array=\"${array}\"} ${percent}" >> "${TMPFILE}"
        fi
    fi
done < /proc/mdstat

# Atomic move
mv "${TMPFILE}" "${TEXTFILE_COLLECTOR_DIR}/mdstat.prom"
