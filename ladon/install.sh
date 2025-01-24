#!/bin/bash

# Exit on any error
set -e

# Must run as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Create necessary directories
mkdir -p /var/lib/node_exporter/textfile_collector
chown root:root /var/lib/node_exporter/textfile_collector

# Make collector scripts executable
chmod +x "${SCRIPT_DIR}/node-exporter-textfile/"*.sh

# Install systemd services
cp "${SCRIPT_DIR}/systemd/ladon.service" /etc/systemd/system/
cp "${SCRIPT_DIR}/systemd/ladon-collectors.service" /etc/systemd/system/
cp "${SCRIPT_DIR}/systemd/ladon-collectors.timer" /etc/systemd/system/

# Reload systemd
systemctl daemon-reload

# Enable and start services
systemctl enable ladon.service
systemctl enable ladon-collectors.timer
systemctl start ladon.service
systemctl start ladon-collectors.timer

echo "Ladon monitoring stack has been installed and started."
echo "Check status with: systemctl status ladon.service"
