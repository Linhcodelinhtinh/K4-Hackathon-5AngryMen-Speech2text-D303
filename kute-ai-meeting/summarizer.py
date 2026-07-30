import os
import sys
from dotenv import load_dotenv
from groq import Groq

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Load environment variables
load_dotenv()

DEFAULT_MODEL = "llama-3.3-70b-versatile"

def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError("GROQ_API_KEY chưa được cấu hình trong file .env!")
    return Groq(api_key=api_key)

SYSTEM_PROMPT = """Bạn là một Chuyên gia Thư ký Cuộc họp AI (AI Meeting Assistant) chuyên nghiệp.
Nhiệm vụ của bạn là nhận bản ghi chép cuộc họp thô (raw transcript từ Speech-to-Text) và tổng hợp thành Biên bản Cuộc họp (Meeting Notes) bằng định dạng Markdown hoàn chỉnh và thẩm mỹ.

YÊU CẦU BẮT BUỘC:
1. SỬA LỖI CHÍNH TẢ & PHÁT ÂM: Tự động phát hiện và sửa các lỗi chính tả, nói ngọng hoặc từ Whisper nghe nhầm (Ví dụ: "rác" -> "RAG", "bi iu" -> "BU", "làm ma" -> "Llama", "gê bê tê" -> "GPT", "áp pi" -> "API", v.v.).
2. THUẬT NGỮ CHUYÊN NGÀNH AI/TECH: Hiểu và giữ chuẩn các thuật ngữ AI và công nghệ tiếng Anh (Ví dụ: Prompt, RAG, GPU, API, Fine-tuning, LLM, Vector Database, Benchmark, KPI, Sprint, Stakeholder...).
3. TRUNG THỰC VỚI TRANSCRIPT: Chỉ trích xuất và tóm tắt dựa trên thông tin thực sự có trong transcript. Tuyệt đối không tự suy diễn hoặc bịa thêm thông tin bên ngoài.
4. ĐỊNH DẠNG ĐẦU RẠ: Trả về duy nhất nội dung Markdown với cấu trúc tiêu chuẩn bên dưới.

CẤU TRÚC MARKDOWN YÊU CẦU:

# Meeting Notes: [Đặt tiêu đề cuộc họp phù hợp dựa trên nội dung]

## 1. Executive Summary
- [Tóm tắt ngắn gọn 3-5 câu về mục đích chính và kết quả chung của cuộc họp]

## 2. Key Takeaways
- [Điểm quan trọng 1]
- [Điểm quan trọng 2]
- [Các quyết định chính đã được đồng thuận]

## 3. Action Items
| Task / Nhiệm vụ | Assignee / Người phụ trách | Deadline / Thời hạn |
| :--- | :--- | :--- |
| [Tên công việc cụ thể] | [Tên người được giao hoặc 'Chưa xác định'] | [Thời gian/hạn chót hoặc 'Chưa xác định'] |

## 4. Open Questions & Follow-ups
- [Câu hỏi 1 còn bỏ ngỏ hoặc chưa được giải quyết]
- [Vấn đề cần thảo luận thêm trong cuộc họp sau]
"""

def generate_summary(transcript: str, model_name: str = DEFAULT_MODEL) -> str:
    """
    Nhận transcript thô và sinh Meeting Notes dạng Markdown sử dụng LLM trên Groq.
    """
    if not transcript or not transcript.strip():
        raise ValueError("Transcript trống, không thể thực hiện tóm tắt.")

    print(f"🧠 Đang gửi transcript ({len(transcript)} ký tự) tới Groq LLM ({model_name})...")
    client = get_groq_client()

    user_content = f"Dưới đây là bản transcript thô của cuộc họp:\n\n---\n{transcript}\n---\n\nHãy tạo Meeting Notes Markdown chuẩn hóa theo đúng yêu cầu."

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ],
        temperature=0.3,
        max_tokens=4096
    )

    result_text = response.choices[0].message.content
    return result_text.strip()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            content = f.read()
        summary = generate_summary(content)
        print("\n--- SUMMARY RESULT ---")
        print(summary)
    else:
        print("Sử dụng: python summarizer.py <duong_dan_file_raw_transcript.txt>")
