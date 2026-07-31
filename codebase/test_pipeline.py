import os
import sys
import unittest
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure current directory is in PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from summarizer import generate_summary, SYSTEM_PROMPT

class TestKuteAIMeetingPipeline(unittest.TestCase):
    def setUp(self):
        self.sample_transcript = """
        Xin chào mọi người, hôm nay chúng ta họp về dự án AI Meeting Assistant.
        Tham gia cuộc họp gồm Anh Tuấn, Chị Hoa và bạn Minh.
        Vấn đề đầu tiên là mô hình nói ngọng Whisper nhiều từ chuyên ngành. Ví dụ rác hay bị nhầm với RAG, áp pi nhầm với API, hoặc làm ma nhầm với Llama 3.3.
        Anh Tuấn chốt là sẽ đưa RAG pipeline vào thử nghiệm trong tuần này, deadline là thứ sáu ngày 15/08.
        Chị Hoa sẽ chịu trách nhiệm tối ưu hóa Prompt và cấu hình GPU trên hệ thống Groq, hoàn thành trước ngày 12/08.
        Bạn Minh sẽ viết Discord Bot tích hợp Core Function này, deadline ngày 20/08.
        Có một câu hỏi mở là chúng ta nên dùng Vector Database nào: Qdrant hay Pinecone? Vấn đề này sẽ thảo luận thêm vào buổi họp tuần sau.
        """

    def test_prompt_contains_required_instructions(self):
        """Kiểm tra system prompt có đầy đủ yêu cầu sửa lỗi Whisper và trích xuất Action Items không."""
        self.assertIn("RAG", SYSTEM_PROMPT)
        self.assertIn("Whisper", SYSTEM_PROMPT)
        self.assertIn("Action Items", SYSTEM_PROMPT)

    def test_summarizer_live_or_mock(self):
        """Kiểm tra gọi hàm summarizer nếu đã cấu hình GROQ_API_KEY hợp lệ."""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your_groq_api_key_here":
            print("\n⚠️ Bỏ qua Live LLM test do chưa cung cấp GROQ_API_KEY hợp lệ trong .env")
            return
            
        print("\n🧪 Đang chạy test tích hợp thật tới Groq LLM...")
        summary = generate_summary(self.sample_transcript)
        print("\n--- KẾT QUẢ TÓM TẮT MẪU ---")
        print(summary)
        
        self.assertIn("Meeting Notes", summary)
        self.assertIn("Action Items", summary)
        self.assertIn("|", summary)  # Bảng Markdown Action Items

if __name__ == "__main__":
    unittest.main()
