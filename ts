import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
from datetime import datetime

# Load and parse the CAN log file
def load_can_log(file_path, target_id):
    """Load and process CAN log data for a specific target CAN ID."""
    data = []
    pattern = r"\(([\d\.]+)\)\s+\w+\s+([\w]+)#([\w]+)"
    
    with open(file_path, 'r') as f:
        for line in f:
            match = re.match(pattern, line)
            if match:
                timestamp, can_id, can_data = match.groups()
                if can_id == target_id:  # Filter for specific CAN ID
                    data.append({
                        'timestamp': float(timestamp),
                        'id': can_id,
                        'data': can_data
                    })
    
    df = pd.DataFrame(data)
    if not df.empty:
        # Convert timestamp to datetime and calculate metrics
        df['time'] = pd.to_datetime(df['timestamp'], unit='s')
        df['delta_time'] = df['time'].diff().dt.total_seconds().fillna(0)
        df['oacc'] = df['delta_time'].cumsum()
        df['acc'] = np.arange(1, len(df) + 1)  # Accumulated Clock Count (ACC)
    return df

# Plot the results
def plot_results(baseline_df, suspension_df, attack_df, target_id):
    """Plot Oacc, Identification Error, CUSUM, and ACC for the baseline, suspension, and attack logs."""
    plt.figure(figsize=(15, 20))

    # Accumulated Clock Offset (Oacc)
    plt.subplot(4, 1, 1)
    plt.plot(baseline_df['time'], baseline_df['oacc'], '--', label='Baseline', color='blue')
    plt.plot(suspension_df['time'], suspension_df['oacc'], label='Suspension', color='orange')
    plt.plot(attack_df['time'], attack_df['oacc'], label='Attack', color='red')
    plt.title(f'Accumulated Clock Offset (Oacc) - CAN ID {target_id}')
    plt.xlabel('Time (s)')
    plt.ylabel('Oacc')
    plt.legend()
    plt.grid()

    # Identification Error
    plt.subplot(4, 1, 2)
    identification_error = attack_df['oacc'] - baseline_df['oacc'].iloc[0]
    plt.plot(attack_df['time'], identification_error, label='Identification Error', color='green')
    plt.title(f'Identification Error - CAN ID {target_id}')
    plt.xlabel('Time (s)')
    plt.ylabel('Error')
    plt.legend()
    plt.grid()

    # CUSUM Control Limit
    plt.subplot(4, 1, 3)
    cusum = np.cumsum(identification_error - identification_error.mean())
    plt.plot(attack_df['time'], cusum, label='CUSUM Control Limit', color='purple')
    plt.title(f'CUSUM Control Limit - CAN ID {target_id}')
    plt.xlabel('Time (s)')
    plt.ylabel('CUSUM')
    plt.legend()
    plt.grid()

    # Accumulated Clock Count (ACC)
    plt.subplot(4, 1, 4)
    plt.plot(baseline_df['time'], baseline_df['acc'], '--', label='Baseline', color='blue')
    plt.plot(suspension_df['time'], suspension_df['acc'], label='Suspension', color='orange')
    plt.plot(attack_df['time'], attack_df['acc'], label='Attack', color='red')
    plt.title(f'Accumulated Clock Count (ACC) - CAN ID {target_id}')
    plt.xlabel('Time (s)')
    plt.ylabel('ACC')
    plt.legend()
    plt.grid()

    # Save the plot to a file
    plt.tight_layout()
    plt.savefig(f"analysis_CAN_ID_{target_id}.png")
    print(f"Saved analysis plots for CAN ID {target_id} as PNG.")
    plt.close()

# Main script
if __name__ == "__main__":
    target_id = "180"  # Replace with the CAN ID you want to analyze

    # Load baseline, suspension, and attack logs
    baseline_file = "baseline.log"  # Replace with your baseline log file
    suspension_file = "suspension_attack.log"  # Replace with your suspension log file
    attack_file = "attack.log"  # Replace with your attack log file

    # Load data for the specified CAN ID
    baseline_df = load_can_log(baseline_file, target_id)
    suspension_df = load_can_log(suspension_file, target_id)
    attack_df = load_can_log(attack_file, target_id)

    # Check if all data is available
    if baseline_df.empty or suspension_df.empty or attack_df.empty:
        print(f"Data missing for CAN ID {target_id}. Ensure all log files have valid data.")
    else:
        # Plot results
        plot_results(baseline_df, suspension_df, attack_df, target_id)
