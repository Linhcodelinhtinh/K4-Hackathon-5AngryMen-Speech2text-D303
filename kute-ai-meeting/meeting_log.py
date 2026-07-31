import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).parent.resolve()
MEETING_LOG_DIR = BASE_DIR / "meeting_log"


def _safe_name(value: str, max_len: int = 40) -> str:
    """Chuyển tên (channel/guild) thành chuỗi an toàn để đặt tên thư mục."""
    cleaned = "".join(c if c.isalnum() or c in "-_" else "_" for c in value)
    return cleaned[:max_len] or "unknown"


def start_session(guild_id: int, channel_name: str, source: str, metadata: Optional[dict] = None) -> Path:
    """
    Tạo 1 session_dir riêng trong meeting_log/ ngay khi Bot được gọi
    (lúc nhận lệnh !note hoặc !start), trước khi audio được tải về/ghi âm,
    để toàn bộ dữ liệu của phiên (audio, transcript, notes, metadata) nằm
    cùng 1 thư mục và được ghi trực tiếp vào đó thay vì file tạm.
    """
    MEETING_LOG_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_id = f"{timestamp}_{guild_id}_{source}_{_safe_name(channel_name)}_{uuid.uuid4().hex[:6]}"
    session_dir = MEETING_LOG_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    start_metadata = {
        "session_id": session_id,
        "source": source,
        "guild_id": guild_id,
        "started_at": datetime.now().isoformat(),
        **(metadata or {}),
    }
    (session_dir / "metadata.json").write_text(
        json.dumps(start_metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return session_dir


def audio_path_for(session_dir: Path, ext: str = ".wav") -> Path:
    """Đường dẫn file audio cố định bên trong session_dir (dùng ngay khi ghi/tải audio)."""
    if not ext.startswith("."):
        ext = f".{ext}"
    return session_dir / f"audio{ext}"


def finalize_session(
    session_dir: Path,
    raw_transcript: str,
    meeting_notes: str,
    extra_metadata: Optional[dict] = None,
) -> Path:
    """
    Ghi transcript + meeting notes và cập nhật metadata khi cuộc họp kết thúc.
    Audio đã được ghi trực tiếp vào session_dir từ lúc bắt đầu nên không cần copy lại.
    """
    (session_dir / "transcript.txt").write_text(raw_transcript or "", encoding="utf-8")
    (session_dir / "meeting_notes.md").write_text(meeting_notes or "", encoding="utf-8")

    metadata_path = session_dir / "metadata.json"
    metadata = {}
    if metadata_path.exists():
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except Exception:
            metadata = {}
    metadata.update(extra_metadata or {})
    metadata["ended_at"] = datetime.now().isoformat()
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    return session_dir
