# Bài Thu Hoạch Cá Nhân (Reflection)

- **Họ và Tên**: Lưu Quang Linh
- **Mã Học Viên**: K4-1024
- **Vai trò trong nhóm**: Group Leader / Backend Developer & System Architect
- **Hạng mục phụ trách**: `spec.md`, Kiến trúc FastAPI Backend (`codebase/api/index.py`), Parallel Audio Chunking (`codebase/stt_service.py`), Serverless Vercel Deployment.

---

## 1. Những Đóng Góp Chính Trong Hackathon
Trong 1.5 ngày diễn ra Mini Hackathon AI Batch 03, tôi đã đảm nhận vị trí Trưởng nhóm và Kiến trúc sư hệ thống:
- Chủ trì xây dựng tài liệu **AI Spec (`spec.md`)** chuẩn 8 phần, định hình rõ lát cắt sản phẩm, bài toán JTBD và Quality Bar cho cả nhóm.
- Lập trình module **`stt_service.py`**: Thiết kế thuật toán chia cắt file âm thanh lớn hơn 24MB thành các đoạn 10 phút sử dụng `pydub` và `static-ffmpeg` (giúp chạy out-of-the-box trên cả Windows/Linux mà không cần cài FFmpeg thủ công), xử lý gõ chữ song song qua `ThreadPoolExecutor` với Groq Whisper Large V3.
- Phát triển **FastAPI Backend (`api/index.py`)**: Xây dựng 3 RESTful endpoints (`/api/transcribe`, `/api/summarize`, `/api/process`), xử lý validate file, quản lý API Key đa nhà cung cấp và xử lý lỗi tiếng Việt thân thiện (`parse_and_raise_error`).
- Đóng gói và cấu hình triển khai Serverless trên hạ tầng Vercel (`vercel.json`).

---

## 2. Bài Học Kỹ Thuật & Tư Duy Sản Phẩm AI Trút Ra Được
1. **Tư duy Lát cắt mỏng (Vertical Slice) & Cost of Error**: Khi xây dựng sản phẩm AI, bài toán quan trọng nhất không phải là mô hình hoành tráng đến đâu mà là việc kiểm soát chi phí của sự sai sót (Cost of Error). Việc lựa chọn mức tự động hóa `Augment` thay vì `Automate` hoàn toàn giúp người dùng giữ vai trò người duyệt (Human-in-the-loop), vừa tiết kiệm nguồn lực vừa đảm bảo độ tin cậy.
2. **Kỹ thuật Xử lý Giới hạn API (Bypassing API Limits)**: Việc gặp rào cản 24MB của Groq Whisper và Context Window của LLM đã dạy cho tôi bài học quý giá về kiến trúc chia để trị (Divide and Conquer): kết hợp **Audio Parallel Chunking** ở tầng âm thanh và **Map-Reduce Summarization** ở tầng văn bản.
3. **Multi-provider Fallback Pattern**: Thiết kế hệ thống linh hoạt có khả năng tự động fallback từ OpenRouter sang Groq và Gemini giúp ứng dụng hoạt động cực kỳ ổn định, không bị gián đoạn kể cả khi gặp lỗi Rate Limit (429) trong buổi Demo.

---

## 3. Tự Đánh Giá & Hướng Phát Triển Tiếp Theo
- **Mức độ hoàn thành công việc**: $100\%$ các mục tiêu kiến trúc và phân công đã đề ra.
- **Kế hoạch nâng cấp**: Trong phiên bản tiếp theo, tôi dự định tích hợp thêm bước lọc nhiễu tín hiệu âm thanh (Voice Activity Detection - VAD) và bổ sung tính năng tự động ghi nhận ý kiến phát biểu theo từng diễn giả (Speaker Diarization).
