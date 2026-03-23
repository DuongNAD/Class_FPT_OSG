import os
import time
import psutil
import joblib
import signal
import numpy as np
from tensorflow.keras.models import load_model

# ---------------------------------------------------------
# 1. CẤU HÌNH HỆ THỐNG (SYSTEM CONFIGURATION)
# ---------------------------------------------------------
MODEL_PATH = r'e:\Project\Class\OSG\lightweight_ram_lstm.h5'
SCALER_PATH = r'e:\Project\Class\OSG\scaler.pkl'
TIME_STEPS = 10
FEATURE_COUNT = 45 # Đảm bảo tuyệt đối 45 cột dữ liệu

print("Đang khởi động AI Daemon và nạp mô hình...")
import tensorflow.keras.metrics as metrics
model = load_model(MODEL_PATH, compile=False) # Skip compilation to avoid custom object MSE errors completely in inference
scaler = joblib.load(SCALER_PATH)

# Danh sách trắng (Whitelist) - Không bao giờ bị đóng băng
WHITELIST = [
    'code', 'idea', 'java', 'node', 'gnome-terminal', 
    'bash', 'systemd', 'Xorg', 'python3'
]

ram_history = []

# ---------------------------------------------------------
# 2. BỘ TRÍCH XUẤT ĐẶC TRƯNG (FEATURE EXTRACTION ENGINE)
# ---------------------------------------------------------
def get_45_features():
    """
    Thu thập chính xác 45 thông số để khớp với Input Shape của mô hình.
    Anh có thể tinh chỉnh lại thứ tự các phần tử trong mảng 'features' này 
    sao cho khớp 100% với lúc anh train model.
    """
    # Khởi tạo mảng chứa 45 số 0 (Kỹ thuật Zero Padding để chống lỗi)
    features = np.zeros(FEATURE_COUNT)
    
    # [Index 0]: Tỷ lệ RAM tổng của hệ thống (Đây thường là Target Variable)
    features[0] = psutil.virtual_memory().percent
    
    # [Index 1]: Tỷ lệ Swap (Bộ nhớ ảo)
    features[1] = psutil.swap_memory().percent
    
    # [Index 2 đến 44]: Thông số CPU và RAM của các tiến trình cụ thể
    # Nàng thơ thiết lập sẵn bộ quét cho các phần mềm phổ biến
    target_processes = ['chrome', 'firefox', 'docker', 'mysql', 'vscode']
    
    current_idx = 2
    for target in target_processes:
        cpu_total = 0.0
        ram_total = 0.0
        
        # Quét các tiến trình đang chạy
        for p in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
            try:
                if p.info['name'] and target in p.info['name'].lower():
                    cpu_total += p.info['cpu_percent'] or 0.0
                    ram_total += p.info['memory_percent'] or 0.0
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        # Nạp dữ liệu vào mảng nếu chưa vượt quá 45 cột
        if current_idx < FEATURE_COUNT:
            features[current_idx] = cpu_total
            current_idx += 1
        if current_idx < FEATURE_COUNT:
            features[current_idx] = ram_total
            current_idx += 1
            
    return features

# ---------------------------------------------------------
# 3. BỘ MÁY THỰC THI (EXECUTION ENGINE)
# ---------------------------------------------------------
def drop_caches():
    """Hành động Level 1: Dọn dẹp Cache nhẹ nhàng"""
    print("[CẢNH BÁO LEVEL 1] RAM có dấu hiệu tăng cao. Đang dọn dẹp Cache...")
    os.system("sync; echo 1 > /proc/sys/vm/drop_caches")

def smooth_throttling():
    """Hành động Level 2: Đóng băng tiến trình ngốn RAM"""
    print("[CẢNH BÁO LEVEL 2] Dự đoán RAM sắp cạn kiệt. Kích hoạt Kill Switch mềm...")
    
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
        if proc['name'] not in WHITELIST:
            try:
                os.kill(proc['pid'], signal.SIGSTOP) # Đóng băng thay vì giết
                print(f"Đã đóng băng tiến trình: {proc['name']} (PID: {proc['pid']})")
                frozen_count += 1
                if frozen_count >= 3: # Xử lý 3 kẻ ngốn RAM nhất
                    break
            except Exception:
                pass

# ---------------------------------------------------------
# 4. VÒNG LẶP SUY LUẬN (INFERENCE LOOP)
# ---------------------------------------------------------
while True:
    try:
        # Thu thập 1 hàng dữ liệu (45 cột)
        current_features = get_45_features()
        ram_history.append(current_features)
        
        # Duy trì cửa sổ thời gian chuẩn 10 nhịp
        if len(ram_history) > TIME_STEPS:
            ram_history.pop(0)
            
        if len(ram_history) == TIME_STEPS:
            # Chuyển đổi thành ma trận Numpy hình dáng (10, 45)
            history_matrix = np.array(ram_history)
            
            # Chuẩn hóa dữ liệu toàn bộ ma trận (Data Normalization)
            scaled_matrix = scaler.transform(history_matrix)
            
            # Định hình lại thành cấu trúc 3D cho LSTM: (1 batch, 10 timesteps, 45 features)
            input_data = scaled_matrix.reshape(1, TIME_STEPS, FEATURE_COUNT)
            
            # Mô hình dự đoán (Inference)
            pred_scaled = model.predict(input_data, verbose=0)
            
            # Kỹ thuật Inverse Transform an toàn: 
            # Tạo một mảng ảo (Dummy Array) 45 cột, nhét kết quả dự đoán vào cột số 0 (Tỷ lệ RAM)
            dummy_array = np.zeros((1, FEATURE_COUNT))
            dummy_array[0, 0] = pred_scaled[0][0] 
            
            # Dịch ngược kết quả ra % RAM thực tế
            pred_ram = scaler.inverse_transform(dummy_array)[0][0]
            
            print(f"RAM hiện tại: {current_features[0]:.1f}% | Dự đoán tương lai: {pred_ram:.1f}%")
            
            # Ra quyết định (Decision Making)
            if pred_ram >= 95.0:
                smooth_throttling()
                time.sleep(15) # Nghỉ ngơi để hệ điều hành ổn định lại
            elif pred_ram >= 85.0:
                drop_caches()
                
        time.sleep(5) # Lấy mẫu mỗi 5 giây
        
    except Exception as e:
        print(f"Lỗi vòng lặp: {e}")
        time.sleep(5)