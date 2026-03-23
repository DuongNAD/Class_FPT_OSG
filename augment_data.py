import pandas as pd
import numpy as np
import os
import glob
from datetime import timedelta

# Paths to the 3 dataset files
file_paths = [
    r"e:\Project\Class\OSG\ram_dataset.csv",
    r"e:\Project\Class\OSG\ram_dataset (1).csv",
    r"e:\Project\Class\OSG\ram_dataset (2).csv"
]

# 1. Merge the datasets
dfs = []
for p in file_paths:
    if os.path.exists(p):
        df = pd.read_csv(p)
        dfs.append(df)
    else:
        print(f"Warning: File not found: {p}")

if not dfs:
    print("No datasets found. Exiting.")
    exit(1)

merged_df = pd.concat(dfs, ignore_index=True)

# Parse timestamp
merged_df['timestamp'] = pd.to_datetime(merged_df['timestamp'])
merged_df = merged_df.sort_values(by='timestamp').reset_index(drop=True)

print(f"Original merged dataset shape: {merged_df.shape}")

# 2. Data Augmentation
# We will create synthetic data by adding noise to numerical features
# and keeping the categorical (process names) the same as the base row.

# Identify numerical columns (exclude timestamp and categorical 'name' columns)
num_cols = merged_df.select_dtypes(include=[np.number]).columns.tolist()

# Let's generate 3x more data
augmentation_factor = 3
synthetic_dfs = []

# Noise configuration: add 1-5% gaussian noise based on column standard deviation
np.random.seed(42)

for i in range(augmentation_factor):
    syn_df = merged_df.copy()
    
    # Generate random noise for numerical columns
    for col in num_cols:
        std = syn_df[col].std()
        if pd.isna(std) or std == 0:
            continue
        
        # Add noise (mean 0, std = 2% of original std)
        noise = np.random.normal(0, std * 0.02, size=len(syn_df))
        syn_df[col] = syn_df[col] + noise
        
        # Enforce logical bounds
        if 'percent' in col or 'cpu' in col:
            syn_df[col] = np.clip(syn_df[col], 0, 100) # Percentage bounds
        elif 'ram' in col or 'swap' in col or 'rss' in col or 'vms' in col:
            syn_df[col] = np.maximum(syn_df[col], 0) # Cannot be negative bytes
            syn_df[col] = np.floor(syn_df[col]) # Memory bytes should be integers
            
    # Modify timestamps slighly so they are distinct
    time_offset = timedelta(seconds=i+1)
    syn_df['timestamp'] = syn_df['timestamp'] + time_offset
    
    synthetic_dfs.append(syn_df)

# Combine original with synthetic data
final_df = pd.concat([merged_df] + synthetic_dfs, ignore_index=True)

# Sort by timestamp again
final_df = final_df.sort_values(by='timestamp').reset_index(drop=True)

print(f"Augmented dataset shape: {final_df.shape}")

# 3. Save the augmented dataset
output_path = r"e:\Project\Class\OSG\ram_dataset_augmented.csv"
final_df.to_csv(output_path, index=False)
print(f"Successfully saved augmented dataset to: {output_path}")
