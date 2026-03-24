# TÀI LIỆU BẢO VỆ ĐỒ ÁN: Ý TƯỞNG & QUÁ TRÌNH HUẤN LUYỆN MÔ HÌNH (LSTM)

Tài liệu này dùng để trả lời vấn đáp khi Giáo viên đặt câu hỏi về các quyết định thiết kế (Design Decisions) trong hệ thống AI dự báo tràn RAM.

---

## 1. Ý tưởng cốt lõi của Model là gì?
Máy tính đơ (Freeze) không phải do RAM tự dưng tăng đột biến ở 1 giây nào đó, mà do 1 "quãng tích tụ" trước khi chạm mốc 100%. 
*   **Ý tưởng Logic:** Xây dựng một AI có khả năng "đọc vị" đường dốc của RAM (đang từ từ đi lên hay bất ngờ vọt thẳng đứng).
*   **Tại sao lại chọn kiến trúc LSTM (Long Short-Term Memory)?** Các phần mềm truyền thống (như Task Manager) chỉ lấy chỉ số tĩnh của **thực tại**. Còn mạng LSTM sinh ra để ghi nhớ **quá khứ**. AI của chúng ta dùng bộ nhớ dài hạn của LSTM để so sánh các nhịp đập 10 giây trước với hiện tại, từ đó dự báo chính xác tương lai 1 giây sau xem RAM có tiếp tục dốc lên quỹ đạo nguy hiểm không để vát còi cảnh báo trước.
*   **Mô hình siêu nhẹ (Lightweight):** Để một AI làm nhiệm vụ "giám sát hệ điều hành", bản thân nó không được phép... ngốn hệ điều hành. Model được lược giản tối đa xuống chỉ còn khối nơ-ron: `32 Unit -> 16 Unit`, đảm bảo Daemon (`ai_daemon.py`) chạy 24/7 nhưng chi phí CPU gần như = 0.

## 2. Model được Train (Huấn luyện) như thế nào?
Để AI học được cách dự đoán, nhóm không nạp nguyên bảng Excel trực tiếp. Quá trình huấn luyện trải qua các bước tinh tế sau:

*   **B1. Khử biến gộp (Univariate Time-Series):** Bỏ qua mọi cột CPU, tên ứng dụng rác, Byte tuyệt đối. Mọi thứ được ép về 1 trục duy nhất là tỷ lệ **`ram_percent`**. Model được dạy cách tập trung tuyệt đối vào đường dốc của % RAM.
*   **B2. MinMaxScaler:** Dữ liệu tỷ lệ (0 - 100%) được thuật toán chuẩn hóa MinMax nén về lõi Toán học từ `0.0` đến `1.0`. Giúp mạng Nơ-ron (vốn nhạy cảm với con số) tính toán Gradient nhạy bén hơn.
*   **B3. Kỹ thuật "Cửa sổ trượt" (Sliding Window):** Đây là linh hồn của hệ thống. Nhóm setup `look_back = 5`. Có nghĩa là mô hình không học từng dòng riêng lẻ mà nạp theo khối **5 dòng một (tương đương 5 nhịp thời gian)**. Nó vừa nhìn `t1, t2, t3, t4, t5` để học cách dự đoán `t6`. Nhờ thế AI mới phản xạ siêu tốc khi bạn mở ứng dụng nặng.
*   **B4. Hàm phạt (Loss Function - MSE):** Model được luyện bằng hàm sai số *Mean Squared Error*. Hàm này cứ thấy AI dự đoán chệch nhịp khi RAM Spike là nó khuếch đại hình phạt lên theo số mũ. Ép AI phải đặc biệt nhạy cảm để gào lên báo động ở các khúc cua gắt (khi bạn mở nhiều tab).

## 3. Tại sao lại dùng file dataset `ram_dataset_augmented.csv`?
Khi thầy giáo hỏi *"Tại sao lại bỏ file Preprocessed cũ (hoặc file gốc) mà lại dùng file csv này?"*, câu trả lời rớt điểm tuyệt đối là:
*   **Xóa bỏ thiên lệch hệ điều hành (Oracle Paradox):** File Gốc bị lỗi chết người là dữ liệu "Ảo". Khi dùng file gốc, cứ RAM dâng cao là Windows tự động dọn rác ngầm làm file tụt xuống. AI học từ đó nên nghĩ rằng "RAM lên cao thì tự nhiên sẽ tụt xuống an toàn". Điều này dẫn tới thảm hoạ AI dự đoán láo (Accuracy 100.8%).
*   **Thêm nhiễu đa biên độ (Data Augmentation):** File `...augmented.csv` là thành quả trí tuệ. Nhóm đã vứt đi các dữ liệu lỗi, rồi lập trình file `augment_data.py`. File này đem trộn 3 bộ dữ liệu máy tính khác nhau vào, rồi dùng Toán học tạo ra độ nhiễu loạn ngẫu nhiên tiêm vào file (Gaussian Noise). Lượng Data được x3, AI học đầy đủ mọi hỉ nộ ái ố của tài nguyên máy tính, chống được bệnh học vẹt (Overfitting) mà file cũ mắc phải.
*   **Tính độc lập Phần cứng:** Nhờ vứt bỏ các file cũ gắn liền dung lượng dung lượng (Byte). File `augmented` chỉ dùng cấu trúc phần trăm. Đem mô hình đi kiểm thử ở máy tính yếu RAM 4GB hay Desktop xịn 64GB, 90% bị đầy luôn giữ trọn ý nghĩa vẹn nguyên!
