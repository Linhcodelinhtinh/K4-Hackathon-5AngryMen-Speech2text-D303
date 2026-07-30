import os
import sys
import math
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from groq import Groq

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Automatically resolve FFmpeg binaries for Windows/Mac/Linux
try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except Exception as e:
    print(f"⚠️ static_ffmpeg warning: {e}")

MAX_FILE_SIZE_MB = 24

def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key.strip() in ["", "your_groq_api_key_here", "gsk_your_groq_api_key_here"]:
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

def transcribe_audio_with_chunks(audio_path: str, model_name: str = "whisper-large-v3", language: str = None) -> dict:
    """
    Thực hiện Speech-to-Text cho file âm thanh MP3.
    Nếu file > 24MB, tự động chia cắt thành các đoạn 10 phút,
    transcribe song song và trả về cả full_transcript và danh sách chunk_transcripts.
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
        transcript = _transcribe_single_file(client, audio_path, model_name, language).strip()
        return {
            "full_transcript": transcript,
            "chunk_transcripts": [transcript]
        }

    # Trường hợp 2: File > 24MB, chia nhỏ và xử lý song song với pydub
    print(f"📦 File > {MAX_FILE_SIZE_MB}MB. Chia cắt âm thanh thành các đoạn 10 phút và transcribe song song...")
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
    
    # Cắt file âm thanh thành các temporary files
    temp_chunk_files = []
    for index in range(total_chunks):
        start_ms = index * chunk_length_ms
        end_ms = min((index + 1) * chunk_length_ms, total_length_ms)
        chunk_sound = sound[start_ms:end_ms]
        
        tmp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        tmp_path = tmp_file.name
        tmp_file.close()
        
        chunk_sound.export(tmp_path, format="mp3")
        temp_chunk_files.append((index, tmp_path))

    chunk_transcripts = [None] * total_chunks

    def _process_chunk_file(idx: int, path: str) -> tuple[int, str]:
        try:
            print(f"⏳ Đang transcribe chunk {idx + 1}/{total_chunks}...")
            text = _transcribe_single_file(client, path, model_name, language)
            return idx, text.strip()
        finally:
            if os.path.exists(path):
                os.remove(path)

    # Chạy song song Whisper API cho các chunk với ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=min(3, total_chunks)) as executor:
        futures = [executor.submit(_process_chunk_file, idx, path) for idx, path in temp_chunk_files]
        for future in as_completed(futures):
            idx, text = future.result()
            chunk_transcripts[idx] = text
            print(f"✅ Hoàn tất Transcribe đoạn {idx + 1}/{total_chunks}")

    full_transcript = "\n\n".join(chunk_transcripts).strip()
    return {
        "full_transcript": full_transcript,
        "chunk_transcripts": chunk_transcripts
    }

def transcribe_audio(audio_path: str, model_name: str = "whisper-large-v3", language: str = None) -> str:
    """Hàm wrapper tương thích ngược, trả về chuỗi full_transcript."""
    result = transcribe_audio_with_chunks(audio_path, model_name, language)
    return result["full_transcript"]

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        file_arg = sys.argv[1]
        try:
            res = transcribe_audio_with_chunks(file_arg)
            print("\n--- FULL TRANSCRIPT RESULT ---")
            print(res["full_transcript"][:500] + ("..." if len(res["full_transcript"]) > 500 else ""))
            print(f"\n🧩 Tổng số chunks: {len(res['chunk_transcripts'])}")
        except Exception as err:
            print(f"❌ Lỗi: {err}")
    else:
        print("Sử dụng: python stt_service.py <duong_dan_file_mp3>")
