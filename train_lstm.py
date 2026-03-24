import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import os

# 1. Load the preprocessed data
data_dir = r"e:\Project\Class\OSG"
X_train = np.load(os.path.join(data_dir, "X_train.npy"))
y_train = np.load(os.path.join(data_dir, "y_train.npy"))
X_test = np.load(os.path.join(data_dir, "X_test.npy"))
y_test = np.load(os.path.join(data_dir, "y_test.npy"))

print(f"X_train shape: {X_train.shape}")
print(f"y_train shape: {y_train.shape}")
print(f"X_test shape: {X_test.shape}")
print(f"y_test shape: {y_test.shape}")

# X_train shape is (samples, timesteps, features)
timesteps = X_train.shape[1]
features = X_train.shape[2]

# 2. Model Architecture Construction (Xây dựng kiến trúc AI)
print("Building LSTM Model...")
model = Sequential()

# Lớp ẩn 1: Input Layer + LSTM với 32 units (siêu nhẹ)
model.add(LSTM(units=32, return_sequences=True, input_shape=(timesteps, features)))
model.add(Dropout(0.2)) # Chống học vẹt (Overfitting)

# Lớp ẩn 2: LSTM với 16 units
model.add(LSTM(units=16, return_sequences=False))
model.add(Dropout(0.2))

# Lớp đầu ra (Output Layer): 1 nơ-ron duy nhất dự đoán tỷ lệ % RAM
model.add(Dense(units=1, activation='linear'))

# 3. Model Compilation
# Optimizer Adam phổ biến, Loss là Mean Squared Error (sai số bình phương trung bình)
model.compile(optimizer='adam', loss='mse', metrics=['mae'])
model.summary()

# 4. Training (Huấn luyện)
print("Starting Training...")
# EarlyStopping để tự động dừng sớm nếu AI không học thêm được gì mới, tránh tốn thời gian
early_stopping = tf.keras.callbacks.EarlyStopping(
    monitor='val_loss', 
    patience=5, 
    restore_best_weights=True
)

history = model.fit(
    X_train, y_train,
    epochs=50,
    batch_size=32,
    validation_data=(X_test, y_test),
    callbacks=[early_stopping],
    verbose=1
)

# 5. Save the Lightweight Model
model_path = os.path.join(data_dir, "lightweight_ram_lstm.keras")
model.save(model_path)
print(f"Model saved to: {model_path}")

# Evaluate on test set
test_loss, test_mae = model.evaluate(X_test, y_test, verbose=0)
print(f"Test Loss (MSE): {test_loss:.4f}")
print(f"Test MAE: {test_mae:.4f}")
