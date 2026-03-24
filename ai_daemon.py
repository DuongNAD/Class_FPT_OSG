import os
import time
import psutil
import json
import signal
import subprocess
import platform
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

# ---------------------------------------------------------
# 1. CẤU HÌNH HỆ THỐNG (SYSTEM CONFIGURATION)
# ---------------------------------------------------------
# Cơ chế Fallback (Tự động nhận diện môi trường chạy)
if os.path.exists('lightweight_ram_lstm.keras'):
    MODEL_PATH = 'lightweight_ram_lstm.keras'
    SCALER_PATH = 'scaler_config.json'
else:
    MODEL_PATH = '/opt/ai-ram-manager/lightweight_ram_lstm.keras'
    SCALER_PATH = '/opt/ai-ram-manager/scaler_config.json'

TIME_STEPS = 5 # Changed from 10 to 5 for 2x faster reaction time
FEATURE_COUNT = 1 

print("Đang khởi động AI Daemon và nạp mô hình...")

# Dựng khung xương AI thủ công để tránh lỗi phiên bản Keras
model = Sequential()
model.add(Dropout(0.2, input_shape=(TIME_STEPS, FEATURE_COUNT)))
model.add(LSTM(32, return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(16))
model.add(Dense(1))

# Nạp linh hồn (Weights) vào khung xương
model.load_weights(MODEL_PATH)

# Nạp bộ chuẩn hóa dữ liệu từ JSON (Zero-dependency approach)
with open(SCALER_PATH, 'r') as f:
    scaler_params = json.load(f)

# Phục hồi mảng Data Min và Data Max thành Numpy arrays
data_min = np.array(scaler_params["data_min"])
data_max = np.array(scaler_params["data_max"])
# Đã sửa lại mặc định là 0 vì features[0] đang giữ giá trị mem.percent
target_idx = scaler_params.get("target_idx", 0)

WHITELIST = [
    'code', 'idea', 'java', 'node', 'gnome-terminal',
    'bash', 'systemd', 'Xorg', 'python3',
    'gnome-shell', 'wayland', 'dbus-daemon', 'pulseaudio', 'pipewire', 'vmtoolsd'
]

ram_history = []

# ---------------------------------------------------------
# 2. BỘ TRÍCH XUẤT ĐẶC TRƯNG (FEATURE EXTRACTION ENGINE)
# ---------------------------------------------------------
def get_numerical_features():
    features = np.zeros(FEATURE_COUNT)
    mem = psutil.virtual_memory()
    features[0] = mem.percent
    return features

# ---------------------------------------------------------
# 3. BỘ MÁY THỰC THI (EXECUTION ENGINE)
# ---------------------------------------------------------
def drop_caches():
    print("[CẢNH BÁO LEVEL 1] RAM có dấu hiệu tăng cao. Đang dọn dẹp Cache...")
    try:
        os.system("sync; echo 1 > /proc/sys/vm/drop_caches")
    except:
        pass

def get_foreground_pid():
    # Nhận diện PID của cửa sổ ứng dụng người dùng đang tương tác
    try:
        sys_os = platform.system()
        if sys_os == 'Windows':
            import ctypes
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            pid = ctypes.c_ulong()
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            return int(pid.value)
        elif sys_os == 'Linux':
            output = subprocess.check_output(['xdotool', 'getactivewindow', 'getwindowpid'], stderr=subprocess.DEVNULL)
            return int(output.strip())
    except Exception:
        return -1
    return -1

def smooth_throttling():
    print("[CẢNH BÁO LEVEL 2] Dự đoán RAM sắp cạn kiệt. Kích hoạt Khoá an toàn...")
    active_pid = get_foreground_pid()
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
        try:
            if proc.info['memory_percent'] is not None:
                processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
            
    processes = sorted(processes, key=lambda x: x['memory_percent'], reverse=True)
    
    frozen_count = 0
    for proc in processes:
        # BỎ QUA nếu đây là ứng dụng người dùng đang mở sáng nhất (Foreground)
        if proc['pid'] == active_pid:
            print(f"🛡️ BỎ QUA (Context-aware): Bảo vệ phần mềm đang dùng - {proc['name']} (PID: {proc['pid']})")
            continue
            
        if proc['name'] not in WHITELIST:
            try:
                os.kill(proc['pid'], signal.SIGSTOP)
                print(f"Đã đóng băng tiến trình: {proc['name']} (PID: {proc['pid']})")
                frozen_count += 1
                if frozen_count >= 3:
                    break
            except Exception:
                pass

# ---------------------------------------------------------
# 4. VÒNG LẶP SUY LUẬN (INFERENCE LOOP)
# ---------------------------------------------------------
while True:
    try:
        current_features = get_numerical_features()
        ram_history.append(current_features)
        
        if len(ram_history) > TIME_STEPS:
            ram_history.pop(0)
            
        if len(ram_history) == TIME_STEPS:
            history_matrix = np.array(ram_history)

            epsilon = 1e-8
            scaled_matrix = (history_matrix - data_min) / (data_max - data_min + epsilon)
            
            input_data = scaled_matrix.reshape(1, TIME_STEPS, FEATURE_COUNT)
            pred_scaled = model.predict(input_data, verbose=0)

            pred_ram = pred_scaled[0][0] * (data_max[target_idx] - data_min[target_idx]) + data_min[target_idx]
            
            print(f"RAM hiện tại: {current_features[target_idx]:.1f}% | Dự đoán tương lai: {pred_ram:.1f}%")

            if pred_ram >= 80.0 and current_features[target_idx] >= 50.0:
                smooth_throttling()
                time.sleep(15) 
            elif pred_ram >= 70.0 and current_features[target_idx] >= 40.0:
                drop_caches()
                
        time.sleep(2)
        
    except Exception as e:
        print(f"Lỗi vòng lặp: {e}")
        time.sleep(2)
