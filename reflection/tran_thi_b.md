# Bài Thu Hoạch Cá Nhân (Reflection)

- **Họ và Tên**: Trần Thị B
- **Mã Học Viên**: K4-1026
- **Vai trò trong nhóm**: Frontend Developer & UI/UX Designer
- **Hạng mục phụ trách**: Giao diện Web SPA (`codebase/public/`), Kéo thả upload đa file, Hiển thị Tab Transcript & Sub-tabs, Tìm kiếm từ khóa, Export Markdown/Slack/PDF, Khôi phục phiên làm việc qua `localStorage`.

---

## 1. Những Đóng Góp Chính Trong Hackathon
- Thiết kế giao diện Web 2 cột hiện đại theo tiêu chí Rich Aesthetics: Dark mode sang trọng, hiệu ứng Glassmorphism, typography Outfit/Inter và micro-animations mượt mà.
- Xây dựng vùng kéo thả file (Drag & Drop zone) hỗ trợ chọn cùng lúc tới 5 file audio kèm client-side validation kiểm tra số lượng và tổng dung lượng 300MB.
- Lập trình bộ công cụ Export đa dạng: Sao chép Markdown thô, Tải file `.md`, Định dạng copy chuẩn cho kênh chat Slack, và tính năng In trực tiếp ra bản PDF.
- Lập trình tính năng tìm kiếm từ khóa thông minh có highlight trực tiếp trên tab Transcript thô và cơ chế lưu trữ tự động `localStorage`.

---

## 2. Bài Học Rút Ra Về Thiết Kế Giao Diện AI (AI UX Principles)
1. **Minh bạch trạng thái và giảm lo âu cho người dùng (Progress Visibility)**: Việc xử lý audio và gọi LLM có thể tốn từ 15-45 giây. Việc thiết kế các Progress Spinner, thanh đếm thời gian thực và dòng chữ trạng thái chi tiết ("Đang chia nhỏ audio 10 phút...", "Đang chạy Map-Reduce LLM...") giúp người dùng kiên nhẫn và tin tưởng vào hệ thống.
2. **Nguyên tắc HAX G9 & PAIR Human Control**: Giao diện cần trao quyền kiểm soát linh hoạt cho người dùng (nút tóm tắt lại từ transcript gốc, nút copy/export nhanh) để họ không cảm thấy bị phụ thuộc vào một kết quả duy nhất của AI.

---

## 3. Tự Đánh Giá
- **Mức độ hoàn thành**: $100\%$ công việc được giao đúng tiến độ. Giao diện nhận được phản hồi rất tích cực từ người dùng trải nghiệm trong buổi CP5.
