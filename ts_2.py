import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from datetime import datetime, timedelta

# Load CAN log file and process for a specific ID
def load_can_log(file_path, target_id):
    """Load and parse CAN log data for a specific target ID."""
    data = []
    pattern = r"\(([\d\.]+)\)\s+\w+\s+([\w]+)#([\w]+)"
    with open(file_path, 'r') as f:
        for line in f:
            match = re.match(pattern, line)
            if match:
                timestamp, can_id, can_data = match.groups()
                if can_id == target_id:
                    data.append({
                        'timestamp': float(timestamp),
                        'id': can_id,
                        'data': can_data
                    })
    df = pd.DataFrame(data)
    if not df.empty:
        df['time'] = pd.to_datetime(df['timestamp'], unit='s')
        df['delta_time'] = df['time'].diff().dt.total_seconds().fillna(0)
        df['oacc'] = df['delta_time'].cumsum()
    return df

# Plot Results
def plot_metrics(baseline_df, attack_df, attack_type, can_id, save_prefix):
    """Plot Oacc, Identification Error, and CUSUM Control Limit."""
    plt.figure(figsize=(10, 15))
    
    # Oacc
    plt.subplot(3, 1, 1)
    plt.plot(baseline_df['time'], baseline_df['oacc'], '--', label='Baseline', color='blue')
    plt.plot(attack_df['time'], attack_df['oacc'], label=f'{attack_type}', color='red')
    plt.title(f'Accumulated Clock Offset (Oacc) - {attack_type} - CAN ID {can_id}')
    plt.xlabel('Time (s)')
    plt.ylabel('Oacc')
    plt.legend()
    
    # Identification Error
    plt.subplot(3, 1, 2)
    identification_error = attack_df['oacc'] - baseline_df['oacc'].iloc[0]
    plt.plot(attack_df['time'], identification_error, label='Identification Error', color='orange')
    plt.title(f'Identification Error - {attack_type} - CAN ID {can_id}')
    plt.xlabel('Time (s)')
    plt.ylabel('Error')
    plt.legend()
    
    # CUSUM Control Limit
    plt.subplot(3, 1, 3)
    cusum = np.cumsum(identification_error - identification_error.mean())
    plt.plot(attack_df['time'], cusum, label='CUSUM Control Limit', color='purple')
    plt.title(f'CUSUM Control Limit - {attack_type} - CAN ID {can_id}')
    plt.xlabel('Time (s)')
    plt.ylabel('CUSUM')
    plt.legend()
    
    plt.tight_layout()
    filename = f"{save_prefix}_CAN_ID_{can_id}.png"
    plt.savefig(filename)
    print(f"Saved plot: {filename}")
    plt.close()

# Generate Summary Table
def generate_summary_table(baseline_df, attack_df, can_id, attack_type):
    """Generate a summary table comparing baseline and attack metrics."""
    baseline_oacc = baseline_df['oacc'].iloc[-1]
    attack_oacc = attack_df['oacc'].iloc[-1]
    identification_error = attack_oacc - baseline_oacc
    cusum = np.cumsum((attack_df['oacc'] - baseline_df['oacc'].iloc[0]) - (attack_df['oacc'].mean())).iloc[-1]

    summary = {
        "CAN ID": can_id,
        "Attack Type": attack_type,
        "Baseline Oacc": f"{baseline_oacc:.4f}",
        "Attack Oacc": f"{attack_oacc:.4f}",
        "Identification Error": f"{identification_error:.4f}",
        "CUSUM Deviation": f"{cusum:.4f}"
    }
    return summary

# Main script
if __name__ == "__main__":
    log_files = {
        "baseline": "baseline.log",
        "fabrication": "attack.log",
        "suspension": "suspension_attack.log"
    }
    target_ids = ['080', '100', '180']  # List of CAN IDs
    summary_results = []

    # Process each CAN ID and generate plots/tables
    for can_id in target_ids:
        print(f"\nProcessing CAN ID: {can_id}")
        
        # Load baseline data
        baseline_df = load_can_log(log_files['baseline'], can_id)
        if baseline_df.empty:
            print(f"No baseline data for CAN ID {can_id}. Skipping...")
            continue
        
        # Fabrication Attack
        fabrication_df = load_can_log(log_files['fabrication'], can_id)
        if not fabrication_df.empty:
            plot_metrics(baseline_df, fabrication_df, "Fabrication Attack", can_id, "fabrication")
            summary_results.append(generate_summary_table(baseline_df, fabrication_df, can_id, "Fabrication Attack"))
        
        # Suspension Attack
        suspension_df = load_can_log(log_files['suspension'], can_id)
        if not suspension_df.empty:
            plot_metrics(baseline_df, suspension_df, "Suspension Attack", can_id, "suspension")
            summary_results.append(generate_summary_table(baseline_df, suspension_df, can_id, "Suspension Attack"))
    
    # Create summary table
    summary_df = pd.DataFrame(summary_results)
    print("\nSummary Table:")
    print(summary_df)
    summary_df.to_csv("attack_summary_table.csv", index=False)
    print("Summary table saved as attack_summary_table.csv.")
