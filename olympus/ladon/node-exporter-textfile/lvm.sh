#!/bin/bash

# Directory for node exporter textfile collector
TEXTFILE_COLLECTOR_DIR="/var/lib/node_exporter/textfile_collector"

# Create directory if it doesn't exist
mkdir -p "${TEXTFILE_COLLECTOR_DIR}"

# Temporary file for metrics
TMPFILE=$(mktemp)

# Get LVM info
echo "# HELP node_lvm_lv_size_bytes Logical volume size in bytes"
echo "# TYPE node_lvm_lv_size_bytes gauge"
lvs --units b --noheadings --nosuffix -o lv_name,vg_name,lv_size | while read -r lv vg size; do
    echo "node_lvm_lv_size_bytes{lv=\"${lv}\",vg=\"${vg}\"} ${size}" >> "${TMPFILE}"
done

echo "# HELP node_lvm_vg_size_bytes Volume group size in bytes"
echo "# TYPE node_lvm_vg_size_bytes gauge"
vgs --units b --noheadings --nosuffix -o vg_name,vg_size,vg_free | while read -r vg size free; do
    echo "node_lvm_vg_size_bytes{vg=\"${vg}\"} ${size}" >> "${TMPFILE}"
    echo "node_lvm_vg_free_bytes{vg=\"${vg}\"} ${free}" >> "${TMPFILE}"
done

# Atomic move
mv "${TMPFILE}" "${TEXTFILE_COLLECTOR_DIR}/lvm.prom"
