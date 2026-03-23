import pandas as pd
import numpy as np
import os
from datetime import timedelta

# File path
file_path = r"e:\Project\Class\OSG\ram_dataset_augmented.csv"

# First, read the existing dataset to get exact columns and the last timestamp
df_existing = pd.read_csv(file_path)
columns = df_existing.columns.tolist()

if 'timestamp' in columns:
    df_existing['timestamp'] = pd.to_datetime(df_existing['timestamp'])
    last_timestamp = df_existing['timestamp'].max()
else:
    # If no timestamp column? Just set a default
    last_timestamp = pd.Timestamp.now()

num_samples = 3000
np.random.seed(42)

# System Constants (based on the VM/host)
TOTAL_RAM = 16848530232.0 
TOTAL_SWAP = 2147483648.0 # Example 2GB swap

synthetic_data = []

# Process names simulation
process_names = ['systemd', 'bash', 'gnome-terminal', 'sshd', 'python3', 'htop', 'snapd', 'NetworkManager', 'cron', 'rsyslogd']

current_time = last_timestamp + timedelta(seconds=1)

for i in range(num_samples):
    row = {}
    row['timestamp'] = current_time
    current_time += timedelta(seconds=2)
    
    # 1. Random RAM Usage between 10.0% and 42.0%
    ram_percent = np.random.uniform(10.0, 42.0)
    used_ram = (ram_percent / 100.0) * TOTAL_RAM
    available_ram = TOTAL_RAM - used_ram
    
    # 2. Random Swap
    swap_percent = np.random.uniform(0.0, 2.0)
    swap_used = (swap_percent / 100.0) * TOTAL_SWAP
    
    # System stats Map
    row['total_ram'] = TOTAL_RAM
    row['available_ram'] = available_ram
    row['used_ram'] = used_ram
    row['ram_percent'] = ram_percent
    row['swap_used'] = swap_used
    row['swap_percent'] = swap_percent
    
    # 3. Simulate Top 10 processes
    # We want sum of RSS to be some portion of used_ram to be realistic
    rss_pool = used_ram * np.random.uniform(0.1, 0.4) # Processes take 10-40% of used ram (rest is buffers/cache)
    
    # Generate 10 random portions that sum to 1
    portions = np.random.dirichlet(np.ones(10), size=1)[0]
    portions.sort()
    portions = portions[::-1] # Descending order
    
    for idx in range(1, 11):
        proc_rss = rss_pool * portions[idx - 1]
        proc_vms = proc_rss * np.random.uniform(1.1, 3.0)
        proc_cpu = np.random.uniform(0.0, 5.0)
        
        row[f'proc_{idx}_name'] = process_names[idx - 1]
        row[f'proc_{idx}_rss'] = proc_rss
        row[f'proc_{idx}_vms'] = proc_vms
        row[f'proc_{idx}_cpu'] = proc_cpu
        
    synthetic_data.append(row)

# Create DataFrame
df_synthetic = pd.DataFrame(synthetic_data, columns=columns)

# Append to original
df_final = pd.concat([df_existing, df_synthetic], ignore_index=True)
df_final = df_final.sort_values(by='timestamp').reset_index(drop=True)

df_final.to_csv(file_path, index=False)
print(f"Generated {num_samples} rows of low-RAM data (10-42%).")
print(f"Total dataset size is now: {len(df_final)} rows.")
print("Saved to:", file_path)
