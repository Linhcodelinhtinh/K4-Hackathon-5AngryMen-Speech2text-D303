import os
import sys
import time
import tempfile
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

class SummarizeRequest(BaseModel):
    raw_transcript: str
    custom_prompt: str = None
    groq_api_key: str = None

# Add parent directory to sys.path to import core modules
BASE_DIR = Path(__file__).parent.parent.resolve()
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from stt_service import transcribe_audio
from summarizer import generate_summary, DEFAULT_MODEL, get_groq_client, SYSTEM_PROMPT

app = FastAPI(title="Kute AI Meeting API", description="API Backend for Kute AI Meeting Notes")

def validate_groq_api_key(provided_key: str = None) -> str:
    if provided_key and provided_key.strip():
        os.environ["GROQ_API_KEY"] = provided_key.strip()
        return provided_key.strip()
    
    current_key = os.getenv("GROQ_API_KEY")
    if not current_key or current_key.strip() in ["", "your_groq_api_key_here", "gsk_your_groq_api_key_here"]:
        raise HTTPException(
            status_code=400,
            detail="Lỗi 400: 'Thiếu Groq API Key. Vui lòng nhập API Key trên giao diện Web hoặc tạo file .env!'"
        )
    return current_key

def parse_and_raise_error(e: Exception):
    if isinstance(e, HTTPException):
        raise e
    err_str = str(e)
    err_type = type(e).__name__

    if "GROQ_API_KEY" in err_str or "api_key" in err_str.lower() or isinstance(e, ValueError):
        raise HTTPException(
            status_code=400,
            detail="Lỗi 400: 'Thiếu hoặc sai cấu hình Groq API Key. Vui lòng kiểm tra lại API Key!'"
        )
    elif "AuthenticationError" in err_type or "401" in err_str or "Invalid API Key" in err_str or "invalid_api_key" in err_str.lower():
        raise HTTPException(
            status_code=401,
            detail="Lỗi 401: 'Groq API Key không hợp lệ hoặc hết hạn. Vui lòng kiểm tra lại Key!'"
        )
    elif "RateLimitError" in err_type or "429" in err_str or "rate_limit" in err_str.lower():
        raise HTTPException(
            status_code=429,
            detail="Lỗi 429: 'Quá giới hạn số lượng request Groq API (Rate Limit). Thử lại sau ít phút!'"
        )
    elif "pydub" in err_str.lower() or "ffmpeg" in err_str.lower() or "AudioSegment" in err_str:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi 500: 'Lỗi xử lý Audio (Thiếu FFmpeg hoặc file hỏng)': {err_str}"
        )
    elif isinstance(e, FileNotFoundError):
        raise HTTPException(
            status_code=404,
            detail=f"Lỗi 404: 'Không tìm thấy file ghi âm': {err_str}"
        )
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi 500: 'Lỗi hệ thống ({err_type})': {err_str}"
        )

@app.post("/api/transcribe")
async def transcribe_endpoint(
    audio_file: UploadFile = File(...),
    groq_api_key: str = Form(None)
):
    """Endpoint chỉ thực hiện Speech-to-Text từ Audio."""
    try:
        validate_groq_api_key(groq_api_key)

        file_ext = Path(audio_file.filename).suffix or ".mp3"
        with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as tmp:
            tmp_path = tmp.name
            content = await audio_file.read()
            tmp.write(content)

        try:
            stt_start = time.time()
            raw_transcript = transcribe_audio(tmp_path)
            stt_time = time.time() - stt_start

            return JSONResponse({
                "success": True,
                "filename": audio_file.filename,
                "raw_transcript": raw_transcript,
                "stt_time": stt_time
            })
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    except Exception as e:
        parse_and_raise_error(e)

@app.post("/api/summarize")
async def summarize_endpoint(req: SummarizeRequest):
    """Endpoint chỉ thực hiện Tóm tắt từ Raw Transcript text."""
    try:
        validate_groq_api_key(req.groq_api_key)

        if not req.raw_transcript or not req.raw_transcript.strip():
            raise HTTPException(status_code=400, detail="Lỗi 400: 'Văn bản Transcript trống, không thể tóm tắt!'")

        llm_start = time.time()
        
        if req.custom_prompt and req.custom_prompt.strip():
            client = get_groq_client()
            user_content = f"Dưới đây là bản transcript thô của cuộc họp:\n\n---\n{req.raw_transcript}\n---\n\nHãy tạo Meeting Notes theo đúng chỉ dẫn."
            response = client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": req.custom_prompt.strip()},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.3,
                max_tokens=4096
            )
            meeting_notes = response.choices[0].message.content.strip()
        else:
            meeting_notes = generate_summary(req.raw_transcript)

        llm_time = time.time() - llm_start

        return JSONResponse({
            "success": True,
            "meeting_notes": meeting_notes,
            "llm_time": llm_time
        })
    except Exception as e:
        parse_and_raise_error(e)

@app.post("/api/process")
async def process_meeting_endpoint(
    audio_file: UploadFile = File(...),
    custom_prompt: str = Form(None),
    groq_api_key: str = Form(None)
):
    """Endpoint full pipeline: Speech-to-Text + Tóm tắt LLM"""
    try:
        validate_groq_api_key(groq_api_key)

        file_ext = Path(audio_file.filename).suffix or ".mp3"
        with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as tmp:
            tmp_path = tmp.name
            content = await audio_file.read()
            tmp.write(content)

        start_total_time = time.time()
        
        try:
            # Bước 1: Transcribe
            stt_start = time.time()
            raw_transcript = transcribe_audio(tmp_path)
            stt_time = time.time() - stt_start

            # Bước 2: Tóm tắt
            llm_start = time.time()
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

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    except Exception as e:
        parse_and_raise_error(e)

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
