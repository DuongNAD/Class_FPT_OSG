import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import joblib
import os

# Setup paths
input_path = r"e:\Project\Class\OSG\ram_dataset_augmented.csv"
output_X_path = r"e:\Project\Class\OSG\X_train.npy"
output_y_path = r"e:\Project\Class\OSG\y_train.npy"
scaler_path = r"e:\Project\Class\OSG\minmax_scaler.pkl"

print("1. Loading dataset...")
df = pd.read_csv(input_path)

# Ensure sorted by timestamp if it exists, then drop it
if 'timestamp' in df.columns:
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    df = df.drop(columns=['timestamp'])

print("2. Cleaning (Làm sạch)...")
# Drop rows with any NaN values
initial_len = len(df)
df = df.dropna()
print(f"   Dropped {initial_len - len(df)} rows containing missing values.")

print("3. Converting to Hardware-Independent Features (Percentages)...")
# Keep ONLY the target column! pure univariate time-series
keep_cols = ['ram_percent']
df = df[keep_cols]

print("4. Normalization / Scaling (Chuẩn hóa băng MinMaxScaler)...")
target_col = 'ram_percent'
target_idx = df.columns.get_loc(target_col)

# Scale features to [0, 1] range
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(df)

# Save scaler for future predictions
joblib.dump(scaler, scaler_path)
print(f"   Scaler saved to: {scaler_path}")

print("5. Sliding Window (Kỹ thuật trượt cửa sổ)...")
# Using 5 past timesteps to predict future (Makes model way more reactive to sudden tabs)
look_back = 5
X, y = [], []

for i in range(len(scaled_data) - look_back):
    # Features from past 10 steps
    X.append(scaled_data[i:(i + look_back), :])
    # Target to predict: ram_percent at step t + look_back
    y.append(scaled_data[i + look_back, target_idx])

X = np.array(X)
y = np.array(y)

print(f"   Generated {len(X)} sequences.")
print(f"   Features shape (X): {X.shape} -> (samples, timesteps, features)")
print(f"   Target shape (y): {y.shape}")

print("6. Train/Test Split (Chia tách tập dữ liệu)...")
# TRỌNG TÂM Time Series: Không được dùng train_test_split (random split)
# Vì xáo trộn ngẫu nhiên sẽ làm hỏng trình tự thời gian và gây Data Leakage.
# Phải cắt tuần tự: Train lấy khúc đầu (80%), Test lấy khúc đuôi (20%).
split_idx = int(len(X) * 0.8)

X_train, X_test = X[:split_idx], X[split_idx:]
y_train, y_test = y[:split_idx], y[split_idx:]

print(f"   Training Set (80%): {len(X_train)} samples")
print(f"   Testing Set (20%): {len(X_test)} samples")

print("7. Saving preprocessed Time Series data...")
output_dir = r"e:\Project\Class\OSG"
np.save(os.path.join(output_dir, "X_train.npy"), X_train)
np.save(os.path.join(output_dir, "y_train.npy"), y_train)
np.save(os.path.join(output_dir, "X_test.npy"), X_test)
np.save(os.path.join(output_dir, "y_test.npy"), y_test)
print("   Saved X_train.npy, y_train.npy, X_test.npy, y_test.npy")
print("Data preprocessing and Train/Test Split completed successfully.")
