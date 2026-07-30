import os
import sys
import uvicorn
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from api.index import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print("\n" + "="*60)
    print("🚀 KHỞI CHẠY WEB UI KUTE AI MEETING")
    print("="*60)
    print(f"🌐 Mở trình duyệt tại: http://localhost:{port}")
    print("="*60 + "\n")
    uvicorn.run("api.index:app", host="0.0.0.0", port=port, reload=True)
