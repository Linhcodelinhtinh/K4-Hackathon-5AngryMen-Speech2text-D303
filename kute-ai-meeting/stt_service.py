import os
import sys
import math
import tempfile
from dotenv import load_dotenv
from groq import Groq

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Load environment variables from .env
load_dotenv()

MAX_FILE_SIZE_MB = 24

def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError("GROQ_API_KEY chưa được cấu hình. Vui lòng cập nhật file .env!")
    return Groq(api_key=api_key)

def _transcribe_single_file(client: Groq, file_path: str, model_name: str = "whisper-large-v3", language: str = None) -> str:
    """Gửi 1 file âm thanh trực tiếp đến Groq API để transcribe."""
    with open(file_path, "rb") as audio_file:
        kwargs = {
            "file": (os.path.basename(file_path), audio_file),
            "model": model_name,
            "response_format": "text"
        }
        if language:
            kwargs["language"] = language
            
        response = client.audio.transcriptions.create(**kwargs)
        if isinstance(response, str):
            return response
        elif hasattr(response, "text"):
            return response.text
        return str(response)

def transcribe_audio(audio_path: str, model_name: str = "whisper-large-v3", language: str = None) -> str:
    """
    Thực hiện Speech-to-Text cho file âm thanh MP3.
    Tự động chia nhỏ file nếu kích thước vượt quá 24MB.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Không tìm thấy file ghi âm: {audio_path}")
    
    file_size_bytes = os.path.getsize(audio_path)
    file_size_mb = file_size_bytes / (1024 * 1024)
    print(f"🎙️ Đang xử lý file audio: {audio_path} ({file_size_mb:.2f} MB)")
    
    client = get_groq_client()
    
    # Trường hợp 1: File <= 24MB, gửi trực tiếp
    if file_size_mb <= MAX_FILE_SIZE_MB:
        print("⚡ File ≤ 24MB, gửi trực tiếp đến Groq Whisper API...")
        transcript = _transcribe_single_file(client, audio_path, model_name, language)
        return transcript.strip()

    # Trường hợp 2: File > 24MB, chia nhỏ bằng pydub
    print(f"📦 File > {MAX_FILE_SIZE_MB}MB. Tiến hành chia cắt file âm thanh thành các đoạn 10 phút...")
    try:
        from pydub import AudioSegment
    except ImportError:
        raise ImportError("Thiếu thư viện 'pydub'. Vui lòng chạy: pip install pydub")

    try:
        sound = AudioSegment.from_file(audio_path)
    except Exception as e:
        raise RuntimeError(f"Lỗi khi đọc file âm thanh bằng pydub (Hãy đảm bảo FFmpeg đã được cài đặt): {str(e)}")

    chunk_length_ms = 10 * 60 * 1000  # 10 phút = 600,000 ms
    total_length_ms = len(sound)
    total_chunks = math.ceil(total_length_ms / chunk_length_ms)
    
    print(f"🧩 Tổng thời lượng: {total_length_ms / 1000 / 60:.2f} phút. Chia thành {total_chunks} đoạn.")
    
    transcripts = []
    for index in range(total_chunks):
        start_ms = index * chunk_length_ms
        end_ms = min((index + 1) * chunk_length_ms, total_length_ms)
        chunk_sound = sound[start_ms:end_ms]
        
        # Lưu temporary chunk file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            print(f"⏳ Đang xử lý chunk {index + 1}/{total_chunks} (từ {start_ms/1000:.0f}s đến {end_ms/1000:.0f}s)...")
            chunk_sound.export(tmp_path, format="mp3")
            chunk_text = _transcribe_single_file(client, tmp_path, model_name, language)
            if chunk_text:
                transcripts.append(chunk_text.strip())
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    full_transcript = "\n\n".join(transcripts)
    return full_transcript.strip()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        file_arg = sys.argv[1]
        try:
            res = transcribe_audio(file_arg)
            print("\n--- TRANSCRIPT RESULT ---")
            print(res[:500] + ("..." if len(res) > 500 else ""))
        except Exception as err:
            print(f"❌ Lỗi: {err}")
    else:
        print("Sử dụng: python stt_service.py <duong_dan_file_mp3>")
