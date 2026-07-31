# Hướng dẫn Deploy Web UI Kute AI Meeting lên Vercel

Dự án đã được cấu hình sẵn sàng cho **Vercel Serverless Functions** bằng `@vercel/python`.

## Cấu trúc hỗ trợ Deploy Vercel

```
kute-ai-meeting/
├── vercel.json          # Route & Build config cho Vercel
├── api/
│   └── index.py         # Serverless Entry Point (FastAPI)
├── public/              # Static Web Frontend
│   ├── index.html       # UI Drag & Drop & Prompt Editor
│   ├── style.css        # Glassmorphism Styling
│   └── app.js           # Client-side Logic & Markdown Parser
├── stt_service.py       # Core Speech-to-Text
├── summarizer.py        # Core LLM Summarizer
└── requirements.txt     # Python Dependencies
```

---

## Cách 1: Deploy qua GitHub Repository (Khuyên dùng - Nhanh nhất)

1. **Push dự án lên GitHub**:
   - Push toàn bộ thư mục `kute-ai-meeting` lên kho lưu trữ GitHub của bạn.

2. **Kết nối với Vercel**:
   - Truy cập [https://vercel.com/new](https://vercel.com/new).
   - Chọn Import repository từ GitHub.
   - Nếu thư mục `kute-ai-meeting` nằm ở subfolder trong repo, tại phần **Root Directory**, điền `kute-ai-meeting`.

3. **Cấu hình Biến Môi Trường (Environment Variables)**:
   - Thêm biến môi trường:
     - **Key**: `GROQ_API_KEY`
     - **Value**: `gsk_your_actual_groq_api_key_here`

4. **Bấm Deploy**:
   - Vercel sẽ tự động build và cấp cho bạn đường dẫn URL dạng `https://kute-ai-meeting.vercel.app`.

---

## Cách 2: Deploy trực tiếp bằng Vercel CLI

1. Cài đặt Vercel CLI (nếu chưa có):
   ```bash
   npm i -g vercel
   ```

2. Di chuyển vào thư mục dự án và chạy lệnh:
   ```bash
   cd kute-ai-meeting
   vercel
   ```

3. Thêm API Key vào môi trường Vercel:
   ```bash
   vercel env add GROQ_API_KEY
   ```

4. Deploy lên Production:
   ```bash
   vercel --prod
   ```

---

## Cách Chạy Cục Bộ (Local Demo)

Nếu muốn xem thử Web UI trên máy cá nhân trước khi deploy:
```bash
python kute-ai-meeting/server.py
```
Sau đó truy cập: [http://localhost:8000](http://localhost:8000)
