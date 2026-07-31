# Bài Thu Hoạch Cá Nhân (Reflection)

- **Họ và Tên**: Nguyễn Khánh Toàn
- **Mã Học Viên**: 2A202601738
- **Vai trò trong nhóm**: AI Prompt Engineer & Evaluation Lead
- **Hạng mục phụ trách**: Tối ưu Prompts (`codebase/summarizer.py`), Xây dựng Golden Set 20 cases (`eval/golden_set.json`), Báo cáo Đánh giá các lượt chạy (`eval/eval_results.md`).

---

## 1. Những Đóng Góp Chính Trong Hackathon

- Nghiên cứu và thiết kế bộ Prompts 2 giai đoạn cho kiến trúc Map-Reduce: **`CHUNK_MAP_PROMPT`** (giai đoạn Map tóm tắt đoạn nhỏ và sửa lỗi thuật ngữ AI) và **`REDUCE_AGGREGATE_PROMPT`** (giai đoạn Reduce tổng hợp Master Summary, Bảng Action Items và duy trì thẻ `<details>` đa file).
- Tích hợp từ điển chuẩn hóa thuật ngữ công nghệ tiếng Việt/Anh trực tiếp vào System Prompt để tự động sửa các lỗi nghe nhầm đặc trưng của Whisper (`RAG` -> "rác", `Llama` -> "làm ma", `API` -> "áp pi", `Fine-tuning` -> "bóp chim / phai tuning").
- Xây dựng bộ dữ liệu kiểm thử **Golden Set 20 cases** chuẩn hóa và tiến hành đánh giá qua 3 lượt chạy, nâng tỷ lệ Pass Rate từ $65.0\%$ lên **$90.0\%$**, vượt chỉ tiêu Quality Bar của nhóm.

---

## 2. Bài Học Rút Ra Về Prompt Engineering & Evaluation

1. **Prompt không phải là ma thuật, Prompt là quy chuẩn giao tiếp (Structured Output Enforcement)**: Để LLM trả về đúng bảng Markdown và không bỏ sót file khi tóm tắt batch 5 file audio, việc đưa ra các constraint rõ ràng cùng mẫu ví dụ cấu trúc HTML/Markdown trong Prompt có vai trò quyết định $90\%$ sự thành công.
2. **Tầm quan trọng của Golden Set**: Không thể cải tiến Prompt nếu không có bộ đo lường định lượng. Việc đánh giá qua 20 cases cụ thể giúp tôi phát hiện ngay lỗi "chỉ tóm tắt file cuối cùng" ở lượt chạy 1 để kịp thời điều chỉnh Prompt cho lượt chạy 2 và 3.

---

## 3. Tự Đánh Giá

- **Mức độ hoàn thành**: Hoàn thành xuất sắc nhiệm vụ Prompter và Evaluation.
- **Kỷ niệm đáng nhớ**: Khoảnh khắc khi Prompt Map-Reduce sửa thành công từ "rác pipeline" thành "RAG pipeline" trong buổi test lượt 3.
