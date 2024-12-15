import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Step 1: Load the dataset
def load_data(folder_path):
    """Load and clean CAN bus voltage data by skipping metadata rows dynamically."""
    try:
        all_dataframes = []
        file_count = 0

        for file in os.listdir(folder_path):
            if file.endswith(".csv"):
                file_path = os.path.join(folder_path, file)
                print(f"Processing file: {file}")

                # Open file to find the header row dynamically
                with open(file_path, 'r') as f:
                    lines = f.readlines()

                # Find the line containing the actual header
                header_index = -1
                for i, line in enumerate(lines):
                    if "Time" in line and "Channel A" in line and "Channel B" in line:
                        header_index = i
                        break

                # Skip invalid files with no header
                if header_index == -1:
                    print(f"Warning: No valid header found in {file}. Skipping.")
                    continue

                # Read the data starting from the header
                df = pd.read_csv(file_path, skiprows=header_index, on_bad_lines='skip')

                # Ensure correct column naming and validate numeric columns
                df.columns = ['Time (ms)', 'Channel A (V)', 'Channel B (V)']
                df['Time (ms)'] = pd.to_numeric(df['Time (ms)'], errors='coerce')
                df['Channel A (V)'] = pd.to_numeric(df['Channel A (V)'], errors='coerce')
                df['Channel B (V)'] = pd.to_numeric(df['Channel B (V)'], errors='coerce')

                # Drop invalid rows
                df = df.dropna(subset=['Time (ms)', 'Channel A (V)', 'Channel B (V)'])

                all_dataframes.append(df)
                file_count += 1

                # Stop after processing 50 files
                if file_count >= 50:
                    print("Loaded first 50 CSV files.")
                    break

        # Combine all dataframes
        if all_dataframes:
            combined_df = pd.concat(all_dataframes, ignore_index=True)
            combined_df = combined_df.sort_values(by='Time (ms)').reset_index(drop=True)
            return combined_df
        else:
            print("No valid files found.")
            return pd.DataFrame()

    except Exception as e:
        print("Error loading files:", e)
        return pd.DataFrame()

# Step 2: Analyze the legitimate voltage thresholds
def analyze_voltages(df):
    """Analyze mean and standard deviation for Channel A and Channel B voltages."""
    mean_a = df['Channel A (V)'].mean()
    std_a = df['Channel A (V)'].std()
    mean_b = df['Channel B (V)'].mean()
    std_b = df['Channel B (V)'].std()

    print(f"Channel A Voltage - Mean: {mean_a:.4f} V, Std Dev: {std_a:.4f} V")
    print(f"Channel B Voltage - Mean: {mean_b:.4f} V, Std Dev: {std_b:.4f} V\n")

    return (mean_a, std_a), (mean_b, std_b)

# Step 3: Calculate Time Intervals and Accumulated Offsets
def calculate_time_intervals(df):
    """Calculate time intervals (delta time) and accumulated offsets."""
    df['Time Diff (ms)'] = df['Time (ms)'].diff().fillna(0)
    df['Oacc'] = df['Time Diff (ms)'].cumsum()
    return df

# Step 4: Simulate a fabricated message
def simulate_fabrication_attack(df, mean_a, mean_b):
    """Generate a fabricated CAN message with adjusted voltage and timing."""
    fabricated_message = {
        'Time (ms)': df['Time (ms)'].iloc[-1] + 0.002,  # Slight timing deviation
        'Channel A (V)': mean_a + 0.05,  # Slightly higher than the mean
        'Channel B (V)': mean_b + 0.05   # Slightly higher than the mean
    }
    df.loc[len(df)] = fabricated_message
    print("Fabricated Suspension Attack Message:")
    print(fabricated_message)
    return df, fabricated_message

# Step 5: Simulate a masquerading attack
def simulate_masquerading_attack(df, target_mean_a, target_mean_b):
    """Simulate a masquerading attack by mimicking another ECU's voltage characteristics."""
    masqueraded_message = {
        'Time (ms)': df['Time (ms)'].iloc[-1] + 0.002,  # Mimic normal timing
        'Channel A (V)': target_mean_a,  # Mimic the target ECU voltage
        'Channel B (V)': target_mean_b
    }
    df.loc[len(df)] = masqueraded_message
    print("Masqueraded Message:")
    print(masqueraded_message)
    return df, masqueraded_message

# Step 6: Detect anomalies using CUSUM
def cusum_detection(series, threshold):
    """Apply CUSUM detection for anomalies."""
    cusum = np.cumsum(series - series.mean())
    anomalies = np.where(np.abs(cusum) > threshold)[0]
    return anomalies

# Step 7: Plot legitimate, fabricated, masqueraded messages, and anomalies
def plot_voltages_and_anomalies(df, fabricated_message, masqueraded_message, anomalies):
    """Plot original Channel A and B voltages with fabricated, masqueraded messages, and anomalies."""
    plt.figure(figsize=(10, 6))
    plt.plot(df['Time (ms)'], df['Channel A (V)'], label='Channel A (Legit)', alpha=0.7)
    plt.plot(df['Time (ms)'], df['Channel B (V)'], label='Channel B (Legit)', alpha=0.7)

    # Highlight the fabricated message
    plt.scatter(fabricated_message['Time (ms)'], fabricated_message['Channel A (V)'], 
                color='red', label='Fabricated Channel A', zorder=5)
    plt.scatter(fabricated_message['Time (ms)'], fabricated_message['Channel B (V)'], 
                color='orange', label='Fabricated Channel B', zorder=5)

    # Highlight the masqueraded message
    plt.scatter(masqueraded_message['Time (ms)'], masqueraded_message['Channel A (V)'], 
                color='blue', label='Masqueraded Channel A', zorder=5)
    plt.scatter(masqueraded_message['Time (ms)'], masqueraded_message['Channel B (V)'], 
                color='green', label='Masqueraded Channel B', zorder=5)

    # Highlight anomalies
    if len(anomalies) > 0:
        plt.scatter(df.loc[anomalies, 'Time (ms)'], df.loc[anomalies, 'Channel A (V)'], 
                    color='purple', label='Anomalies', zorder=6)

    plt.xlabel('Time (ms)')
    plt.ylabel('Voltage (V)')
    plt.title('Legitimate vs Fabricated and Masqueraded CAN Messages with Anomalies')
    plt.legend()
    plt.grid()
    plt.show()

# Main Function
def main():
    folder_path = "Dacia Duster"  # Replace with the folder path containing CSV files

    combined_df = load_data(folder_path)

    if combined_df.empty:
        print("No valid data found.")
        return

    print(f"Total combined data size: {combined_df.shape}\n")

    # Step 3: Calculate Time Intervals and Accumulated Offsets
    combined_df = calculate_time_intervals(combined_df)
    print("Time intervals and accumulated offsets added.")

    # Analyze Legitimate Voltages
    (mean_a, std_a), (mean_b, std_b) = analyze_voltages(combined_df)

    # Simulate a Fabrication Attack
    combined_df, fabricated_message = simulate_fabrication_attack(combined_df, mean_a, mean_b)

    # Simulate a Masquerading Attack
    target_mean_a, target_mean_b = mean_a, mean_b  # Adjust for specific target ECUs if needed
    combined_df, masqueraded_message = simulate_masquerading_attack(combined_df, target_mean_a, target_mean_b)

    # Detect Anomalies
    anomalies = cusum_detection(combined_df['Oacc'], threshold=0.1)
    print(f"Anomalies detected at indices: {anomalies}")

    # Plot Results
    plot_voltages_and_anomalies(combined_df, fabricated_message, masqueraded_message, anomalies)

if __name__ == "__main__":
    main()
