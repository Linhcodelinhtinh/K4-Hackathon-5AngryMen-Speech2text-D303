import os
import sys
import time
import tempfile
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

# Add parent directory to sys.path to import core modules
BASE_DIR = Path(__file__).parent.parent.resolve()
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from stt_service import transcribe_audio
from summarizer import generate_summary, DEFAULT_MODEL, get_groq_client, SYSTEM_PROMPT

app = FastAPI(title="Kute AI Meeting API", description="API Backend for Kute AI Meeting Notes")

@app.post("/api/process")
async def process_meeting_endpoint(
    audio_file: UploadFile = File(...),
    custom_prompt: str = Form(None),
    groq_api_key: str = Form(None)
):
    """
    Endpoint xử lý ghi âm cuộc họp:
    Nhận file MP3/Audio + Custom Prompt + Groq API Key tùy chọn
    Trả về Raw Transcript và Meeting Notes Markdown
    """
    # Nếu người dùng truyền API Key từ UI, ưu tiên dùng API Key này
    if groq_api_key and groq_api_key.strip():
        os.environ["GROQ_API_KEY"] = groq_api_key.strip()
    
    # Kiểm tra GROQ_API_KEY
    current_key = os.getenv("GROQ_API_KEY")
    if not current_key or current_key == "your_groq_api_key_here":
        raise HTTPException(
            status_code=400,
            detail="GROQ_API_KEY chưa được cấu hình. Vui lòng nhập API Key trên giao diện Web hoặc tạo file .env!"
        )

    # Đọc extension của file tải lên
    file_ext = Path(audio_file.filename).suffix or ".mp3"
    
    # Lưu file tải lên vào temporary file
    with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as tmp:
        tmp_path = tmp.name
        content = await audio_file.read()
        tmp.write(content)

    start_total_time = time.time()
    
    try:
        # Bước 1: Speech to Text (Groq Whisper Large V3)
        stt_start = time.time()
        raw_transcript = transcribe_audio(tmp_path)
        stt_time = time.time() - stt_start

        # Bước 2: Tóm tắt bằng LLM (Groq Llama 3.3 70B)
        llm_start = time.time()
        
        # Nếu có Custom Prompt từ người dùng, thực hiện gọi trực tiếp LLM
        if custom_prompt and custom_prompt.strip():
            client = get_groq_client()
            user_content = f"Dưới đây là bản transcript thô của cuộc họp:\n\n---\n{raw_transcript}\n---\n\nHãy tạo Meeting Notes theo đúng chỉ dẫn."
            response = client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": custom_prompt.strip()},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.3,
                max_tokens=4096
            )
            meeting_notes = response.choices[0].message.content.strip()
        else:
            meeting_notes = generate_summary(raw_transcript)

        llm_time = time.time() - llm_start
        total_time = time.time() - start_total_time

        return JSONResponse({
            "success": True,
            "filename": audio_file.filename,
            "raw_transcript": raw_transcript,
            "meeting_notes": meeting_notes,
            "stt_time": stt_time,
            "llm_time": llm_time,
            "total_time": total_time
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# Serve static frontend files for local or serverless deployment
PUBLIC_DIR = BASE_DIR / "public"
if PUBLIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(PUBLIC_DIR)), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(str(PUBLIC_DIR / "index.html"))

    @app.get("/{filename}")
    async def serve_public_file(filename: str):
        file_path = PUBLIC_DIR / filename
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(PUBLIC_DIR / "index.html"))
