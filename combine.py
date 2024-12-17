import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

# Function to load CAN log data for a specific CAN ID
def load_can_log(file_path, target_id):
    """Load and parse CAN log data for a specific target CAN ID."""
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
                        'can_id': can_id,
                        'data': can_data
                    })
    df = pd.DataFrame(data)
    if not df.empty:
        df['time'] = pd.to_datetime(df['timestamp'], unit='s')
        df['delta_time'] = df['time'].diff().dt.total_seconds().fillna(0)
        df['oacc'] = df['delta_time'].cumsum()
    return df

# Function to plot metrics
def plot_metrics(baseline_df, attack_df, can_id):
    """Plot Oacc, Identification Error, and CUSUM."""
    plt.figure(figsize=(12, 10))

    # Oacc Plot
    plt.subplot(3, 1, 1)
    plt.plot(baseline_df['time'], baseline_df['oacc'], '--', label='Baseline', color='blue')
    plt.plot(attack_df['time'], attack_df['oacc'], label='Combined Attack', color='red')
    plt.title(f'Accumulated Clock Offset (Oacc) - CAN ID {can_id}')
    plt.xlabel('Time')
    plt.ylabel('Oacc')
    plt.legend()

    # Identification Error Plot
    plt.subplot(3, 1, 2)
    identification_error = attack_df['oacc'] - baseline_df['oacc'].iloc[0]
    plt.plot(attack_df['time'], identification_error, label='Identification Error', color='orange')
    plt.title(f'Identification Error - CAN ID {can_id}')
    plt.xlabel('Time')
    plt.ylabel('Error')
    plt.legend()

    # CUSUM Plot
    plt.subplot(3, 1, 3)
    cusum = np.cumsum(identification_error - identification_error.mean())
    plt.plot(attack_df['time'], cusum, label='CUSUM Control Limit', color='purple')
    plt.title(f'CUSUM Control Limit - CAN ID {can_id}')
    plt.xlabel('Time')
    plt.ylabel('CUSUM')
    plt.legend()

    plt.tight_layout()
    plt.savefig(f"combined_attack_CAN_ID_{can_id}.png")
    print(f"Saved plot for CAN ID {can_id}: combined_attack_CAN_ID_{can_id}.png")
    plt.close()

# Main function
if __name__ == "__main__":
    # Define log file paths
    log_files = {
        "baseline": "base_co.log",
        "attack": "combined_att.log"
    }

    # Define target CAN IDs
    target_ids = ['244']  # Add CAN IDs to analyze

    # Process each CAN ID
    for can_id in target_ids:
        print(f"\nProcessing CAN ID: {can_id}")

        # Load baseline and attack data
        baseline_df = load_can_log(log_files['baseline'], can_id)
        attack_df = load_can_log(log_files['attack'], can_id)

        # Check if data is available
        if baseline_df.empty or attack_df.empty:
            print(f"No data for CAN ID {can_id}. Skipping...")
            continue

        # Generate plots
        plot_metrics(baseline_df, attack_df, can_id)

    print("Analysis complete!")
   # Create summary table
    summary_df = pd.DataFrame(summary_results)
    print("\nSummary Table:")
    print(summary_df)
    summary_df.to_csv("attack_summary_table.csv", index=False)
    print("Summary table saved as attack_summary_table.csv.")
