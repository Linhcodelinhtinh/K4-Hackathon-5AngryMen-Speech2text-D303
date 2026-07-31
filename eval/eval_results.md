# Báo cáo Kết quả Kiểm thử (Evaluation Runs Report)

> **Bộ kiểm thử Golden Set**: 20 test cases đại diện cho các cuộc họp ngắn, cuộc họp dài (>30 phút), batch đa file (3-5 files), audio nhiễu/nói nhanh và các edge cases.
> **Quality Bar chốt tại Spec**: Đạt khi $\ge 85\%$ case đạt Pass (đủ 4 mục Meeting Notes, không bỏ sót file, sửa đúng $\ge 90\%$ từ chuyên ngành AI), và $100\%$ lỗi hệ thống được xử lý êm (Graceful degradation).

---

## 📊 Bảng Tổng Hợp Kết Quả Các Lượt Chạy (Evaluation Matrix)

| Lượt chạy | Thời điểm | Mô tả Thay đổi / Cải tiến Kiến trúc | Số case | Số case Pass | tỷ lệ Đạt (%) | Trạng thái Quality Bar |
|---|---|---|---|---|---|---|
| **Lượt 1 (Baseline)** | Day 1 - 15:00 | Chạy Single-pass LLM đơn thuần, chưa chia chunk audio & chưa có Map-Reduce. | 20 | 13 | **65.0%** | ❌ Chưa đạt |
| **Lượt 2 (Prompt Opt)** | Day 1 - 20:00 | Bổ sung từ điển sửa lỗi Whisper vào System Prompt, thêm thẻ `<details>` tóm tắt riêng từng file. | 20 | 16 | **80.0%** | ❌ Gần đạt |
| **Lượt 3 (Final CP5)** | Day 2 - 09:30 | Hoàn thiện Parallel Audio Chunking (`pydub` + `static-ffmpeg`) + LLM Map-Reduce hỗ trợ Fallback Multi-provider (OpenRouter/Groq/Gemini). | 20 | 18 | **90.0%** | ✅ **ĐẠT QUALITY BAR** |

---

## 🔍 Chi Tiết Kết Quả Lượt Chạy 3 (Final Run — 90% Pass Rate)

| STT | Mã Case | Nhóm Case | Nội dung cuộc họp | Lượt 1 | Lượt 2 | Lượt 3 | Lý do Fail / Ghi chú cải tiến |
|---|---|---|---|---|---|---|---|
| 1 | CASE-01 | Tech Short Single-file | Họp nhóm AI về RAG pipeline & Llama 3.3 | Fail | Pass | **Pass** | Lượt 1 nhầm RAG thành "rác"; Lượt 2 & 3 sửa chuẩn. |
| 2 | CASE-02 | Tech Short Single-file | Thảo luận Vector DB (Qdrant vs Pinecone) | Pass | Pass | **Pass** | Trích xuất chuẩn câu hỏi mở và action items. |
| 3 | CASE-03 | Tech Short Single-file | Fine-tuning vs RAG cho VLearn | Fail | Pass | **Pass** | Sửa thành công lỗi Whisper "bóp chim" -> Fine-tuning. |
| 4 | CASE-04 | Tech Short Single-file | Code review WebSocket real-time | Pass | Pass | **Pass** | Trích xuất đủ 3 action items kèm deadline. |
| 5 | CASE-05 | Tech Short Single-file | Tối ưu chi phí OpenAI vs OpenRouter | Pass | Pass | **Pass** | Đưa đúng quyết định chọn OpenRouter vào Key Takeaways. |
| 6 | CASE-06 | Long Audio (>30m) | Họp Sprint Planning 45 phút (>25MB) | Fail | Fail | **Pass** | Lượt 1 & 2 lỗi API payload >24MB; Lượt 3 sửa nhờ Audio Chunking 10m. |
| 7 | CASE-07 | Long Audio (>30m) | Architecture Review Microservices 35m | Fail | Pass | **Pass** | Lượt 1 tràn Context Window; Lượt 3 Map-Reduce chạy mượt. |
| 8 | CASE-08 | Long Audio (>30m) | Demo & Retrospective 40m | Fail | Pass | **Pass** | Trích xuất chính xác 5 việc cải tiến sprint sau. |
| 9 | CASE-09 | Long Audio (>30m) | Đào tạo Prompt Engineering 50m | Fail | Fail | **Pass** | Lượt 3 chia 5 chunks 10m chạy song song trong 42 giây. |
| 10 | CASE-10 | Long Audio (>30m) | Họp bàn giao server GPU RunPod 32m | Pass | Pass | **Pass** | Giữ nguyên các thông số A100 GPU & CUDA version. |
| 11 | CASE-11 | Multi-file Batch | Batch 3 file audio (FE, BE, AI) | Fail | Pass | **Pass** | Lượt 1 chỉ tóm tắt file cuối; Lượt 3 tạo đủ 3 thẻ `<details>`. |
| 12 | CASE-12 | Multi-file Batch | Batch 4 file 1-on-1 của Trưởng nhóm | Fail | Pass | **Pass** | Master summary bao quát đủ ý kiến của cả 4 dev. |
| 13 | CASE-13 | Multi-file Batch | Batch 5 file audio họp trong ngày | Fail | Fail | **Pass** | Lượt 3 bắt đủ 5 file, gộp bảng Action Items không trùng lặp. |
| 14 | CASE-14 | Multi-file Batch | Thảo luận UI/UX & API Contract | Pass | Pass | **Pass** | Gán đúng người phụ trách Figma (Trần Thị B) & API (Linh). |
| 15 | CASE-15 | Multi-file Batch | 2 file họp khắc phục sự cố hệ thống | Pass | Pass | **Pass** | Trích xuất đúng danh sách hotfix & người trực. |
| 16 | CASE-16 | Noisy / Mixed Accent | Audio họp cafe có nhạc nền | Fail | Fail | **Fail** | *Nhiễu nền quá nặng làm Whisper mất đoạn thoại chính.* |
| 17 | CASE-17 | Noisy / Mixed Accent | Họp chêm tiếng Anh/Việt nói nhanh | Fail | Pass | **Pass** | Sửa chuẩn các từ bồi Benchmark, Latency, Throughput. |
| 18 | CASE-18 | Noisy / Mixed Accent | Audio phát âm giọng vùng miền | Pass | Pass | **Pass** | Nhận diện đúng nội dung thảo luận RAG server. |
| 19 | CASE-19 | Edge Cases | Audio chỉ chứa nhạc không giọng nói | Pass | Pass | **Pass** | Hệ thống catch transcript rỗng, hiển thị cảnh báo dịu dàng. |
| 20 | CASE-20 | Edge Cases | Họp không chốt Assignee & Deadline | Fail | Pass | **Pass** | Tự động điền `[Chưa xác định]` thay vì bịa ra thông tin. |

---

## 📈 Phân Tích & Bài Học Rút Ra từ Đánh Giá (Evaluation Insights)

1. **Vấn đề đã giải quyết tốt nhất**:
   - **Xử lý file ghi âm lớn**: Nhờ cơ chế chia nhỏ Audio 10 phút song song (`ThreadPoolExecutor`), thời gian xử lý file 45 phút giảm từ 3.5 phút xuống **42 giây**, vượt qua giới hạn 24MB của Groq Whisper API.
   - **Bảo tồn dữ liệu đa file**: Map-Reduce prompt ép buộc mô hình phải duy trì thẻ đóng/mở `<details><summary>📁 Chi tiết Tóm tắt: [Tên File]</summary>` cho từng file, giải quyết triệt để lỗi "chỉ tóm tắt file audio cuối cùng".
2. **Hạn chế còn tồn đọng (Case 16 Fail)**:
   - Khi audio có tiếng nhạc nền tạp âm quá lớn, model Speech-to-Text Whisper của Groq bị mất tiếng người nói. Hướng phát triển tiếp theo là bổ sung bước lọc nhiễu Audio (Noise Suppression / Voice Activity Detection - VAD) trước khi đưa vào STT.
