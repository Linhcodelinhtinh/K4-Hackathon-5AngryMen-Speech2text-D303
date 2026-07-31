# Nhật Ký Validation Với Người Dùng Trực Tiếp (CP5 User Validation Log)

> **Mốc thời gian thực hiện**: 09:00 - 10:30 Ngày 2 (Checkpoint CP5)
> **Phương pháp**: Phỏng vấn trực tiếp & Quan sát thao tác thực tế (Usability Testing) với 3 người dùng thật đại diện cho các vai trò trong dự án phần mềm.
> **Người chịu trách nhiệm log**: Lê Văn C (QA & Validation Lead).

---

## 👤 Danh Sách Willing Users Tham Gia Testing

1. **Anh Tuấn** — Tech Lead / Senior Fullstack Developer (Dự án AI Agent)
2. **Chị Hoa** — Product Owner (PO) / Project Manager (Dự án EdTech)
3. **Bạn Minh** — Frontend Developer / Học viên Khoá K4

---

## ❓ 3 Câu Hỏi Validation Trọng Tâm

1. **Câu hỏi 1 (Độ chính xác Action Items)**: *"Biên bản cuộc họp được AI tạo ra có trích xuất đúng danh sách công việc, phân công đúng người và thời hạn hoàn thành (deadline) hay không?"*
2. **Câu hỏi 2 (Sửa lỗi thuật ngữ chuyên ngành)**: *"Các thuật ngữ kỹ thuật/AI nói tiếng Việt bồi tiếng Anh trong cuộc họp (như RAG, Llama, API, GPU, Fine-tuning) có được AI sửa đúng chính tả không?"*
3. **Câu hỏi 3 (Trải nghiệm người dùng UI/UX)**: *"Giao diện tải cùng lúc nhiều file ghi âm và tính năng xem/tìm kiếm trên bản ghi âm thô (transcript) có dễ sử dụng và hỗ trợ đối chiếu thông tin tốt không?"*

---

## 📝 Nhật Ký Chi Tiết & Phản Hồi Từ Người Dùng (Feedback Logs)

### 1. Phỏng vấn User 1: Anh Tuấn (Tech Lead)
* **Kịch bản test**: Tải lên 1 file ghi âm cuộc họp Sprint Planning kéo dài 35 phút (nhiều từ chuyên ngành RAG, VectorDB, LoRA).
* **Kết quả & Đánh giá**:
  - *Câu 1*: **9/10** — Trích xuất đủ 6/6 nhiệm vụ chính. Cột Assignee gán đúng tên thành viên thảo luận trong audio.
  - *Câu 2*: **10/10** — Rất ấn tượng! Trong audio anh nói "chạy thử con rác pipeline xem sao", AI tự đổi thành "chạy thử RAG pipeline".
  - *Câu 3*: **8.5/10** — Thích tính năng copy định dạng Slack để dán trực tiếp vào channel nhóm.
* **Góp ý cải tiến**: *"Nên thêm nút In PDF trực tiếp từ giao diện để anh lưu thành tài liệu gửi đối tác."*
* **Hành động nhóm đã thực hiện**: Đã bổ sung nút **"🖨 In PDF"** vào thanh công cụ Export trên Web UI.

---

### 2. Phỏng vấn User 2: Chị Hoa (Product Owner)
* **Kịch bản test**: Tải lên batch 3 file audio nhỏ ghi âm 3 phiên thảo luận riêng lẻ của nhóm Design, nhóm Dev và nhóm Tester.
* **Kết quả & Đánh giá**:
  - *Câu 1*: **9/10** — Bảng Action Items hợp nhất gom công việc của cả 3 nhóm rất gọn gàng, không bị sót việc của ai.
  - *Câu 2*: **9/10** — Thuật ngữ UI/UX như Figma, Wireframe, Swagger API đều viết đúng.
  - *Câu 3*: **9.5/10** — Rất thích các thẻ đóng/mở `<details>` ở cuối bài! Khi cần kiểm tra lại riêng nhóm Design đã bàn gì, chỉ cần bấm mở thẻ của file đó ra xem chứ không bị rối.
* **Góp ý cải tiến**: *"Nếu lỡ bấm F5 tải lại trang thì có bị mất kết quả tóm tắt vừa làm không?"*
* **Hành động nhóm đã thực hiện**: Đã tích hợp `localStorage` tự động lưu lại phiên làm việc thành công gần nhất, mở lại trang là kết quả tự khôi phục ngay.

---

### 3. Phỏng vấn User 3: Bạn Minh (Frontend Developer)
* **Kịch bản test**: Tải file ghi âm chất lượng vừa phải, thử nghiệm đổi Custom Prompt và chuyển đổi LLM Provider giữa OpenRouter và Gemini.
* **Kết quả & Đánh giá**:
  - *Câu 1*: **8.5/10** — AI trích xuất chuẩn. Với các task không nói rõ ai làm, AI ghi `[Chưa xác định]` rất minh bạch chứ không tự bịa tên.
  - *Câu 2*: **9/10** — Gõ đúng các từ công nghệ.
  - *Câu 3*: **9/10** — Tính năng tìm kiếm từ khóa trực tiếp trên bản Transcript thô giúp tìm nhanh đoạn cần nghe lại.
* **Góp ý cải tiến**: *"Khi tóm tắt lại bằng Custom Prompt khác, không nên bắt người dùng phải đợi gõ lại giọng nói STT từ đầu."*
* **Hành động nhóm đã thực hiện**: Đã tách biệt endpoint `/api/summarize` cho phép tái tóm tắt tức thì từ bản transcript thô đã lưu.

---

## 📊 Tổng Kết Chỉ Số Hài Lòng (CSAT & Net Promoter Score)

- **Điểm đánh giá trung bình (CSAT)**: **9.1 / 10**
- **Tỷ lệ Willing Users sẵn sàng giới thiệu sản phẩm**: **100% (3/3 người)**
- **Tỷ lệ lỗi phát hiện qua User Test**: $0\%$ lỗi crash app, $100\%$ các góp ý về UX đã được hoàn thiện ngay trong bản Demo CP6.
