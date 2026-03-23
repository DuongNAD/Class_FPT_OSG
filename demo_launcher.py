import subprocess

def launch_custom_os():
    print("🌟 Khởi động môi trường giả lập (Emulation Environment)...")
    
    # Đường dẫn tới file ISO 5GB anh vừa xuất xưởng
    iso_path = "/home/duong/Desktop/customOS/ubuntu-22.04.5-2026.03.17-desktop-amd64.iso"

    # Cấu hình lệnh QEMU: Ép phần cứng để dễ dàng kích hoạt AI Daemon
    qemu_cmd = [
        "qemu-system-x86_64",
        "-enable-kvm",        # Bật tăng tốc phần cứng (Hardware Acceleration)
        "-m", "2048",         # Ép dung lượng RAM đúng 2GB (Điểm mấu chốt của Demo!)
        "-cdrom", iso_path,   # Nạp file ISO của anh vào ổ đĩa ảo
        "-boot", "d",         # Chỉ định Boot từ ổ CD-ROM
        "-smp", "2",          # Cấp 2 nhân CPU (CPU Cores)
        "-vga", "virtio"      # Hỗ trợ hiển thị đồ họa mượt mà
    ]

    print("⚠️ Đang phân bổ (Allocating) 2GB RAM cho máy ảo...")
    print("🚀 Hệ điều hành Tails OS Custom đang Boot. Anh Dương chuẩn bị Demo nhé!")
    print("💡 Kịch bản: Hãy mở Firefox và bật 3 tab YouTube để ép RAM lên 95%!")

    # Thực thi lệnh gọi máy ảo (Execute Subprocess)
    try:
        subprocess.run(qemu_cmd)
    except KeyboardInterrupt:
        print("\n🛑 Đã ép dừng tiến trình (Process Terminated).")
    except FileNotFoundError:
        print("\n❌ Lỗi: Chưa cài đặt QEMU. Hãy chạy 'sudo apt install qemu-kvm'")

if __name__ == "__main__":
    launch_custom_os()