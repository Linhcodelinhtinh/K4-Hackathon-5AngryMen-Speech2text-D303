# AI SPEC — Kute AI Meeting Notes (Trợ lý cuộc họp & Tóm tắt Audio đa file) · Nhóm 05 (5AngryMen) · Zone D (D303)
Hướng: [ ] A — VLearn  [X] B — Trợ lý Học viên / Làm việc  [ ] C — Làn mở
Loại: [ ] Tối ưu tính năng có sẵn  [X] Tính năng mới

---

## §1. User & Job
- **Job executor + workflow**:
  - *Executor*: Tech Lead, Project Manager (PM), Scrum Master, Thư ký dự án phát triển phần mềm / sản phẩm AI.
  - *Workflow*:
    1. Sau mỗi cuộc họp (Sprint Planning, Daily Standup, Technical Review, 1-on-1), nhận 1 hoặc nhiều file ghi âm audio (MP3/WAV/M4A).
    2. Nghe lại audio hoặc đọc transcript thô để tổng hợp nội dung, tìm các quyết định chính và bảng phân công công việc (Action Items).
    3. Tra cứu, sửa lại các thuật ngữ công nghệ/AI bị gõ sai hoặc nghe nhầm trong ghi âm (RAG, LLM, API, GPU, Fine-tuning, LoRA...).
    4. Soạn biên bản cuộc họp (Meeting Notes) gửi lên kênh trao đổi chung (Slack, Discord, Notion) để phân công nhiệm vụ cho các thành viên.
- **Core JTBD** *(không chứa tên sản phẩm/AI)*:
  - *"Khi kết thúc các cuộc họp kỹ thuật kéo dài hoặc chuỗi nhiều phiên thảo luận song song, người quản lý nhóm muốn nhanh chóng nhận được biên bản họp chuẩn hóa kèm bảng phân công công việc chính xác, để toàn bộ nhóm nắm rõ nhiệm vụ và deadline mà không phải tốn 1-2 tiếng nghe lại từng file ghi âm."*
- **Problem statement** *(KHÔNG chữ AI)*:
  - *"Người quản lý dự án công nghệ mất từ 1.5 - 2 giờ mỗi ngày để nghe lại các file ghi âm cuộc họp dài hoặc tổng hợp thông tin từ nhiều file audio nhỏ rải rác, dẫn đến việc dễ bỏ sót công việc được giao, thông tin bị phân tán và các thuật ngữ chuyên ngành tiếng Anh/Việt bị ghi chép sai lệch."*
- **Evidence** *(chuẩn A và B — log đầy đủ trong repo)*:
  - **Số liệu mining / kết quả khảo sát**: Khảo sát $n = 35$ học viên, lập trình viên và PM trong nhóm và các sub-team:
    - **88.6%** ($31/35$) xác nhận mất trên 45 phút sau mỗi cuộc họp để tổng hợp meeting notes.
    - **74.3%** ($26/35$) phản ánh việc nghe lại file ghi âm dài rất tốn thời gian và dễ gây phân tâm.
    - **82.8%** ($29/35$) thừa nhận các công cụ gõ/transcribe tự động hiện tại ghi sai hoàn toàn các thuật ngữ chuyên ngành công nghệ (tiếng Việt chêm tiếng Anh).
  - **≥5 quote/ví dụ nguyên văn + nguồn**:
    1. *"Họp Sprint Planning xong audio 45 phút, ngồi tua lại để ghi xem ai nhận task gì tốn hết cả buổi chiều."* — Log khảo sát PM Tech, User `#U012`.
    2. *"Mấy từ như RAG, Prompt Engineering, Fine-tuning họp nói tiếng Việt bồi tiếng Anh là mấy tool Speech-to-Text dịch ra thành 'rác', 'bóp chim', 'phai tuning' nhìn không hiểu nổi."* — Log chat VLearn, Lead Dev `#U045`.
    3. *"Nhóm mình họp 3 file audio nhỏ riêng lẻ từng team, lúc tổng hợp toàn phải mở từng file lên nghe rồi ghép thủ công."* — Feedback log User `#U089`.
    4. *"Nhiều lúc họp xong không ai nhớ deadline của task là khi nào vì không có bảng Action Items phân công rõ ràng."* — Survey response User `#U023`.
    5. *"Muốn dùng LLM để tóm tắt file ghi âm dài 1 tiếng nhưng upload lên toàn báo lỗi vượt max size 25MB hoặc vượt quá context window của AI."* — Discord feedback User `#U067`.

---

## §2. Impact & quyết định chọn
- **Bảng impact ≥3 ứng viên**:
  | Ứng viên ý tưởng | Bao nhiêu người bị | Tần suất | Tốn gì mỗi người/lần | Khả thi kĩ thuật |
  |---|---|---|---|---|
  | **1. Trợ lý Tự động gõ & Tóm tắt Audio Cuộc họp đa file (Kute AI Meeting)** | 35/35 người (100%) | 3-5 lần/tuần | 60-90 phút nghe lại/tổng hợp thủ công | **Cao** (Groq Whisper + Parallel Chunking + LLM Map-Reduce) |
  | **2. Bot AI điểm danh & phân tích cảm xúc diễn giả trong Zoom/Meet** | 10/35 người (28.5%) | 1-2 lần/tuần | 15 phút kiểm tra danh sách | **Thấp** (Phụ thuộc Webhook API phức tạp của Zoom/Meet, rủi ro bảo mật) |
  | **3. Trợ lý tự động soạn Email báo cáo tiến độ dự án tuần** | 20/35 người (57.1%) | 1 lần/tuần | 30 phút/tuần | **Trung bình** (Ít nhức nhối hàng ngày so với việc họp) |

- **Ứng viên ĐÃ LOẠI + vì sao**:
  - *Loại Ứng viên 2*: Tần suất dùng thấp, thời gian tiết kiệm ít (15 phút/tuần), độ phức tạp kết nối Webhook Zoom/Meet cao, rủi ro đánh giá sai cảm xúc diễn giả gây mâu thuẫn nội bộ.
  - *Loại Ứng viên 3*: Giá trị tiết kiệm không đột phá (30 phút/tuần), người dùng có thể tự copy/paste template email đơn giản mà không cần pipeline AI xử lý phức tạp.
- **Ứng viên CHỌN + vì sao (bằng số)**:
  - *Chọn Ứng viên 1 (Kute AI Meeting Notes)* vì tác động vượt trội: Tiết kiệm trung bình **4.5 giờ/người/tuần** $\times$ $35\text{ người} = \mathbf{157.5\text{ giờ làm việc/tuần}}$ cho toàn bộ nhóm. Tính khả thi đạt 100% trong 1.5 ngày hackathon nhờ kiến trúc Web Fast API + Vanilla JS + Parallel Audio Chunking + LLM Map-Reduce hỗ trợ multi-provider.

---

## §3. Giải pháp tương tự đã nghiên cứu
- **Otter.ai / Fireflies.ai**:
  - *Flow*: Bot tham gia phòng họp trực tuyến -> Transcribe real-time -> Summarize ra biên bản.
  - *Đáng học*: Giao diện trực quan, chia đoạn speaker linh hoạt, tìm kiếm từ khóa tốt.
  - *Đáng né*: Không hỗ trợ xử lý tiếng Việt chêm tiếng Anh chuyên ngành (nhầm RAG, Llama, API...); giá thành đắt; bắt buộc phải cấp quyền Bot truy cập phòng họp.
  - *Mình khác gì*: Cho phép nộp trực tiếp file audio ghi âm sẵn mà không cần cấp quyền bot; hỗ trợ batch upload 5 file cùng lúc (đến 300MB); thuật toán cắt chunk song song vượt giới hạn 24MB API; Prompt thiết kế riêng sửa lỗi thuật ngữ AI tiếng Việt; Map-Reduce bảo tồn chi tiết từng file.
- **Turboscribe / Whisper Web App thô**:
  - *Flow*: Upload audio -> Speech-to-Text -> Xuất văn bản thô.
  - *Đáng học*: Tốc độ gõ chữ từ audio nhanh.
  - *Đáng né*: Chỉ trả về một khối văn bản thô không cấu trúc, không trích xuất Action Items / Deadlines, không xử lý được file audio dung lượng lớn vượt quá context window của LLM.
  - *Mình khác gì*: Tích hợp trọn gói 2 bước STT + LLM Summarization (Map-Reduce); tự động xuất bảng Action Items (Task, Assignee, Deadline); hỗ trợ thay đổi Provider/Model (Groq, OpenRouter, Gemini) và tùy chỉnh Custom Prompt linh hoạt.

---

## §4. Thiết kế
- **Lát cắt MỘT CÂU**:
  - *"Một Tech Lead (1 user) tải lên chuỗi 1-5 file audio cuộc họp kỹ thuật nặng tới 300MB (1 việc), AI tự động chia nhỏ audio, transcribe và chạy Map-Reduce LLM sửa lỗi thuật ngữ công nghệ tiếng Việt (1 quyết định AI), xuất ra Biên bản cuộc họp Markdown hoàn chỉnh kèm bảng Action Items và chi tiết từng file (1 kết quả)."*
- **Non-goals (≥3 thứ KHÔNG build)**:
  1. KHÔNG build tính năng Bot tự động tham gia cuộc họp trực tiếp (Zoom/Google Meet/Teams).
  2. KHÔNG build hệ thống quản lý tài khoản, đăng nhập, hoặc lưu trữ database người dùng (Stateless application).
  3. KHÔNG build tính năng Speaker Diarization phức tạp phân biệt giọng nói từng người bằng AI chuyên biệt (dùng phân tách theo file/chunk và ngữ cảnh).
- **Mức prototype nhắm tới**: `[ ] Sketch  [ ] Mock  [X] Working`
  - *Phần thật*: 100% Speech-to-Text (Groq Whisper Large V3), Audio parallel chunking (`pydub` + `static-ffmpeg`), LLM Summarization Map-Reduce (Groq Llama 3.3 70B, OpenRouter, Gemini), Web API FastAPI & Vanilla JS Frontend UI.
  - *Phần mock*: Không có (Toàn bộ pipeline chạy live API thật).
- **Automation**: `[X] augment  [ ] conditional  [ ] automate`
  - *Lý do theo cost-of-error*: Việc bỏ sót nhiệm vụ hoặc tóm tắt sai quyết định cuộc họp có chi phí lỗi cao (miss deadline, làm sai yêu cầu kỹ thuật). Do đó AI đóng vai trò Trợ lý tạo bản thảo Biên bản họp (Augment), cho phép người dùng xem lại transcript thô, chỉnh sửa prompt, chọn model và copy/export kết quả.
- **§4b. Nguyên tắc đã áp dụng (≥4 — HAX/PAIR, xem guide)**:
  | Nguyên tắc | Áp cụ thể vào đâu trong prototype |
  |---|---|
  | **HAX G1**: Make clear what the system can do | Giao diện hiển thị rõ giới hạn (Tối đa 5 file, tổng 300MB, hỗ trợ MP3/WAV/M4A) và hiển thị quy trình xử lý 2 bước rõ ràng (STT -> LLM Summarize). |
  | **HAX G9**: Support efficient correction | Cho phép user nhập Custom Prompt, chọn lại Provider/Model LLM và bấm "Tóm tắt lại" trực tiếp từ transcript đã lưu mà không cần tốn chi phí/thời gian transcribe lại audio. |
  | **PAIR**: Support human control | Cung cấp đầy đủ nút thao tác điều khiển: Sao chép Markdown, Tải file `.md`, Sao chép định dạng Slack, In PDF, Tìm kiếm từ khóa trong transcript thô. |
  | **PAIR**: Set expectations for AI accuracy | Cung cấp Tab "Transcript" gốc có sub-tabs cho từng file để user dễ dàng đối chiếu/cross-check thông tin tóm tắt với văn bản thô. |

---

## §5. Kiểu lỗi — 4 lớp chỗ khó + kịch bản (≥8)
| STT | Lớp chỗ khó | Kịch bản lỗi cụ thể | Nguyên nhân kĩ thuật | Cách ứng xử / Thiết kế giảm thiểu |
|---|---|---|---|---|
| 1 | **Nhập liệu lỗi** | User upload file không phải audio (VD: file txt/pdf đổi đuôi `.mp3`) hoặc file audio bị hỏng. | `pydub`/`ffmpeg` không decode được stream audio. | Backend catch `RuntimeError`/`pydub` exception, trả về lỗi HTTP 500 với thông báo tiếng Việt: *"Lỗi xử lý Audio (File hỏng hoặc không đúng định dạng)"*. |
| 2 | **Nhập liệu lỗi** | User upload quá 5 file hoặc tổng dung lượng các file > 300MB. | Vượt ngưỡng cấu hình an toàn hệ thống. | Client-side JS validate ngay lập tức chặn submit; Backend hàm `validate_audio_files` ném HTTP 400 rõ ràng. |
| 3 | **Nhập liệu lỗi** | API Key (Groq / Gemini / OpenRouter) bị trống hoặc sai / hết hạn. | Thiếu credentials gọi LLM/STT API. | Bắt lỗi `AuthenticationError` / `ValueError`, trả lỗi HTTP 400/401 hướng dẫn nhập Key hợp lệ trên UI. |
| 4 | **Thiếu thông tin** | File audio chỉ có tiếng ồn, nhạc nền, hoặc nói quá nhỏ không có tiếng người. | Groq Whisper trả về transcript rỗng hoặc chỉ có kí tự nhiễu. | Pipeline phát hiện transcript thô < 20 ký tự -> Hiển thị cảnh báo *"Audio không chứa nội dung thoại rõ ràng"* thay vì gửi LLM. |
| 5 | **Thiếu thông tin** | Cuộc họp không đề cập đến người phụ trách (Assignee) hoặc Deadline cho công việc. | Thông tin trao đổi trong họp còn bỏ ngỏ. | Prompt quy định điền `[Chưa xác định]` vào cột Assignee/Deadline thay vì tự bịa ra thông tin. |
| 6 | **Ngoài phạm vi** | User nhập Custom Prompt yêu cầu làm việc ngoài cuộc họp (VD: *"Viết giúp tôi một đoạn code Python tính Fibonacci"*). | User dùng box Custom Prompt như một Chatbot hội thoại thông thường. | Prompt hệ thống ép khuôn cấu trúc Markdown bắt buộc (`# Meeting Notes...`), giữ đúng định dạng biên bản họp. |
| 7 | **Giới hạn mô hình** | Whisper transcribe sai từ chuyên ngành tiếng Việt/Anh ("RAG" -> "rác", "Llama" -> "làm ma", "API" -> "áp pi"). | Giới hạn acoustic model của Whisper với tiếng Việt chêm tiếng Anh. | Tích hợp từ điển chuẩn hóa trong System Prompt & Map-Reduce Prompt ép LLM tự động sửa lại thuật ngữ chuẩn. |
| 8 | **Giới hạn mô hình** | File audio dung lượng lớn (>24MB) hoặc quá dài (>12,000 chars) bị tràn Context Window hoặc mất thông tin file đầu/cuối. | Đạt giới hạn payload API Groq Whisper (24MB) và context window LLM. | Thiết kế 2 tầng chia chunk: Audio Parallel Chunking (10 phút/chunk) + LLM Map-Reduce bảo tồn thông tin từng file dưới dạng HTML details. |

---

## §6. Bốn đường đi của trải nghiệm
- **Happy path**:
  - User kéo thả 1-5 file MP3 vào giao diện Web -> Bấm *"Bắt đầu Xử lý"* -> Hệ thống hiển thị Progress Spinner -> Trả về Kết quả Biên bản họp Markdown đẹp mắt với Executive Summary, Key Takeaways, Bảng Action Items, và Chi tiết từng file.
- **Low-confidence (②)**:
  - Audio có đoạn nói ngọng/nhiễu tín hiệu -> LLM tóm tắt đoạn đó nhưng đánh dấu `[Nội dung cần xác minh lại: ...]` hoặc để `[Chưa xác định]` trong bảng Action Items để user chú ý.
- **Failure/không căn cứ (①)**:
  - File ghi âm quá ngắn hoặc chỉ có tiếng rè -> Trả về thông báo: *"Không thể trích xuất văn bản từ audio. Vui lòng kiểm tra lại chất lượng file ghi âm."*
- **Correction (user sửa)**:
  - User đọc kết quả -> Muốn nhấn mạnh thêm vào phần Tech Tasks -> Thay đổi Custom Prompt -> Bấm *"Tóm tắt lại"* -> Backend gọi lại `/api/summarize` với raw transcript đã lưu (không tốn chi phí/thời gian transcribe lại audio).
- **Khi bị đòi ngoài phạm vi (③)**:
  - User nhập prompt yêu cầu dịch sang tiếng Pháp hoặc tạo thơ -> Hệ thống vẫn ưu tiên trả về đúng cấu trúc Biên bản họp tiếng Việt chuẩn hóa, phần nội dung phụ ghi nhận ngắn gọn.
- **Case đặc thù domain (④)**:
  - Cuộc họp chứa nhiều biệt ngữ công nghệ AI (RAG, Fine-tuning, VectorDB, LoRA, Quantization) -> LLM tự động nhận diện và sửa lỗi sai âm của STT thành đúng từ chuẩn chuyên ngành.

---

## §7. Kiểm thử
- **Chiều chất lượng + định nghĩa kiểm chứng được**:
  1. *Tính chính xác của Action Items*: Trích xuất đúng $\ge 85\%$ danh sách công việc, người phụ trách, deadline có trong audio test.
  2. *Tính toàn vẹn đa file (Multi-file coverage)*: $100\%$ các file audio trong batch upload đều có phần tóm tắt riêng trong thẻ `<details><summary>`.
  3. *Khả năng sửa lỗi thuật ngữ AI (Jargon correction rate)*: Nhận diện và tự sửa đúng $\ge 90\%$ các từ Whisper transcribe sai (RAG, Llama, API, GPU, Prompt...).
  4. *Thời gian xử lý (Latency)*: Thời gian xử lý 1 file 30 phút audio $< 45$ giây nhờ xử lý song song parallel chunks.
- **Golden set** *(≥20 case trong `eval/` registry)*:
  - **5 case** audio cuộc họp ngắn (<5 phút, đơn file, chủ đề Tech/RAG).
  - **5 case** audio cuộc họp dài (>30 phút, file >24MB, kiểm thử Audio Chunking & Map-Reduce).
  - **5 case** đa file (batch 3-5 file audio đại diện cho 3-5 sub-team họp song song).
  - **3 case** audio chất lượng kém (nhiễu nền, nói ngọng, chêm tiếng Anh/Việt liên tục).
  - **2 case** edge cases (file không tiếng thoại, file audio bị méo dạng format).
- **Quality bar** *(chốt từ hạn chốt spec của khoá, giữ nguyên sau đó)*:
  - *"Đạt khi $\ge\mathbf{85\%}$ case trong Golden Set đạt điểm Pass (đủ 4 mục Meeting Notes, không bỏ sót file, sửa đúng từ chuyên ngành), và $100\%$ lỗi API Key / File Size được xử lý êm (graceful degradation) không crash app."*
- **Kết quả các lượt chạy (bảng % — cập nhật đến trước CP6)**:
  | Lượt chạy | Thời điểm | Số case test | % Đạt (Pass Rate) | Ghi chú / Cải tiến |
  |---|---|---|---|---|
  | Lượt 1 (Baseline) | Day 1 - 15:00 | 20 cases | 65.0% | Chưa có Map-Reduce, file dài bị trôi thông tin, sai từ chuyên ngành AI. |
  | Lượt 2 (Prompt Opt) | Day 1 - 20:00 | 20 cases | 80.0% | Bổ sung từ điển sửa lỗi Whisper vào System Prompt, thêm thẻ `<details>` đa file. |
  | Lượt 3 (Final CP5) | Day 2 - 09:30 | 20 cases | 90.0% | Hoàn thiện Parallel Audio Chunking + LLM Map-Reduce fallback multi-provider (Groq/Gemini/OpenRouter). |

---

## §8. Phân công & kế hoạch
- **Phân công có tên**:
  - **Lưu Quang Linh (Lead)**: Spec & Architecture, Backend FastAPI (`api/index.py`), Parallel Audio Chunking (`stt_service.py`), Deployment Vercel.
  - **Thành viên 2 (AI Prompt Eng)**: Tối ưu LLM Prompts (Map-Reduce & Jargon correction in `summarizer.py`), Xây dựng Golden Set 20 cases.
  - **Thành viên 3 (Frontend Dev)**: UI/UX Web App (`public/index.html`, `app.js`, `style.css`), drag-and-drop, export options (Slack/PDF/Markdown).
  - **Thành viên 4 (Tester/Validation)**: Tiến hành User Validation CP5 với 3+ willing users, tổng hợp feedback log.
  - **Thành viên 5 (Demo/Slides)**: Soạn slide demo 6 trang, quay demo video và chuẩn bị kịch bản thuyết trình.
- **Willing users (≥3 tên) + kế hoạch vòng validation CP5**:
  - *3 Willing users*: Anh Tuấn (Tech Lead), Chị Hoa (Product Owner), Bạn Minh (Fullstack Dev).
  - *3 câu hỏi validation*:
    1. "Biên bản họp tạo ra có trích xuất đúng danh sách Action Items và người làm không?"
    2. "Các từ ngữ chuyên ngành AI (RAG, Llama, API) có được viết đúng chính tả không?"
    3. "Giao diện tải nhiều file audio và tính năng xem lại transcript có dễ sử dụng không?"
  - *Người log feedback*: Thành viên 4 (Tester/Validation).
- **Multi-prototype (nếu làm)**:
  - *Phương án A (CLI script `main.py`)*: Dùng cho developer chạy local nhanh qua dòng lệnh terminal.
  - *Phương án B (Web SPA `api/index.py` + `public/`)*: Dùng cho người dùng cuối (PM/Thư ký) thao tác trực quan trên trình duyệt.
  - *Lý do chọn Phương án B làm prototype chính*: Tiếp cận được người dùng không chuyên IT, hỗ trợ kéo thả file và xem kết quả tức thì.

---

## §9. Changelog
| Thời điểm | Đổi gì | Vì sao (trỏ về feedback/case nào) |
|---|---|---|
| Day 1 11:00 | Thêm chế độ Map-Reduce | Case audio dài >30 phút bị vượt quá token limit của LLM single-pass. |
| Day 1 16:00 | Thêm `static-ffmpeg` & parallel chunking | Phát hiện lỗi ffmpeg chưa cài trên máy Windows của user và API Groq giới hạn 24MB/file. |
| Day 1 21:00 | Tích hợp Multi-provider (Groq, OpenRouter, Gemini) | Đề phòng Groq API bị Rate Limit (Lỗi 429) trong buổi Demo. |
| Day 2 08:30 | Thêm thẻ `<details>` tóm tắt riêng từng file | Feedback User `#U089`: Khi upload 3 file audio, bản tóm tắt chung làm trôi thông tin riêng từng file. |
