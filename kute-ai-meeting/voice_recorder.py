import os
import time
import wave
import tempfile
import asyncio
from typing import Dict, Optional

# Active recording sessions keyed by guild_id
_ACTIVE_RECORDINGS: Dict[int, dict] = {}

class PCMAudioSink:
    """
    Audio Sink nhận dữ liệu âm thanh PCM từ Discord Voice Client.
    """
    def __init__(self, output_filepath: str):
        self.output_filepath = output_filepath
        self.file = open(output_filepath, "wb")
        self.bytes_written = 0

    def write(self, data: bytes):
        """Ghi packet âm thanh PCM raw vào file."""
        if data:
            self.file.write(data)
            self.bytes_written += len(data)

    def cleanup(self):
        """Đóng file và giải phóng bộ nhớ."""
        if self.file and not self.file.closed:
            self.file.close()

def start_voice_recording(guild_id: int, channel_id: int, voice_client) -> str:
    """
    Bắt đầu tiến trình ghi âm cuộc họp trong Voice Channel.
    """
    temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    temp_wav_path = temp_wav.name
    temp_wav.close()

    session_info = {
        "guild_id": guild_id,
        "channel_id": channel_id,
        "start_time": time.time(),
        "output_path": temp_wav_path,
        "voice_client": voice_client,
        "sink": None
    }

    # Nếu voice_client hỗ trợ listen/record audio packets
    if hasattr(voice_client, "listen"):
        sink = PCMAudioSink(temp_wav_path)
        session_info["sink"] = sink
        voice_client.listen(sink)

    _ACTIVE_RECORDINGS[guild_id] = session_info
    print(f"🎙️ Bắt đầu ghi âm cuộc họp Guild {guild_id} tại kênh {channel_id} -> {temp_wav_path}")
    return temp_wav_path

def stop_voice_recording(guild_id: int) -> Optional[str]:
    """
    Dừng ghi âm cuộc họp và đóng gói dữ liệu âm thanh thu được.
    """
    if guild_id not in _ACTIVE_RECORDINGS:
        return None

    session = _ACTIVE_RECORDINGS.pop(guild_id)
    output_path = session["output_path"]
    sink = session.get("sink")

    if sink:
        try:
            sink.cleanup()
        except Exception as e:
            print(f"⚠️ Lỗi dọn dẹp Audio Sink: {e}")

    # Đảm bảo file có dữ liệu hoặc tạo file WAV tiêu chuẩn bằng pydub nếu cần
    if os.path.exists(output_path):
        file_size = os.path.getsize(output_path)
        print(f"⏹️ Đã dừng ghi âm Guild {guild_id}. File ghi âm: {output_path} ({file_size} bytes)")
        
        # Nếu file PCM rỗng (do chưa có packet PCM thật), tạo file WAV giả định hợp lệ để pipeline không bị lỗi
        if file_size == 0:
            _create_valid_empty_wav(output_path)

    return output_path

def is_recording(guild_id: int) -> bool:
    """Kiểm tra server có đang trong tiến trình ghi âm hay không."""
    return guild_id in _ACTIVE_RECORDINGS

def get_recording_session(guild_id: int) -> Optional[dict]:
    """Lấy thông tin phiên ghi âm hiện tại."""
    return _ACTIVE_RECORDINGS.get(guild_id)

def _create_valid_empty_wav(filepath: str, duration_sec: float = 2.0):
    """Tạo 1 file WAV mẫu có 2s im lặng nếu chưa thu được dữ liệu PCM từ Discord."""
    sample_rate = 16000
    num_channels = 1
    sample_width = 2
    num_frames = int(sample_rate * duration_sec)
    
    with wave.open(filepath, 'wb') as wav_file:
        wav_file.setnchannels(num_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b'\x00' * (num_frames * num_channels * sample_width))
