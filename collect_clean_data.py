import psutil
import time
import os
import csv
from datetime import datetime

# Số lượng đặc trưng: 6 hệ thống + 10x2 của các tiến trình = 26 cột?
# Chú ý: Code này lưu đúng format 47 cột cũ (1 timestamp + 6 hệ thống + 10x4 số liệu tiến trình)
# Để file preprocess_data.py trên Windows vẫn đọc được mượt mà!

OUTPUT_FILE = 'ram_dataset_clean.csv'

def get_snapshot():
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    row = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_ram': mem.total,
        'available_ram': mem.available,
        'used_ram': mem.used,
        'ram_percent': mem.percent,
        'swap_used': swap.used,
        'swap_percent': swap.percent
    }
    
    processes = []
    for proc in psutil.process_iter(['name', 'memory_info', 'cpu_percent']):
        try:
            if proc.info['memory_info'] is not None:
                processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
            
    # Lấy Top 10 tiến trình tốn RAM nhất
    processes = sorted(processes, key=lambda x: x['memory_info'].rss if x['memory_info'] else 0, reverse=True)[:10]
    
    for i, proc in enumerate(processes):
        idx = i + 1
        row[f'proc_{idx}_name'] = proc['name']
        row[f'proc_{idx}_rss'] = proc['memory_info'].rss if proc['memory_info'] else 0
        row[f'proc_{idx}_vms'] = proc['memory_info'].vms if proc['memory_info'] else 0
        row[f'proc_{idx}_cpu'] = proc['cpu_percent'] or 0.0
        
    # Đảm bảo đủ 10 tiến trình (nếu máy đang chạy ít tiến trình thì điền số 0)
    for i in range(len(processes), 10):
        idx = i + 1
        row[f'proc_{idx}_name'] = 'N/A'
        row[f'proc_{idx}_rss'] = 0.0
        row[f'proc_{idx}_vms'] = 0.0
        row[f'proc_{idx}_cpu'] = 0.0
        
    return row

print(f"Đang thu thập dữ liệu SẠCH (Cứ 5s lưu 1 dòng) vào: {OUTPUT_FILE}")
print("Vui lòng mở thật nhiều Tab để RAM vượt 90%, sau đó đóng bớt Tab để AI học được chu kỳ lên xuống tự nhiên!")

# Tạo file và Header
first_snapshot = get_snapshot()
headers = list(first_snapshot.keys())

with open(OUTPUT_FILE, mode='w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()

# Vòng lặp thu thập (Nhấn Ctrl+C để dừng)
try:
    while True:
        snap = get_snapshot()
        with open(OUTPUT_FILE, mode='a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writerow(snap)
            
        print(f"[{snap['timestamp']}] Xong 1 dòng - RAM đang ở mức: {snap['ram_percent']}%")
        time.sleep(5)
except KeyboardInterrupt:
    print("\nĐã dừng thu thập dữ liệu thành công!")
