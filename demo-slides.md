# Slide Thuyết Trình Demo Sản Phẩm (Demo Slides Outline — 6 Trang)

> **Dự án**: Kute AI Meeting Notes
> **Nhóm**: Nhóm 05 — 5AngryMen (Zone D303)

---

## 📌 SLIDE 1: Bài Toán & Bằng Chứng Nỗi Đau (Problem & Evidence)
- **Problem Statement**: Người quản lý dự án công nghệ mất 1.5 - 2 giờ mỗi ngày để nghe lại ghi âm cuộc họp dài hoặc tổng hợp từ nhiều file audio rải rác.
- **Evidence Mining ($n=35$)**:
  - **88.6%** xác nhận mất >45 phút/cuộc họp để ghi chép thủ công.
  - **82.8%** phàn nàn các công cụ gõ tự động hiện tại ghi sai hoàn toàn các thuật ngữ chuyên ngành tiếng Việt/Anh ("RAG" -> "rác", "Llama" -> "làm ma").
- **Core JTBD**: Muốn nhận ngay biên bản họp chuẩn hóa và bảng phân công công việc chính xác mà không phải tốn 1-2 tiếng nghe lại audio.

---

## 📌 SLIDE 2: Giải Pháp Kute AI Meeting Notes & Lát Cắt
- **Lát cắt 1 CÂU**: Một Tech Lead tải lên chuỗi 1-5 file audio cuộc họp nặng tới 300MB, AI tự động chia nhỏ audio, transcribe và chạy Map-Reduce LLM sửa lỗi thuật ngữ công nghệ, xuất ra Biên bản cuộc họp Markdown hoàn chỉnh kèm bảng Action Items và chi tiết từng file.
- **Mức Prototype**: `Working 100%` (Backend FastAPI + Frontend Vanilla JS + Live LLM API).
- **Mức Tự Động Hóa**: `Augment` — AI tạo bản thảo biên bản họp, người dùng xem lại, chỉnh sửa prompt và copy/export kết quả.

---

## 📌 SLIDE 3: Kiến Trúc Kỹ Thuật (System Architecture)
```
Audio Files (1-5 files, ≤300MB)
       │
       ▼
[Audio Parallel Chunking] ── (Split 10-min chunks via pydub/static-ffmpeg)
       │
       ▼
[STT: Groq Whisper Large V3] ── (Parallel transcription)
       │
       ▼
[LLM Map-Reduce Layer] ── (Map: CHUNK_MAP_PROMPT song song)
       │                 ── (Reduce: REDUCE_AGGREGATE_PROMPT hợp nhất)
       ▼
[OpenRouter / Groq / Gemini] ── (Multi-provider Fallback)
       │
       ▼
Markdown Meeting Notes + Action Items Table + File Detail Tabs
```

---

## 📌 SLIDE 4: Demo Trực Tiếp Trải Nghiệm Sản Phẩm (Live Demo)
- **Thao tác 1**: Kéo thả batch 3 file audio cuộc họp các nhóm (Frontend, Backend, AI).
- **Thao tác 2**: Quan sát tiến trình xử lý STT song song & Map-Reduce LLM real-time.
- **Thao tác 3**: Xem kết quả Biên bản họp Markdown, Bảng Action Items, Thẻ `<details>` từng file và thử nghiệm tính năng Export Slack / In PDF / Re-summarize.

---

## 📌 SLIDE 5: Kiểm Thử & Chất Lượng (Evaluation & Quality Bar)
- **Bộ kiểm thử Golden Set**: 20 test cases (audio ngắn, audio >30m, batch 3-5 files, audio nhiễu/nói nhanh, edge cases).
- **Quality Bar**: Đạt khi $\ge 85\%$ Pass rate.
- **Kết quả 3 lượt chạy**:
  - Lượt 1 (Baseline): $65.0\%$ (Chưa có Map-Reduce & Audio chunking).
  - Lượt 2 (Prompt Opt): $80.0\%$ (Bổ sung từ điển sửa lỗi Jargon).
  - **Lượt 3 (Final CP5)**: **$90.0\%$** (Hoàn thiện Parallel Chunking + LLM Map-Reduce Multi-provider).

---

## 📌 SLIDE 6: User Validation CP5 & Định Hướng Phát Triển
- **Kết quả Validation**: 3/3 Willing Users (Tech Lead, PO, Dev) đánh giá điểm CSAT trung bình **9.1/10**.
- **Cải tiến đã thực hiện ngay từ Feedback**:
  - Thêm nút In PDF trực tiếp.
  - Tích hợp `localStorage` lưu phiên làm việc.
  - Hỗ trợ Re-summarize không cần re-STT.
- **Định hướng phát triển**: Tích hợp Voice Activity Detection (VAD) lọc nhiễu và Speaker Diarization phân biệt từng giọng nói.
