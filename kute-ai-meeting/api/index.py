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

@app.post("/api/transcribe")
async def transcribe_endpoint(
    audio_file: UploadFile = File(...),
    groq_api_key: str = Form(None)
):
    if groq_api_key and groq_api_key.strip():
        os.environ["GROQ_API_KEY"] = groq_api_key.strip()
    
    current_key = os.getenv("GROQ_API_KEY")
    if not current_key or current_key == "your_groq_api_key_here":
        raise HTTPException(status_code=400, detail="GROQ_API_KEY chưa được cấu hình!")
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.post("/api/summarize")
async def summarize_endpoint(req: SummarizeRequest):
    if req.groq_api_key and req.groq_api_key.strip():
        os.environ["GROQ_API_KEY"] = req.groq_api_key.strip()
        
    current_key = os.getenv("GROQ_API_KEY")
    if not current_key or current_key == "your_groq_api_key_here":
        raise HTTPException(status_code=400, detail="GROQ_API_KEY chưa được cấu hình!")
    if not req.raw_transcript or not req.raw_transcript.strip():
        raise HTTPException(status_code=400, detail="Nội dung Raw Transcript trống!")
    try:
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
