import os
import sys
import time
import argparse
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from stt_service import transcribe_audio
from summarizer import generate_summary

def run_meeting_pipeline(audio_path: str, output_dir: str = None, provider: str = "groq", model_name: str = None) -> dict:
    """
    Chạy toàn bộ pipeline xử lý cuộc họp:
    MP3 -> Speech-to-Text -> raw_transcript.txt -> LLM Summary -> meeting_notes.md
    """
    start_total_time = time.time()
    
    audio_file = Path(audio_path).resolve()
    if not audio_file.exists():
        raise FileNotFoundError(f"❌ File ghi âm không tồn tại: {audio_path}")
        
    if output_dir:
        out_path = Path(output_dir).resolve()
    else:
        out_path = audio_file.parent / f"{audio_file.stem}_output"
        
    out_path.mkdir(parents=True, exist_ok=True)
    
    transcript_file = out_path / "raw_transcript.txt"
    notes_file = out_path / "meeting_notes.md"
    
    print("\n" + "="*60)
    print("🚀 BẮT ĐẦU PIPELINE XỬ LÝ GHI ÂM CUỘC HỌP (KUTE AI MEETING)")
    print("="*60)
    print(f"📁 File đầu vào: {audio_file}")
    print(f"📂 Thư mục đầu ra: {out_path}")
    print(f"🤖 LLM Provider: {provider.upper()} | Model: {model_name or 'Default'}\n")
    
    # Bước 1: Speech-to-Text
    print("--- [BƯỚC 1/2] Speech-to-Text (Groq Whisper Large V3) ---")
    stt_start = time.time()
    raw_transcript = transcribe_audio(str(audio_file))
    stt_time = time.time() - stt_start
    print(f"✅ Hoàn thành Speech-to-Text trong {stt_time:.2f} giây.")
    
    # Lưu raw_transcript.txt
    with open(transcript_file, "w", encoding="utf-8") as f:
        f.write(raw_transcript)
    print(f"💾 Đã lưu transcript thô tại: {transcript_file}\n")
    
    # Bước 2: Tóm tắt bằng LLM
    print(f"--- [BƯỚC 2/2] LLM Summarization ({provider.upper()}) ---")
    llm_start = time.time()
    meeting_notes = generate_summary(raw_transcript, provider=provider, model_name=model_name)
    llm_time = time.time() - llm_start
    print(f"✅ Hoàn thành tóm tắt cuộc họp trong {llm_time:.2f} giây.")
    
    # Lưu meeting_notes.md
    with open(notes_file, "w", encoding="utf-8") as f:
        f.write(meeting_notes)
    print(f"💾 Đã lưu Meeting Notes Markdown tại: {notes_file}\n")
    
    total_time = time.time() - start_total_time
    
    print("="*60)
    print("🎉 PIPELINE HOÀN THÀNH THÀNH CÔNG!")
    print("="*60)
    print(f"⏱️ Tổng thời gian xử lý: {total_time:.2f} giây")
    print(f"  └─ Speech-to-Text: {stt_time:.2f}s")
    print(f"  └─ LLM Summary   : {llm_time:.2f}s")
    print("\n📄 Danh sách file kết quả:")
    print(f"  1. Raw Transcript: {transcript_file}")
    print(f"  2. Meeting Notes : {notes_file}")
    print("="*60 + "\n")
    
    return {
        "transcript_path": str(transcript_file),
        "notes_path": str(notes_file),
        "stt_time": stt_time,
        "llm_time": llm_time,
        "total_time": total_time
    }

def main():
    parser = argparse.ArgumentParser(description="Kute AI Meeting: Xử lý MP3 -> STT -> LLM Summary -> Markdown Meeting Notes")
    parser.add_argument("audio_path", nargs="?", help="Đường dẫn tới file ghi âm MP3")
    parser.add_argument("-o", "--output-dir", help="Thư mục lưu kết quả đầu ra (mặc định tạo thư mục cạnh file MP3)")
    parser.add_argument("-p", "--provider", default="groq", choices=["groq", "openrouter", "gemini"], help="Nhà cung cấp LLM (groq, openrouter, gemini)")
    parser.add_argument("-m", "--model", help="Mô hình LLM tùy chỉnh (VD: gemini-2.5-flash, meta-llama/llama-3.3-70b-instruct)")
    
    args = parser.parse_args()
    
    if not args.audio_path:
        print("⚠️ Chưa cung cấp đường dẫn file MP3.")
        audio_path = input("Vui lòng nhập đường dẫn file MP3 ghi âm cuộc họp: ").strip().strip('"').strip("'")
    else:
        audio_path = args.audio_path
        
    try:
        run_meeting_pipeline(audio_path, args.output_dir, provider=args.provider, model_name=args.model)
    except Exception as e:
        print(f"\n❌ LỖI TRONG QUÁ TRÌNH XỬ LÝ: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
