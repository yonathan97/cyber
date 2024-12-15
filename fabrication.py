import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Step 1: Load the dataset
def load_data(folder_path):
    """Efficiently load and clean CAN bus voltage data from all CSV files in a folder."""
    try:
        all_dataframes = []
        for file in os.listdir(folder_path):
            if file.endswith(".csv"):
                file_path = os.path.join(folder_path, file)
                print(f"Processing file: {file}")

                # Process file dynamically and clean unwanted rows in-memory
                clean_lines = []
                with open(file_path, 'r') as f:
                    for line in f:
                        if not line.strip().isdigit() and ',' in line:  # Skip non-data rows
                            clean_lines.append(line)

                # Convert cleaned lines to a DataFrame in-memory
                if clean_lines:
                    from io import StringIO  # In-memory buffer for cleaned data
                    clean_data = StringIO("".join(clean_lines))
                    df = pd.read_csv(clean_data, delimiter=',', on_bad_lines='skip')
                    df.columns = ['Time (ms)', 'Channel A (V)', 'Channel B (V)']
                    all_dataframes.append(df)

                # Process in chunks for memory efficiency
                if len(all_dataframes) >= 50:  # Combine every 50 files
                    yield pd.concat(all_dataframes, ignore_index=True)
                    all_dataframes = []

        # Combine any remaining dataframes
        if all_dataframes:
            yield pd.concat(all_dataframes, ignore_index=True)
    except Exception as e:
        print("Error loading files:", e)

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

# Step 3: Simulate a fabricated message
def simulate_fabrication_attack(df, mean_a, mean_b):
    """Generate a fabricated CAN message with adjusted voltage and timing."""
    fabricated_message = {
        'Time (ms)': df['Time (ms)'].iloc[-1] + 0.002,  # Slight timing deviation
        'Channel A (V)': mean_a + 0.05,  # Slightly higher than the mean
        'Channel B (V)': mean_b + 0.05   # Slightly higher than the mean
    }

    print("Fabricated Suspension Attack Message:")
    print(fabricated_message)
    return fabricated_message

# Step 4: Simulate a masquerading attack
def simulate_masquerading_attack(df, target_mean_a, target_mean_b):
    """Simulate a masquerading attack by mimicking another ECU's voltage characteristics."""
    masqueraded_message = {
        'Time (ms)': df['Time (ms)'].iloc[-1] + 0.002,  # Mimic normal timing
        'Channel A (V)': target_mean_a,  # Mimic the target ECU voltage
        'Channel B (V)': target_mean_b
    }
    print("Masqueraded Message:")
    print(masqueraded_message)
    return masqueraded_message

# Step 5: Plot legitimate vs fabricated and masqueraded voltage signals
def plot_voltages(df, fabricated_message, masqueraded_message):
    """Plot original Channel A and B voltages with the fabricated and masqueraded messages."""
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

    plt.xlabel('Time (ms)')
    plt.ylabel('Voltage (V)')
    plt.title('Legitimate vs Fabricated and Masqueraded CAN Messages')
    plt.legend()
    plt.grid()
    plt.show()

# Main Function
def main():
    folder_path = "Dacia Duster"  # Replace with the folder path containing CSV files

    combined_df = pd.DataFrame()  # Initialize empty DataFrame
    for chunk_df in load_data(folder_path):
        combined_df = pd.concat([combined_df, chunk_df], ignore_index=True)

    if combined_df.empty:
        print("No valid data found.")   
        return

    print(f"Total combined data size: {combined_df.shape}\n")
    
    # Analyze Legitimate Voltages
    (mean_a, std_a), (mean_b, std_b) = analyze_voltages(combined_df)

    # Simulate a Fabrication Attack
    fabricated_message = simulate_fabrication_attack(combined_df, mean_a, mean_b)

    # Simulate a Masquerading Attack
    target_mean_a, target_mean_b = mean_a, mean_b  # Adjust for specific target ECUs if needed
    masqueraded_message = simulate_masquerading_attack(combined_df, target_mean_a, target_mean_b)

    # Plot Results
    plot_voltages(combined_df, fabricated_message, masqueraded_message)

if __name__ == "__main__":
    main()
