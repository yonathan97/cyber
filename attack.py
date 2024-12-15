import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from datetime import datetime

# Load and parse the CAN log file
def load_can_log(file_path, target_id):
    data = []
    pattern = r"\(([\d\.]+)\)\s+\w+\s+([\w]+)#([\w]+)"
    
    with open(file_path, 'r') as f:
        for line in f:
            match = re.match(pattern, line)
            if match:
                timestamp, can_id, can_data = match.groups()
                if can_id == target_id:  # Filter only selected CAN ID
                    data.append({
                        'timestamp': float(timestamp),
                        'id': can_id,
                        'data': can_data
                    })
    
    df = pd.DataFrame(data)
    df['time'] = pd.to_datetime(df['timestamp'], unit='s')
    df['delta_time'] = df['time'].diff().dt.total_seconds().fillna(0)
    df['oacc'] = df['delta_time'].cumsum()
    return df

# Simulate fabrication attack
from datetime import timedelta

def simulate_fabrication_attack(df, attack_frequency):
    """Simulate a fabrication attack by adding fake data points at specified frequency."""
    attack_df = df.copy()
    last_time = df['time'].iloc[-1]  # Get the last timestamp
    
    fabricated_times = [last_time + timedelta(seconds=i * attack_frequency) for i in range(200)]
    fabricated_data = {'time': fabricated_times, 'delta_time': attack_frequency, 'oacc': 0}
    
    fabricated_df = pd.DataFrame(fabricated_data)
    fabricated_df['delta_time'] = attack_frequency
    fabricated_df['oacc'] = fabricated_df['delta_time'].cumsum() + df['oacc'].iloc[-1]  # Continue Oacc from baseline
    
    attack_df = pd.concat([attack_df, fabricated_df], ignore_index=True)
    return attack_df


# Simulate suspension attack
def simulate_suspension_attack(df, suspend_start, suspend_duration):
    suspension_df = df.copy()
    suspension_df = suspension_df[suspension_df['time'] < suspend_start]
    resume_time = suspend_start + suspend_duration
    post_suspension = df[df['time'] >= resume_time]
    return pd.concat([suspension_df, post_suspension], ignore_index=True)

# Plot the results
def plot_results(baseline_df, attack_df, attack_type):
    plt.figure(figsize=(10, 15))
    
    # Accumulated Clock Offset
    plt.subplot(3, 1, 1)
    plt.plot(baseline_df['time'], baseline_df['oacc'], '--', label='Baseline')
    plt.plot(attack_df['time'], attack_df['oacc'], label=f'{attack_type} Attack')
    plt.title(f'Accumulated Clock Offset ({attack_type} Attack)')
    plt.xlabel('Time (s)')
    plt.ylabel('Oacc')
    plt.legend()
    
    # Identification Error
    plt.subplot(3, 1, 2)
    identification_error = attack_df['oacc'] - baseline_df['oacc'].iloc[0]
    plt.plot(attack_df['time'], identification_error, label='Identification Error')
    plt.title(f'Identification Error ({attack_type} Attack)')
    plt.xlabel('Time (s)')
    plt.ylabel('Error')
    plt.legend()
    
    # CUSUM Control Limit
    plt.subplot(3, 1, 3)
    cusum = np.cumsum(identification_error - identification_error.mean())
    plt.plot(attack_df['time'], cusum, label='CUSUM Control Limit')
    plt.title(f'CUSUM Control Limit ({attack_type} Attack)')
    plt.xlabel('Time (s)')
    plt.ylabel('CUSUM')
    plt.legend()
    
    plt.tight_layout()
    plt.show()

# Main script
if __name__ == "__main__":
    log_file = "baseline.log"  # Replace with your actual log file
    target_id = ['100', '080', '180']  # Selected CAN ID for testing
    
    # Load the baseline data
    baseline_df = load_can_log(log_file, target_id)
    
    # Simulate and plot fabrication attack
    fabrication_df = simulate_fabrication_attack(baseline_df, attack_frequency=0.01)
    plot_results(baseline_df, fabrication_df, "Fabrication")
    
    # Simulate and plot suspension attack
    suspend_start = baseline_df['time'].iloc[50]
    suspension_df = simulate_suspension_attack(baseline_df, suspend_start, suspend_duration=5)
    plot_results(baseline_df, suspension_df, "Suspension")
