# Kute AI Meeting Notes — Mini Hackathon AI Batch 03 (K4)

> **Tự động chuyển đổi audio cuộc họp & tổng hợp Biên bản cuộc họp đa file (Multi-file Audio Meeting Summarizer & Action Item Tracker)**

- **Nhóm**: Nhóm 05 — 5AngryMen
- **Zone**: Zone D (Phòng D303)
- **Hướng**: Hướng B — Trợ lý Học viên / Làm việc (Work Assistant)
- **Loại**: Tính năng mới

---

## 👥 Danh sách Thành viên & Phân công Công việc

| Mã HV | Họ và Tên | Vai trò | Phân công nhiệm vụ chi tiết |
|---|---|---|---|
| **2A202601084** | **Lưu Quang Linh** | **Group Leader** | Viết `spec.md`, thiết kế Kiến trúc Backend FastAPI (`codebase/api/index.py`), Parallel Audio Chunking (`codebase/stt_service.py`), Deploy Vercel. |
| **2A2026** | **Nguyễn Văn A** | **AI Prompt Engineer** | Thiết kế & Tối ưu LLM Prompts (Map-Reduce & Sửa lỗi thuật ngữ Jargon in `codebase/summarizer.py`), Xây dựng bộ Golden Set 20 cases (`eval/`). |
| **K4-1026** | **Trần Thị B** | **Frontend Developer** | Phát triển UI/UX Web SPA (`codebase/public/`), Drag & Drop Multi-file Upload, Export Markdown/Slack/PDF, Session Restore. |
| **K4-1027** | **Lê Văn C** | **QA & Validation Lead** | Tiến hành vòng User Validation CP5 với 3 Willing Users, tổng hợp log phản hồi & đánh giá chỉ số (`validation/`). |
| **K4-1028** | **Phạm Văn D** | **Demo & Product Pitcher** | Soạn slide thuyết trình 6 trang (`demo-slides.pdf`), quay video Demo sản phẩm và chuẩn bị kịch bản Pitching CP6. |

---

## 📁 Cấu trúc Repository Nộp bài

```
repo/
├── README.md          ← Thông tin nhóm, danh sách thành viên & phân công nhiệm vụ
├── spec.md            ← AI Spec hoàn chỉnh 8 phần theo 03-template-ai-spec.md
├── demo-slides.pdf    ← Slide thuyết trình 6 trang (Kịch bản Demo CP6)
├── codebase/          ← Mã nguồn Prototype chạy thật (FastAPI Backend + Vanilla JS Frontend)
│   ├── main.py        ← Entrypoint chạy CLI local
│   ├── server.py      ← Local dev server entrypoint
│   ├── stt_service.py ← Parallel Audio Chunking & Groq Whisper STT
│   ├── summarizer.py  ← Multi-provider LLM (OpenRouter/Groq/Gemini) & Map-Reduce
│   ├── api/           ← FastAPI Web Endpoints
│   ├── public/        ← Static Frontend Web App (HTML/CSS/JS)
│   └── vercel.json    ← Cấu hình Serverless Deployment
├── eval/              ← Bộ kiểm thử Golden Set (20 cases) + Bảng kết quả các lượt chạy
│   ├── golden_set.json
│   └── eval_results.md
├── validation/        ← Log phản hồi & kết quả kiểm thử với 3+ willing users (CP5)
│   └── feedback_log.md
└── reflection/        ← Bài thu hoạch & bài học cá nhân của từng thành viên
    ├── luu_quang_linh.md
    ├── nguyen_van_a.md
    ├── tran_thi_b.md
    ├── le_van_c.md
    └── pham_van_d.md
```

---

## 🚀 Hướng dẫn Chạy ứng dụng (`codebase/`)

### 1. Cài đặt Môi trường
```bash
cd codebase
pip install -r requirements.txt
```

### 2. Cấu hình API Key (`.env`)
Tạo file `.env` từ `.env.example` và điền API Keys:
```env
GROQ_API_KEY=gsk_...
OPENROUTER_API_KEY=sk-or-v1-...
GEMINI_API_KEY=AIzaSy...
```

### 3. Chạy Web App Trực quan
```bash
python server.py
# Hoặc: uvicorn api.index:app --reload --port 8000
```
Mở trình duyệt truy cập: `http://localhost:8000`

### 4. Chạy qua CLI
```bash
python main.py path/to/meeting_audio.mp3 -p openrouter
```

---

## 📌 Điểm Nổi Bật của Sản Phẩm (Prototype Status: `Working 100%`)

1. **Audio Parallel Chunking**: Tự động cắt audio > 24MB thành các segment 10 phút dùng `pydub` + `static-ffmpeg` và gõ chữ song song qua Groq Whisper Large V3.
2. **Multi-Provider LLM Map-Reduce**: Tự động chia nhỏ transcript dài > 12,000 ký tự để chạy Map song song, sau đó Reduce hợp nhất thành Biên bản họp Markdown đẹp mắt (mặc định dùng OpenRouter `meta-llama/llama-3.3-70b-instruct`, hỗ trợ fallback Groq và Gemini).
3. **Jargon Correction**: Prompt được tối ưu đặc biệt để tự động sửa các lỗi sai âm tiếng Việt/Anh của Whisper (`RAG` -> "rác", `Llama` -> "làm ma", `API` -> "áp pi").
4. **Preserve Multi-file Details**: Hỗ trợ batch upload tối đa 5 file (300MB), giữ nguyên chi tiết tóm tắt riêng từng file dưới thẻ `<details><summary>` ở cuối bài.
