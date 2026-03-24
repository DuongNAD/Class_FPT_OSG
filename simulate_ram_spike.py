import time
import psutil

# Script mô phỏng Tăng RAM an toàn để Demo dự án AI
# Hoạt động: Tự động ngốn RAM từ từ (100MB mỗi 1-2 giây)
# Cảnh báo an toàn: Giới hạn tự động dừng ngốn RAM khi máy đạt 90% để chống đơ máy.

print("="*60)
print("🚀 BẮT ĐẦU GIẢ LẬP TRÀN RAM (RAM SPIKE) CHO DEMO")
print("⚠️ Script sẽ dừng Cắm thêm RAM tự động khi đạt giới hạn 90%")
print("❌ Để kết thúc Demo và xả RAM: Nhấn Ctrl + C")
print("="*60)
time.sleep(2)

dummy_memory_blocks = []
block_size = 2000 * 1024 * 1024  # 2000 Megabytes (2GB 1 lần cắn)


try:
    while True:
        # Lấy thông số RAM hiện tại của máy
        mem_info = psutil.virtual_memory()
        current_percent = mem_info.percent
        
        # Ngưỡng an toàn (Tránh xanh màn hình hoặc đơ cứng máy)
        if current_percent >= 90.0:
            print(f"\\n🛑 CẢNH BÁO: RAM đã chạm mốc nguy hiểm ({current_percent}%).")
            print("🛑 Tạm dừng ngốn RAM để giữ cho máy còn thở!")
            print("👉 NHẤN [Ctrl + C] ĐỂ KẾT THÚC DEMO VÀ GIẢI PHÓNG TOÀN BỘ RAM")
            
            # Giữ nguyên vòng lặp để giữ bộ nhớ không bị giải phóng
            while True:
                time.sleep(1)
        
        # Nếu RAM chưa tới ngưỡng, tiếp tục nhồi dữ liệu rác (100MB) vào RAM
        try:
            # Tạo 1 mảng byte ảo ngốn exacly 100MB
            # bytearray rất hữu dụng để giữ tài nguyên bộ nhớ thực tế
            dummy_memory_blocks.append(bytearray(block_size))
            
            print(f"💥 Đã cắm thêm 2GB... [RAM hệ thống đang ở mức: {current_percent:.1f}%]")
            
            # Chờ 1.5 giây để Background AI Daemon kịp "ngửi" thấy sự thay đổi
            time.sleep(1.5)
            
        except MemoryError:
            print("\\n🔥 LỖI: Hết RAM cục bộ (Tràn bộ nhớ ứng dụng Python). Đang chờ lệnh... Nhấn Ctrl+C để thoát!")
            while True:
                time.sleep(1)

except KeyboardInterrupt:
    print("\\n" + "="*60)
    print("🧹 ĐÃ HUỶ GIẢ LẬP BỞI NGƯỜI DÙNG (CTRL+C)")
    print("🧹 Đang xả toàn bộ RAM...")
    
    # Kỹ thuật xả rác bộ nhớ tức thì
    dummy_memory_blocks.clear()
    
    # Cho máy tính vài giây để dọn rác System
    for i in range(3, 0, -1):
        print(f"🧹 Máy sẽ mát lại sau {i} giây...")
        time.sleep(1)
        
    print("✅ Đã giải phóng RAM thành công! Trở lại mức bình tĩnh.")
    print("="*60)
