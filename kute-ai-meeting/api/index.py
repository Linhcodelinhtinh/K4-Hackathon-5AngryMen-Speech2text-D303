import os
import sys
import time
import tempfile
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

MAX_FILES_COUNT = 5
MAX_TOTAL_SIZE_MB = 300
MAX_TOTAL_SIZE_BYTES = MAX_TOTAL_SIZE_MB * 1024 * 1024

class SummarizeRequest(BaseModel):
    raw_transcript: str
    custom_prompt: Optional[str] = None
    provider: Optional[str] = "openrouter"
    model_name: Optional[str] = None
    provider_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None

# Add parent directory to sys.path to import core modules
BASE_DIR = Path(__file__).parent.parent.resolve()
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from stt_service import transcribe_audio_with_chunks
from summarizer import generate_summary, DEFAULT_MODEL, get_provider_api_key, SYSTEM_PROMPT

app = FastAPI(title="Kute AI Meeting API", description="API Backend for Kute AI Meeting Notes with Multi-File & Multi-Provider")

def validate_llm_api_key(provider: str = "openrouter", provided_key: str = None) -> str:
    return get_provider_api_key(provider, provided_key)

def validate_audio_files(files: List[UploadFile]) -> float:
    """Kiểm tra giới hạn tối đa 5 file và tổng dung lượng <= 300MB."""
    if not files:
        raise HTTPException(status_code=400, detail="Lỗi 400: 'Vui lòng chọn ít nhất 1 file ghi âm!'")
    
    if len(files) > MAX_FILES_COUNT:
        raise HTTPException(
            status_code=400,
            detail=f"Lỗi 400: 'Chỉ được tải lên tối đa {MAX_FILES_COUNT} file ghi âm cùng lúc (Hiện tại: {len(files)} file)!'"
        )
    
    total_bytes = 0
    for f in files:
        f.file.seek(0, 2)
        total_bytes += f.file.tell()
        f.file.seek(0)
        
    total_mb = total_bytes / (1024 * 1024)
    if total_bytes > MAX_TOTAL_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"Lỗi 400: 'Tổng dung lượng các file vượt quá {MAX_TOTAL_SIZE_MB}MB (Hiện tại: {total_mb:.2f}MB)!'"
        )
    
    return total_mb

def parse_and_raise_error(e: Exception):
    if isinstance(e, HTTPException):
        raise e
    err_str = str(e)
    err_type = type(e).__name__

    if "API_KEY" in err_str or "api_key" in err_str.lower() or isinstance(e, ValueError):
        raise HTTPException(
            status_code=400,
            detail=f"Lỗi 400: '{err_str}'"
        )
    elif "AuthenticationError" in err_type or "401" in err_str or "Invalid API Key" in err_str or "invalid_api_key" in err_str.lower():
        raise HTTPException(
            status_code=401,
            detail="Lỗi 401: 'API Key không hợp lệ hoặc hết hạn. Vui lòng kiểm tra lại Key!'"
        )
    elif "RateLimitError" in err_type or "429" in err_str or "rate_limit" in err_str.lower():
        raise HTTPException(
            status_code=429,
            detail="Lỗi 429: 'Quá giới hạn số lượng request API (Rate Limit). Thử lại sau ít phút!'"
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
    audio_files: List[UploadFile] = File(None),
    audio_file: Optional[UploadFile] = File(None),
    provider: Optional[str] = Form("openrouter"),
    provider_api_key: Optional[str] = Form(None),
    groq_api_key: Optional[str] = Form(None)
):
    """Endpoint Speech-to-Text hỗ trợ tối đa 5 file / max 300MB."""
    try:
        api_key = provider_api_key or groq_api_key
        validate_llm_api_key("groq", api_key)
        
        files_to_process = audio_files or ([audio_file] if audio_file else [])
        total_mb = validate_audio_files(files_to_process)

        stt_start = time.time()
        all_raw_transcripts = []
        all_chunk_transcripts = []
        files_detail = []

        for idx, file_obj in enumerate(files_to_process):
            file_ext = Path(file_obj.filename).suffix or ".mp3"
            with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as tmp:
                tmp_path = tmp.name
                content = await file_obj.read()
                tmp.write(content)

            try:
                result = transcribe_audio_with_chunks(tmp_path)
                header = f"=== FILE {idx+1}/{len(files_to_process)}: {file_obj.filename} ==="
                file_text = f"{header}\n\n{result['full_transcript']}"
                
                all_raw_transcripts.append(file_text)
                for c_idx, c_text in enumerate(result["chunk_transcripts"]):
                    c_header = f"=== FILE {idx+1}/{len(files_to_process)}: {file_obj.filename} (Đoạn {c_idx+1}/{len(result['chunk_transcripts'])}) ==="
                    all_chunk_transcripts.append(f"{c_header}\n\n{c_text}")

                files_detail.append({
                    "filename": file_obj.filename,
                    "transcript": result["full_transcript"]
                })
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

        stt_time = time.time() - stt_start
        full_transcript = "\n\n".join(all_raw_transcripts)

        return JSONResponse({
            "success": True,
            "file_count": len(files_to_process),
            "total_size_mb": round(total_mb, 2),
            "raw_transcript": full_transcript,
            "files_detail": files_detail,
            "chunk_transcripts": all_chunk_transcripts,
            "stt_time": stt_time
        })

    except Exception as e:
        parse_and_raise_error(e)

@app.post("/api/summarize")
async def summarize_endpoint(req: SummarizeRequest):
    """Endpoint Tóm tắt từ Raw Transcript text (Tự động kích hoạt Map-Reduce nếu text dài)."""
    try:
        p = req.provider or "openrouter"
        api_key = req.provider_api_key or req.groq_api_key
        validate_llm_api_key(p, api_key)

        if not req.raw_transcript or not req.raw_transcript.strip():
            raise HTTPException(status_code=400, detail="Lỗi 400: 'Văn bản Transcript trống, không thể tóm tắt!'")

        llm_start = time.time()
        meeting_notes = generate_summary(
            req.raw_transcript,
            custom_prompt=req.custom_prompt,
            model_name=req.model_name,
            provider=p,
            provider_api_key=api_key
        )
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
    audio_files: List[UploadFile] = File(None),
    audio_file: Optional[UploadFile] = File(None),
    custom_prompt: Optional[str] = Form(None),
    provider: Optional[str] = Form("openrouter"),
    model_name: Optional[str] = Form(None),
    provider_api_key: Optional[str] = Form(None),
    groq_api_key: Optional[str] = Form(None)
):
    """
    Endpoint Full Pipeline đa file (Tối đa 5 file / Max 300MB):
    Parallel STT Chunking + Map-Reduce LLM Summarizing
    """
    try:
        p = provider or "openrouter"
        api_key = provider_api_key or groq_api_key
        validate_llm_api_key("groq", api_key if p == "groq" else None) # Groq always needed for Whisper STT
        validate_llm_api_key(p, api_key)

        files_to_process = audio_files or ([audio_file] if audio_file else [])
        total_mb = validate_audio_files(files_to_process)

        start_total_time = time.time()
        
        # Bước 1: STT Tất cả các file
        stt_start = time.time()
        all_raw_transcripts = []
        all_chunk_transcripts = []
        files_detail = []

        for idx, file_obj in enumerate(files_to_process):
            file_ext = Path(file_obj.filename).suffix or ".mp3"
            with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as tmp:
                tmp_path = tmp.name
                content = await file_obj.read()
                tmp.write(content)

            try:
                result = transcribe_audio_with_chunks(tmp_path)
                header = f"=== FILE {idx+1}/{len(files_to_process)}: {file_obj.filename} ==="
                file_text = f"{header}\n\n{result['full_transcript']}"
                
                all_raw_transcripts.append(file_text)
                for c_idx, c_text in enumerate(result["chunk_transcripts"]):
                    c_header = f"=== FILE {idx+1}/{len(files_to_process)}: {file_obj.filename} (Đoạn {c_idx+1}/{len(result['chunk_transcripts'])}) ==="
                    all_chunk_transcripts.append(f"{c_header}\n\n{c_text}")

                files_detail.append({
                    "filename": file_obj.filename,
                    "transcript": result["full_transcript"]
                })
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

        stt_time = time.time() - stt_start
        full_transcript = "\n\n".join(all_raw_transcripts)

        # Bước 2: Tóm tắt Map-Reduce song song các chunks của tất cả file qua Provider đã chọn
        llm_start = time.time()
        meeting_notes = generate_summary(
            all_chunk_transcripts,
            custom_prompt=custom_prompt,
            model_name=model_name,
            provider=p,
            provider_api_key=api_key
        )
        llm_time = time.time() - llm_start
        
        total_time = time.time() - start_total_time

        return JSONResponse({
            "success": True,
            "file_count": len(files_to_process),
            "total_size_mb": round(total_mb, 2),
            "raw_transcript": full_transcript,
            "files_detail": files_detail,
            "meeting_notes": meeting_notes,
            "chunk_count": len(all_chunk_transcripts),
            "stt_time": stt_time,
            "llm_time": llm_time,
            "total_time": total_time
        })

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
