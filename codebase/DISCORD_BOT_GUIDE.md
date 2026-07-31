# Hướng dẫn Cấu hình & Sử dụng Discord Bot (Kute AI Meeting)

Hệ thống Discord Bot được thiết kế để tự động hóa hoàn toàn việc ghi âm và tóm tắt cuộc họp với 2 luồng công việc chính:

1. **Workflow 1: Upload file thủ công (`!note`)**
2. **Workflow 2: Bot tự tham gia Voice Channel ghi âm (`!start` / `!stop` / tự rời khi phòng trống)**

---

## 🛠️ Bước 1: Tạo Discord Bot & Cấp Quyền

1. **Tạo Application mới**:
   - Truy cập [Discord Developer Portal](https://discord.com/developers/applications).
   - Bấm **New Application** $\rightarrow$ Đặt tên cho ứng dụng (VD: `Kute AI Meeting Bot`) $\rightarrow$ Bấm **Create**.

2. **Cấu hình Bot & Privileged Intents**:
   - Vào menu **Bot** ở thanh bên trái.
   - Bấm **Reset Token** để lấy Token của Bot và lưu lại.
   - Cuộn xuống phần **Privileged Gateway Intents** và BẬT 3 công tắc sau:
     - ✅ **PRESENCE INTENT**
     - ✅ **SERVER MEMBERS INTENT**
     - ✅ **MESSAGE CONTENT INTENT**
   - Bấm **Save Changes**.

3. **Tạo Link Mời Bot vào Server**:
   - Vào menu **OAuth2** $\rightarrow$ **URL Generator**.
   - Tại mục **Scopes**, tích chọn: `bot`.
   - Tại mục **Bot Permissions**, tích chọn các quyền sau:
     - **Text Permissions**: `Read Messages/View Channels`, `Send Messages`, `Attach Files`, `Embed Links`, `Read Message History`.
     - **Voice Permissions**: `Connect`, `Speak`, `Use Voice Activity`.
   - Sao chép đường dẫn **Generated URL** ở cuối trang và dán vào trình duyệt để mời Bot vào Discord Server của bạn.

---

## 🔑 Bước 2: Cấu hình File `.env`

Mở file [.env](file:///c:/Users/Admin/.vscode/Batch03-K3-AI-Product-Hackathon/kute-ai-meeting/.env) và cập nhật Bot Token vừa lấy ở Bước 1:

```env
# Discord Bot Token
DISCORD_BOT_TOKEN=MTM..._your_actual_discord_bot_token

# Groq API Key (Cho Speech-to-Text Whisper & LLM Llama)
GROQ_API_KEY=gsk_your_actual_groq_api_key
```

---

## 🚀 Bước 3: Khởi chạy Discord Bot

Mở Terminal và chạy lệnh:
```bash
python kute-ai-meeting/bot.py
```

Khi kết nối thành công, Terminal sẽ hiển thị:
```
🤖 DISCORD BOT ĐÃ KẾT NỐI THÀNH CÔNG: Kute AI Meeting Bot (ID: ...)
```

---

## 📖 Bước 4: Hướng dẫn Sử dụng Chi tiết

### 📁 Workflow 1: Upload File Thủ Công (`!note`)
- **Cách dùng**: Kéo thả 1 file ghi âm (`.mp3`, `.m4a`, `.wav`, `.ogg`) vào ô chat Discord, gõ lệnh `!note` và bấm Enter.
- **Tùy chỉnh Prompt**: Bạn có thể gõ `!note Tập trung vào các Action Items và deadline của dự án`.
- **Kết quả trả về**:
  - Nếu kết quả `< 2000 ký tự`: Bot gửi tin nhắn trực tiếp lên kênh chat.
  - Nếu kết quả `≥ 2000 ký tự`: Bot gửi bài tóm tắt ngắn + đính kèm file `Meeting_Notes.md`.

---

### 🎙️ Workflow 2: Bot Tự Ghi Âm Kênh Thoại (`!start` / `!stop`)
- **Bắt đầu cuộc họp**: Tham gia một phòng thoại (Voice Channel), sau đó gõ `!start`.
  - Bot sẽ tự kết nối vào phòng thoại của bạn và bắt đầu tiến trình ghi âm.
- **Kết thúc cuộc họp**: Gõ `!stop`.
  - Bot sẽ dừng ghi âm, ngắt kết nối kênh thoại và tự động chạy STT + LLM Tóm tắt rồi gửi Meeting Notes lên kênh chat.
- **⚡ Tự động rời phòng khi họp xong**:
  - Nếu tất cả thành viên rời khỏi phòng thoại (chỉ còn lại Bot), Bot sẽ **tự động ngắt kết nối**, dừng ghi âm và tự động xuất biên bản cuộc họp gửi lên kênh chat mà **không cần gõ lệnh `!stop`**.

---

### ❓ Trợ giúp (`!help_meeting`)
Gõ `!help_meeting` trên Discord để xem danh sách lệnh và hướng dẫn trực tiếp.
