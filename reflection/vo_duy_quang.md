# Reflection Cá Nhân — Hackathon AI K4

**Họ tên:** Võ Duy Quang  
**Mã số SV/HV:** 2A202601268  
**Vai trò trong nhóm:** Fullstack AI & Evaluation Engineer  
**Nhóm:** 05 · 5AngryMen · Zone D (D303)  
**Dự án:** Kute AI Meeting Notes  

---

## 1. Vai trò và phần mình đã làm

**Vai trò chính:** Tối ưu hóa LLM Summarizer, xây dựng bộ benchmark 40 test cases, và Redesign UI/UX 2 cột.

**Các việc cụ thể đã làm:**
- [x] **Xây dựng Hệ thống Prompt & Core Engine (`summarizer.py`):** Viết và tối ưu `SYSTEM_PROMPT`, `CHUNK_MAP_PROMPT`, và `REDUCE_AGGREGATE_PROMPT` với các cơ chế: Glossary tiếng Việt cho Whisper misidentifications (vd: *áp pi* $\rightarrow$ API, *rác* $\rightarrow$ RAG), Unit Normalization (vd: *mili giây* $\rightarrow$ ms), Negation Handling, và Off-topic Filter.
- [x] **Xây dựng Bộ Thử Nghiệm Evaluation Benchmark (`eval/test_cases.json`, `eval/run_eval.py`):** Mở rộng bộ kiểm thử lên 40 test cases (bao gồm 15 edge-cases khó về tiếng địa phương, accent Anh/Ấn, lỗi chính tả gõ không dấu, trộn lẫn tiếng Anh-Anh/ Anh-Mỹ tiếng Việt/ tiếng Anh-Ấn và đứt đoạn). Thiết kế `EVAL_SYSTEM_PROMPT` rút gọn (~600 tokens) giúp khắc phục triệt để lỗi Rate Limit TPD của Groq và đưa Pass Rate từ 2.5% lên $\ge 80\%$.
- [x] **Tái thiết kế Giao diện UX 2 Cột Song Song (`public/index.html`, `public/app.js`, `public/style.css`):** Chuyển đổi luồng ứng dụng từ dạng tab lộn xộn sang 2 cột độc lập (Trái: Upload $\rightarrow$ Whisper STT $\rightarrow$ Editor rà soát/sửa transcript $\rightarrow$ Nút Tóm tắt toàn bộ; Phải: Trình chiếu Meeting Notes, Stats bar & Export PDF/Word/Slack).
- [x] **Tích hợp Đa Nhà Cung Cấp LLM & Fallback Mechanism:** Thiết kế cơ chế tự động chuyển vùng linh hoạt giữa Groq (Llama 3.3 70B, Gemma 2 9B), OpenRouter (Claude 3.5, DeepSeek R1) và Google Gemini (Gemini 2.5 Flash).

**File/artifact mình chịu trách nhiệm:**
- [`summarizer.py`](../kute-ai-meeting/summarizer.py) — Core Map-Reduce LLM Summarizer Engine
- [`eval/test_cases.json`](../kute-ai-meeting/eval/test_cases.json) — Bộ 40 test cases thử nghiệm
- [`eval/run_eval.py`](../kute-ai-meeting/eval/run_eval.py) — Script chạy đánh giá tự động & báo cáo
- [`public/index.html`](../kute-ai-meeting/public/index.html) — Giao diện HTML redesign 2 cột
- [`public/app.js`](../kute-ai-meeting/public/app.js) — Logic điều khiển 3 bước (Upload $\rightarrow$ STT $\rightarrow$ Summarize)

---

## 2. AI hỗ trợ mình thế nào trong hackathon này?

**Công cụ AI đã dùng:** Antigravity AI Agent (DeepMind Engine), Claude 3.5 Sonnet, Gemini 2.5 Flash.

**AI hỗ trợ tốt ở:**
- **Sinh Test Cases thực tế:** Dùng AI hỗ trợ tổng hợp và mô phỏng lại các lỗi Whisper thực tế từ log âm thanh và Discord khóa học (vd: lỗi phát âm *làm ma* thành *Llama*, *phác áp pi* thành *FastAPI*, lỗi accent tiếng Anh kiểu Ấn/Anh).
- **Refactor code và xử lý UI:** Tốc độ tạo boilerplate code cho layout CSS Glassmorphism và các hàm xử lý Blob export Word/Slack rất nhanh, tiết kiệm hơn 2 giờ làm việc thủ công.
- **Tối ưu hóa Prompt Token:** AI đề xuất tách riêng `EVAL_SYSTEM_PROMPT` rút gọn để chạy benchmark mà không làm giảm khả năng đánh giá, giúp tiết kiệm 87% token tiêu tốn trên mỗi request API.

**AI không giúp được / mình phải tự làm:**
- **Xử lý sự cố Rate Limit & Decommissioned Models của Groq API:** Khi model `mixtral-8x7b-32768` bị Groq khai tử (trả lỗi HTTP 400) và `llama-3.3-70b-versatile` bị dính Rate Limit TPD (100k tokens/ngày), AI ban đầu chỉ gợi ý thử lại (retry). Mình phải tự tra cứu bảng giá/quota của Groq, cấu hình lại danh sách `fallbacks` sang `gemma2-9b-it`, và chèn hàm `time.sleep(3)` vào luồng eval.
- **Quyết định Luồng UX:** AI ban đầu đề xuất luồng tóm tắt song song từng file tự động (Full Pipeline), nhưng trong thực tế transcript Whisper luôn có lỗi chính tả cần con người rà soát trước. Mình đã tự quyết định đổi sang luồng 2 bước: Transcribe $\rightarrow$ Cho phép User sửa trên Editor $\rightarrow$ Mới cho phép Tóm tắt toàn bộ.

**Bài học về cách dùng AI hiệu quả:**
- Không nên phụ thuộc hoàn toàn vào gợi ý mặc định của AI cho môi trường Production/Benchmark. Cần kiểm soát chặt chẽ dung lượng Token (Token Budget) và giới hạn API (Rate Limits).
- Cung cấp ngữ cảnh lỗi cụ thể (ví dụ paste trực tiếp log traceback 429 TPD hoặc lỗi 400 API) thay vì hỏi AI giải pháp chung chung.

---

## 3. Một bài học từ case fail của chính nhóm

**Case fail chọn phân tích:**

| Mục | Nội dung |
|---|---|
| Case ID | `TC_06` (Multi-file integrity) & Sự cố Benchmark Pass Rate tụt xuống 2.5% |
| Input / Tình huống | Transcript gồm 2 file ghi âm phân tách: `=== FILE 1/2: Hop_P1.mp3 ===` (Hoa làm backend FastAPI) và `=== FILE 2/2: Hop_P2.mp3 ===` (Hùng làm Frontend React). |
| Output thực tế | Model chỉ tóm tắt đúng nội dung của File 2 (Hùng làm Frontend), hoàn toàn bỏ sót nội dung File 1 của Hoa. Đồng thời hệ thống báo lỗi Rate Limit 429 liên tục làm toàn bộ bộ eval bị gãy. |
| Tại sao fail | **(1) Về Prompt:** `SYSTEM_PROMPT` chưa đủ lực để ép LLM không được dùng cơ chế Attention tập trung vào đoạn cuối văn bản (Recency Bias). **(2) Về Hạ tầng:** Prompt quá dài (~5000 tokens) khiến 40 test cases ngốn hết 200,000 tokens/ngày, vượt mức 100,000 TPD của Groq Free Tier. |
| Nhóm xử lý thế nào | **(1)** Thêm quy tắc cứng vào Prompt Map-Reduce & Reduce: *"BẮT BUỘC tóm tắt tất cả các file, tạo thẻ `<details>` chi tiết cho từng file ở cuối"*. **(2)** Tạo `EVAL_SYSTEM_PROMPT` tinh gọn chỉ ~600 tokens cho riêng script `run_eval.py`, thay thế model bị ngưng hỗ trợ `mixtral` bằng `gemma2-9b-it`, và đặt delay 3s giữa mỗi test case. |
| Kết quả sau xử lý | Model nhận diện và tóm tắt trọn vẹn cả File 1 & File 2. Pass rate của bộ 40 test cases nhảy vọt từ **2.5% lên $\ge 85\%$** trong lần chạy thực tế tiếp theo. |

**Bài học rút ra:**
> Khi xử lý dữ liệu dài hoặc đa văn bản (Multi-doc/Multi-file), LLM rất dễ mắc lỗi Recency Bias (chỉ tập trung vào phần cuối). Cần phải ràng buộc cấu trúc Output bắt buộc (như ép tạo bảng hoặc thẻ collapsible cho từng file) để buộc model phải duyệt qua toàn bộ context. Ngoài ra, việc thiết kế bộ Eval Benchmark luôn phải đi kèm với chiến lược quản lý API Quota hợp lý.

---

## 4. Nếu có thêm 1 tuần, mình sẽ ưu tiên làm gì?

1. **Tích hợp Discord Bot Voice Recording trực tiếp (`discord-ext-voice-recv`)** — vì hiện tại người dùng phải ghi âm thủ công rồi nộp file MP3. Nếu bot nhảy trực tiếp vào voice channel của Discord nhóm để thu PCM audio, nộp thẳng sang API Whisper thì trải nghiệm người dùng sẽ khép kín 100%.
2. **Bổ sung tính năng Diarization (Phân biệt người nói - Speaker Identification)** — vì các cuộc họp đông người (4-5 thành viên) nếu transcript không ghi rõ ai đang nói thì LLM dễ bị nhầm lẫn khi gán Action Items.
3. **Phát triển cơ chế RAG trên kho dữ liệu các cuộc họp cũ** — vì giúp team có thể tìm kiếm lại các quyết định cũ (ví dụ: *"Tuần trước team đã chốt dùng Database gì?"*) thông qua Vector Database (Pinecone/ChromaDB).

---
