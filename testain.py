import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

# Function to load CAN log data for a specific CAN ID
def load_can_log(file_path, target_id):
    """Load CAN log data for a specific CAN ID."""
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

# Function to calculate UCL
def calculate_ucl(oacc):
    """Calculate the Upper Control Limit (UCL) for Oacc."""
    return oacc.mean() + 3 * oacc.std()

# Function to generate all plots
def generate_all_plots(baseline_df, attack_df, can_id, attack_label):
    """Generate all requested plots."""
    # Accumulated Clock Offset
    plt.figure(figsize=(8, 6))
    plt.plot(baseline_df['time'], baseline_df['oacc'], label='Without Attack', color='blue')
    plt.plot(attack_df['time'], attack_df['oacc'], label='With Attack', color='red')
    plt.title(f"Accumulated Clock Offset - {attack_label}")
    plt.xlabel("Time [Sec]")
    plt.ylabel("Accumulated Clock Offset [ms]")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"oacc_{attack_label}.png")
    plt.close()

    # Identification Error
    identification_error = attack_df['oacc'] - baseline_df['oacc'].iloc[0]
    plt.figure(figsize=(8, 6))
    plt.plot(attack_df['time'], identification_error, color='orange', label='Identification Error')
    plt.title(f"Identification Error - {attack_label}")
    plt.xlabel("Time [Sec]")
    plt.ylabel("Identification Error")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"identification_error_{attack_label}.png")
    plt.close()

    # Upper Control Limit
    ucl = calculate_ucl(baseline_df['oacc'])
    plt.figure(figsize=(8, 6))
    plt.plot(attack_df['time'], attack_df['oacc'], color='red', label='With Attack')
    plt.axhline(y=ucl, color='purple', linestyle='--', label='Upper Control Limit')
    plt.title(f"Upper Control Limit - {attack_label}")
    plt.xlabel("Time [Sec]")
    plt.ylabel("Oacc")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"ucl_{attack_label}.png")
    plt.close()

    # PMF of Message Intervals
    plt.figure(figsize=(8, 6))
    unique, counts = np.unique(attack_df['delta_time'], return_counts=True)
    probabilities = counts / counts.sum()
    plt.bar(unique, probabilities, width=0.01)
    plt.title(f"Probability Mass Function - {attack_label}")
    plt.xlabel("Message Interval [Sec]")
    plt.ylabel("Probability")
    plt.tight_layout()
    plt.savefig(f"pmf_{attack_label}.png")
    plt.close()

# Main script
if __name__ == "__main__":
    log_file = "attack_log.log"  # Replace with your log file
    target_id = '244'  # Replace with the CAN ID of interest

    # Load baseline and attack data
    print("Loading data...")
    baseline_df = load_can_log(log_file, target_id)
    fabrication_df = load_can_log(log_file, target_id)  # Replace with Fabrication segment
    suspension_df = load_can_log(log_file, target_id)   # Replace with Suspension segment

    # Generate all plots for fabrication and suspension
    if not baseline_df.empty and not fabrication_df.empty:
        generate_all_plots(baseline_df, fabrication_df, target_id, "Fabrication Attack")
    if not baseline_df.empty and not suspension_df.empty:
        generate_all_plots(baseline_df, suspension_df, target_id, "Suspension Attack")

    print("Plots generated successfully!")
