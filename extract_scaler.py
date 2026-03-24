import joblib
import json

# Tải mô hình đã được huấn luyện (Pre-trained scaler)
scaler = joblib.load('minmax_scaler.pkl')

# Rút trích giới hạn trên và dưới, chuyển từ mảng Numpy sang danh sách chuẩn (Standard list)
scaler_params = {
    "data_min": scaler.data_min_.tolist(),
    "data_max": scaler.data_max_.tolist(),
    "target_idx": 0 # ram_percent is at index 0 now
}

# Đóng gói và lưu trữ an toàn (Safe storage)
with open('scaler_config.json', 'w') as f:
    json.dump(scaler_params, f, indent=4)

print("Đã trích xuất thành công! File scaler_config.json đã sẵn sàng.")