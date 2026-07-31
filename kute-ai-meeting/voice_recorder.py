import time
import wave
from pathlib import Path
from typing import Callable, Dict, Optional

import discord
from pydub import AudioSegment

# Active recording sessions keyed by guild_id
_ACTIVE_RECORDINGS: Dict[int, dict] = {}


def start_voice_recording(
    guild_id: int,
    channel_id: int,
    voice_client: discord.VoiceClient,
    finished_callback: Callable,
    *callback_args,
) -> None:
    """
    Bắt đầu ghi âm cuộc họp bằng API ghi âm gốc của py-cord (VoiceClient.start_recording).
    Mỗi thành viên nói được py-cord ghi thành 1 track WAV riêng trong sink.audio_data;
    khi stop_recording() được gọi, py-cord tự chạy finished_callback(sink, *callback_args).
    """
    sink = discord.sinks.WaveSink()

    session_info = {
        "guild_id": guild_id,
        "channel_id": channel_id,
        "start_time": time.time(),
        "voice_client": voice_client,
        "sink": sink,
    }
    _ACTIVE_RECORDINGS[guild_id] = session_info

    voice_client.start_recording(sink, finished_callback, *callback_args)
    print(f"🎙️ [py-cord] Bắt đầu ghi âm Guild {guild_id} tại kênh {channel_id}")


def stop_voice_recording(guild_id: int) -> bool:
    """
    Yêu cầu dừng ghi âm. Việc xử lý audio thực sự diễn ra bất đồng bộ trong
    finished_callback đã đăng ký lúc start_voice_recording.
    """
    session = _ACTIVE_RECORDINGS.get(guild_id)
    if not session:
        return False

    voice_client = session["voice_client"]
    if getattr(voice_client, "recording", False):
        voice_client.stop_recording()
        print(f"⏹️ [py-cord] Đã gửi yêu cầu dừng ghi âm Guild {guild_id}")
    return True


def pop_recording_session(guild_id: int) -> Optional[dict]:
    """Lấy và xoá thông tin phiên ghi âm (gọi bên trong finished_callback)."""
    return _ACTIVE_RECORDINGS.pop(guild_id, None)


def is_recording(guild_id: int) -> bool:
    """Kiểm tra server có đang trong tiến trình ghi âm hay không."""
    return guild_id in _ACTIVE_RECORDINGS


def get_recording_session(guild_id: int) -> Optional[dict]:
    """Lấy thông tin phiên ghi âm hiện tại (không xoá)."""
    return _ACTIVE_RECORDINGS.get(guild_id)


def save_sink_audio(sink: "discord.sinks.Sink", session_dir: Path) -> Optional[str]:
    """
    Lưu audio riêng của từng người nói (user_<id>.<encoding>) vào session_dir,
    đồng thời gộp (overlay) tất cả track thành 1 file audio.wav duy nhất dùng cho STT.
    Trả về đường dẫn audio.wav, hoặc None nếu không ai nói (không có audio_data).
    """
    if not sink.audio_data:
        return None

    combined = None
    for user_id, audio in sink.audio_data.items():
        audio.file.seek(0)
        raw_bytes = audio.file.read()

        user_path = session_dir / f"user_{user_id}.{sink.encoding}"
        user_path.write_bytes(raw_bytes)

        try:
            segment = AudioSegment.from_file(user_path, format=sink.encoding)
        except Exception as e:
            print(f"⚠️ Lỗi decode audio user {user_id}: {e}")
            continue

        combined = segment if combined is None else combined.overlay(segment)

    if combined is None:
        return None

    combined_path = session_dir / "audio.wav"
    combined.export(combined_path, format="wav")
    print(f"⏹️ [py-cord] Đã gộp audio {len(sink.audio_data)} người nói -> {combined_path}")
    return str(combined_path)


def create_valid_empty_wav(filepath: str, duration_sec: float = 3.0):
    """Tạo 1 file WAV 48kHz Stereo im lặng để tránh lỗi STT khi không ai nói trong phòng thoại."""
    sample_rate = 48000
    num_channels = 2
    sample_width = 2
    num_frames = int(sample_rate * duration_sec)

    with wave.open(filepath, "wb") as wav_file:
        wav_file.setnchannels(num_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b"\x00" * (num_frames * num_channels * sample_width))
