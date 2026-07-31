import os
import time
import wave
import tempfile
from typing import Dict, Optional
from discord.ext import voice_recv

# Active recording sessions keyed by guild_id
_ACTIVE_RECORDINGS: Dict[int, dict] = {}

class MeetingAudioSink(voice_recv.AudioSink):
    """
    AudioSink từ discord-ext-voice-recv giải mã tự động các gói tin Opus 
    từ các thành viên trong kênh thoại Discord thành PCM 16-bit 48kHz Stereo.
    """
    def __init__(self, filepath: str):
        super().__init__()
        self.filepath = filepath
        self.wav_file = wave.open(filepath, "wb")
        self.wav_file.setnchannels(2)        # Stereo (2 channels)
        self.wav_file.setsampwidth(2)       # 16-bit PCM (2 bytes per sample)
        self.wav_file.setframerate(48000)    # 48,000 Hz sample rate từ Discord
        self.bytes_written = 0

    def wants_opus(self) -> bool:
        # Nhận PCM đã giải mã thay vì gói tin Opus thô
        return False

    def write(self, user, data: voice_recv.VoiceData):
        """Ghi dữ liệu PCM âm thanh nhận được từ người nói vào file WAV."""
        if data and data.pcm:
            try:
                self.wav_file.writeframes(data.pcm)
                self.bytes_written += len(data.pcm)
            except Exception as e:
                print(f"⚠️ Lỗi ghi frame PCM từ {user}: {e}")

    def cleanup(self):
        """Đóng file WAV an toàn."""
        try:
            if hasattr(self, "wav_file") and self.wav_file:
                self.wav_file.close()
                self.wav_file = None
        except Exception as e:
            print(f"⚠️ Lỗi đóng WAV file: {e}")

def start_voice_recording(guild_id: int, channel_id: int, voice_client: voice_recv.VoiceRecvClient) -> str:
    """
    Bắt đầu ghi âm cuộc họp trong Voice Channel sử dụng VoiceRecvClient.
    """
    temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    temp_wav_path = temp_wav.name
    temp_wav.close()

    sink = MeetingAudioSink(temp_wav_path)
    
    # Bắt đầu lắng nghe audio packets từ Discord
    if hasattr(voice_client, "listen"):
        voice_client.listen(sink)

    session_info = {
        "guild_id": guild_id,
        "channel_id": channel_id,
        "start_time": time.time(),
        "output_path": temp_wav_path,
        "voice_client": voice_client,
        "sink": sink
    }

    _ACTIVE_RECORDINGS[guild_id] = session_info
    print(f"🎙️ [VoiceRecv] Bắt đầu ghi âm Guild {guild_id} tại kênh {channel_id} -> {temp_wav_path}")
    return temp_wav_path

def stop_voice_recording(guild_id: int) -> Optional[str]:
    """
    Dừng ghi âm cuộc họp, giải phóng AudioSink và đóng file WAV.
    """
    if guild_id not in _ACTIVE_RECORDINGS:
        return None

    session = _ACTIVE_RECORDINGS.pop(guild_id)
    output_path = session["output_path"]
    voice_client = session.get("voice_client")
    sink = session.get("sink")

    # Dừng lắng nghe
    if voice_client and hasattr(voice_client, "stop_listening"):
        try:
            voice_client.stop_listening()
        except Exception as e:
            print(f"⚠️ Lỗi khi gọi stop_listening: {e}")

    if sink:
        sink.cleanup()

    # Kiểm tra kích thước file WAV sau khi đóng
    if os.path.exists(output_path):
        file_size = os.path.getsize(output_path)
        bytes_written = getattr(sink, "bytes_written", 0) if sink else 0
        print(f"⏹️ [VoiceRecv] Dừng ghi âm Guild {guild_id}. File: {output_path} ({file_size} bytes, PCM written: {bytes_written} bytes)")

        # Nếu không có tiếng nói trong kênh thoại (PCM written == 0 hoặc file WAV chỉ có header 44 bytes),
        # tạo 2s im lặng để Whisper không bị sập
        if file_size <= 44 or bytes_written == 0:
            print("⚠️ Không ghi nhận được giọng nói nào trong phòng thoại. Tạo file WAV mẫu im lặng...")
            _create_valid_empty_wav(output_path, duration_sec=3.0)

    return output_path

def is_recording(guild_id: int) -> bool:
    """Kiểm tra server có đang trong tiến trình ghi âm hay không."""
    return guild_id in _ACTIVE_RECORDINGS

def get_recording_session(guild_id: int) -> Optional[dict]:
    """Lấy thông tin phiên ghi âm hiện tại."""
    return _ACTIVE_RECORDINGS.get(guild_id)

def _create_valid_empty_wav(filepath: str, duration_sec: float = 3.0):
    """Tạo 1 file WAV 48kHz Stereo im lặng 3s để tránh lỗi Whisper với file rỗng."""
    sample_rate = 48000
    num_channels = 2
    sample_width = 2
    num_frames = int(sample_rate * duration_sec)
    
    with wave.open(filepath, 'wb') as wav_file:
        wav_file.setnchannels(num_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b'\x00' * (num_frames * num_channels * sample_width))
