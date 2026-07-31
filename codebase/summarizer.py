import os
import sys
import math
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from groq import Groq

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Load environment variables
load_dotenv()

DEFAULT_MODEL = "meta-llama/llama-3.3-70b-instruct"
DEFAULT_PROVIDER = "openrouter"
MAX_SINGLE_PASS_CHARS = 12000  # Ngưỡng ký tự để chuyển sang chế độ Chunk Map-Reduce

PROVIDER_MODELS = {
    "groq": {
        "default": "llama-3.3-70b-versatile",
        "fallbacks": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
    },
    "openrouter": {
        "default": "meta-llama/llama-3.3-70b-instruct",
        "fallbacks": ["meta-llama/llama-3.3-70b-instruct", "anthropic/claude-3.5-sonnet", "deepseek/deepseek-r1"]
    },
    "gemini": {
        "default": "gemini-3.5-flash",
        "fallbacks": ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.5-pro", "gemini-1.5-pro"]
    }
}

def get_provider_api_key(provider: str = "openrouter", override_key: str = None) -> str:
    provider = (provider or "openrouter").lower().strip()
    if override_key and override_key.strip():
        key = override_key.strip()
        if provider == "groq":
            os.environ["GROQ_API_KEY"] = key
        elif provider == "openrouter":
            os.environ["OPENROUTER_API_KEY"] = key
        elif provider == "gemini":
            os.environ["GEMINI_API_KEY"] = key
        return key

    env_map = {
        "groq": "GROQ_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
        "gemini": "GEMINI_API_KEY"
    }
    env_var = env_map.get(provider, "OPENROUTER_API_KEY")
    key = os.getenv(env_var)
    if not key or key.strip() in ["", "your_groq_api_key_here", "gsk_your_groq_api_key_here", "your_openrouter_api_key_here", "your_gemini_api_key_here"]:
        raise ValueError(f"Thiếu {env_var}. Vui lòng nhập API Key cho provider '{provider}' trên giao diện Web hoặc file .env!")
    return key.strip()

def get_groq_client() -> Groq:
    api_key = get_provider_api_key("groq")
    return Groq(api_key=api_key)

def call_llm_api(messages: list, provider: str = "openrouter", model_name: str = None, provider_api_key: str = None, temperature: float = 0.3, max_tokens: int = 4096) -> str:
    """Gọi LLM API tương ứng với Provider (Groq, OpenRouter, Gemini) có tích hợp Fallback."""
    provider = (provider or "groq").lower().strip()
    api_key = get_provider_api_key(provider, provider_api_key)

    p_config = PROVIDER_MODELS.get(provider, PROVIDER_MODELS["groq"])
    chosen_model = model_name.strip() if (model_name and model_name.strip()) else p_config["default"]
    models_to_try = [chosen_model] + [m for m in p_config["fallbacks"] if m != chosen_model]

    sys_prompt = ""
    user_content = ""
    for msg in messages:
        if msg.get("role") == "system":
            sys_prompt = msg.get("content", "")
        elif msg.get("role") == "user":
            user_content = msg.get("content", "")

    last_exception = None

    for model in models_to_try:
        try:
            print(f"🧠 Gửi request tới LLM Provider [{provider.upper()}] model: {model}...")
            
            if provider == "groq":
                client = Groq(api_key=api_key)
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content.strip()

            elif provider == "openrouter":
                from openai import OpenAI
                client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=api_key
                )
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    extra_headers={
                        "HTTP-Referer": "https://kute-ai-meeting.local",
                        "X-Title": "Kute AI Meeting Notes"
                    }
                )
                return response.choices[0].message.content.strip()

            elif provider == "gemini":
                from google import genai
                client = genai.Client(api_key=api_key)
                
                config = genai.types.GenerateContentConfig(
                    system_instruction=sys_prompt if sys_prompt else None,
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
                response = client.models.generate_content(
                    model=model,
                    contents=user_content,
                    config=config
                )
                if hasattr(response, "text") and response.text:
                    return response.text.strip()
                return str(response).strip()

            else:
                raise ValueError(f"Provider '{provider}' không được hỗ trợ!")

        except Exception as e:
            print(f"⚠️ Provider [{provider.upper()}] model '{model}' gặp sự cố ({e}). Kích hoạt Fallback...")
            last_exception = e

    raise last_exception

def call_groq_with_fallback(messages: list, temperature: float = 0.3, max_tokens: int = 4096, preferred_model: str = DEFAULT_MODEL) -> str:
    """Wrapper tương thích ngược cho Groq fallback."""
    return call_llm_api(messages, provider="groq", model_name=preferred_model, temperature=temperature, max_tokens=max_tokens)

SYSTEM_PROMPT = """Bạn là một Chuyên gia Thư ký Cuộc họp AI (AI Meeting Assistant) chuyên nghiệp.
Nhiệm vụ của bạn là nhận bản ghi chép cuộc họp thô (raw transcript từ Speech-to-Text) và tổng hợp thành Biên bản Cuộc họp (Meeting Notes) bằng định dạng Markdown.

YÊU CẦU BẮT BUỘC:
1. KHÔNG ĐƯỢC BỎ SÓT FILE NÀO (NẾU CÓ NHIỀU FILE): Phân tách bởi '=== FILE 1: ... ===', '=== FILE 2: ... ==='. Bạn BẮT BUỘC phải đọc và tóm tắt nội dung của TẤT CẢ các file được cung cấp. Tuyệt đối không chỉ tóm tắt file cuối cùng!
2. SỬA LỖI CHÍNH TẢ & PHÁT ÂM: Tự động phát hiện và sửa các lỗi chính tả, nói ngọng hoặc từ Whisper nghe nhầm (Ví dụ: "rác" -> "RAG", "bi iu" -> "BU", "làm ma" -> "Llama", "gê bê tê" -> "GPT", "áp pi" -> "API", v.v.).
3. THUẬT NGỮ CHUYÊN NGÀNH AI/TECH: Hiểu và giữ chuẩn các thuật ngữ AI và công nghệ tiếng Anh (Ví dụ: Prompt, RAG, GPU, API, Fine-tuning, LLM, Vector Database, Benchmark, KPI, Sprint, Stakeholder...).
4. TRUNG THỰC VỚI TRANSCRIPT: Chỉ trích xuất dựa trên thông tin thực sự có trong transcript.
5. CHI TIẾT TỪNG FILE (NẾU ĐA FILE): Ở cuối bài, bạn BẮT BUỘC phải tạo các thẻ đóng/mở `<details><summary>📁 Chi tiết Tóm tắt: [Tên File]</summary> ... </details>` CHO MỖI FILE CÓ TRONG TRANSCRIPT.

CẤU TRÚC MARKDOWN YÊU CẦU:

# Meeting Notes: [Đặt tiêu đề cuộc họp tổng quan]

## 📌 Executive Master Summary
- [Tóm tắt 3-5 câu bao quát toàn bộ nội dung của TẤT CẢ các file]

## 📌 Key Takeaways & Quyết định chính
- [Tổng hợp các điểm cốt lõi và quyết định quan trọng từ TẤT CẢ các file]

## 📌 Action Items Hợp nhất
| Task / Nhiệm vụ | Assignee / Người phụ trách | Deadline / Thời hạn |
| :--- | :--- | :--- |
| [Tên công việc] | [Người được giao] | [Hạn chót] |

## 📌 Open Questions & Follow-ups
- [Câu hỏi tồn đọng]

## 📁 Chi tiết từng File Cuộc họp

<details>
<summary>📁 Chi tiết Tóm tắt: [Tên File 1]</summary>

- **Ý chính**: [Nội dung file 1]
- **Action Items riêng**: [Công việc riêng file 1]

</details>
"""

# Prompt cho bước Map (Tóm tắt từng chunk nhỏ)
CHUNK_MAP_PROMPT = """Bạn là Thư ký Cuộc họp AI.
Nhiệm vụ: Trích xuất các ý chính của đoạn ghi âm cuộc họp (Đoạn {chunk_index}/{total_chunks}).

YÊU CẦU BẮT BUỘC:
1. NẾU ĐOẠN CÓ GHI TÊN FILE (Ví dụ '=== FILE 1/3: audio1.mp3 ... ==='): Bạn BẮT BUỘC phải giữ nguyên dòng thông tin TÊN FILE đó ở đầu bản tóm tắt đoạn này.
2. Trích xuất ngắn gọn: Ý kiến thảo luận chính, Quyết định đã đưa ra, và các Action Items.
3. Chuẩn hóa ngay các thuật ngữ AI/Tech (RAG, LLM, API, GPU, Fine-tuning...).
4. Viết dưới dạng các gạch đầu dòng cô đọng.
"""

# Prompt cho bước Reduce (Tổng hợp tất cả chunk summaries thành Meeting Notes hoàn chỉnh)
REDUCE_AGGREGATE_PROMPT = """Bạn là Chuyên gia Thư ký Cuộc họp AI cao cấp.
Dưới đây là danh sách các bản tóm tắt từng đoạn (Chunk Summaries) của một cuộc họp hoặc chuỗi nhiều file ghi âm cuộc họp khác nhau.

Nhiệm vụ của bạn: TỔNG HỢP VÀ HỢP NHẤT toàn bộ thông tin thành một BIÊN BẢN CUỘC HỌP (Meeting Notes) hoàn chỉnh.

⚠️ YÊU CẦU BẮT BUỘC KHI CÓ NHIỀU FILE GHI ÂM (FILE 1, FILE 2, FILE 3...):
1. TẤT CẢ CÁC FILE ĐỀU BẮT BUỘC PHẢI ĐƯỢC TÓM TẮT: Tuyệt đối KHÔNG ĐƯỢC chỉ tóm tắt file cuối cùng! Bạn phải tổng hợp nội dung của TẤT CẢ các file trong danh sách.
2. BÁO CÁO TỔNG HỢP CHUNG: Phần Executive Master Summary, Key Takeaways và Action Items Hợp nhất phải bao quát thông tin từ TẤT CẢ các file.
3. CHI TIẾT TỪNG FILE: Ở cuối bài, bạn BẮT BUỘC phải tạo thẻ HTML/Markdown `<details><summary>📁 Chi tiết Tóm tắt: [Tên File]</summary> ... </details>` CHO MỖI FILE TRONG DANH SÁCH.

CẤU TRÚC MARKDOWN YÊU CẦU:

# Meeting Notes: [Đặt tiêu đề cuộc họp / chuỗi cuộc họp tổng quan]

## 📌 Executive Master Summary
- [Tóm tắt 3-5 câu bao quát toàn bộ nội dung của TẤT CẢ các file]

## 📌 Key Takeaways & Quyết định chính
- [Các điểm cốt lõi và quyết định quan trọng từ TẤT CẢ các file]

## 📌 Action Items Hợp nhất
| Task / Nhiệm vụ | Assignee / Người phụ trách | Deadline / Thời hạn |
| :--- | :--- | :--- |
| [Công việc cụ thể] | [Người thực hiện] | [Hạn chót] |

## 📌 Open Questions & Follow-ups
- [Các vấn đề còn tồn đọng]

## 📁 Chi tiết từng File Cuộc họp

<details>
<summary>📁 Chi tiết Tóm tắt: [Tên File 1]</summary>

- **Nội dung chính**: [Ý chính của file 1]
- **Quyết định & Action items riêng**: [Nhiệm vụ riêng file 1]

</details>

<details>
<summary>📁 Chi tiết Tóm tắt: [Tên File 2]</summary>

- **Nội dung chính**: [Ý chính của file 2]
- **Quyết định & Action items riêng**: [Nhiệm vụ riêng file 2]

</details>
"""

def summarize_single_chunk(chunk_text: str, chunk_index: int, total_chunks: int, model_name: str = None, provider: str = "openrouter", provider_api_key: str = None) -> str:
    """Tóm tắt 1 chunk văn bản nhỏ (Stage: Map)."""
    if not chunk_text or not chunk_text.strip():
        return ""
    
    sys_prompt = CHUNK_MAP_PROMPT.format(chunk_index=chunk_index, total_chunks=total_chunks)
    user_content = f"Nội dung đoạn cuộc họp #{chunk_index}:\n\n---\n{chunk_text.strip()}\n---"
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": user_content}
    ]
    
    try:
        return call_llm_api(messages, provider=provider, model_name=model_name, provider_api_key=provider_api_key, temperature=0.3, max_tokens=2048)
    except Exception as e:
        print(f"⚠️ Lỗi tóm tắt chunk #{chunk_index}: {e}")
        return f"- [Đoạn {chunk_index}]: {chunk_text[:300]}..."

def aggregate_chunk_summaries(chunk_summaries: list[str], custom_prompt: str = None, model_name: str = None, provider: str = "openrouter", provider_api_key: str = None) -> str:
    """Hợp nhất các tóm tắt thành phần thành Meeting Notes hoàn chỉnh (Stage: Reduce)."""
    combined_summaries_text = "\n\n".join([f"=== TÓM TẮT ĐOẠN {i+1} ===\n{s}" for i, s in enumerate(chunk_summaries) if s])
    
    sys_prompt = custom_prompt.strip() if (custom_prompt and custom_prompt.strip()) else REDUCE_AGGREGATE_PROMPT
    user_content = f"Dưới đây là các bản tóm tắt thành phần từ từng đoạn của cuộc họp:\n\n---\n{combined_summaries_text}\n---\n\nHãy tổng hợp thành Biên bản Cuộc họp Meeting Notes chuẩn hóa."
    
    print(f"🧠 [Reduce Stage] Đang tổng hợp tóm tắt qua [{provider.upper()}]...")
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": user_content}
    ]
    return call_llm_api(messages, provider=provider, model_name=model_name, provider_api_key=provider_api_key, temperature=0.3, max_tokens=4096)

def summarize_chunks_map_reduce(chunk_transcripts: list[str], custom_prompt: str = None, model_name: str = None, provider: str = "openrouter", provider_api_key: str = None) -> str:
    """
    Quy trình Map-Reduce tóm tắt song song danh sách các đoạn transcript.
    - Map: Tóm tắt từng chunk song song qua ThreadPoolExecutor.
    - Reduce: Hợp nhất thành bản Meeting Notes cuối cùng.
    """
    total = len(chunk_transcripts)
    print(f"⚡ [Map Stage] Bắt đầu tóm tắt song song {total} chunks transcript qua [{provider.upper()}]...")
    
    chunk_summaries = [None] * total
    
    with ThreadPoolExecutor(max_workers=min(4, total)) as executor:
        future_to_index = {
            executor.submit(summarize_single_chunk, text, i + 1, total, model_name, provider, provider_api_key): i
            for i, text in enumerate(chunk_transcripts)
        }
        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            try:
                chunk_summaries[idx] = future.result()
                print(f"✅ Hoàn tất Map tóm tắt đoạn {idx + 1}/{total}")
            except Exception as exc:
                print(f"❌ Lỗi Map đoạn {idx + 1}: {exc}")
                chunk_summaries[idx] = f"- [Đoạn {idx + 1}]: N/A"

    return aggregate_chunk_summaries(chunk_summaries, custom_prompt, model_name, provider, provider_api_key)

def generate_summary(transcript_or_chunks, custom_prompt: str = None, model_name: str = None, provider: str = "openrouter", provider_api_key: str = None) -> str:
    """
    Hàm sinh Meeting Notes đa nhà cung cấp (Groq, OpenRouter, Gemini):
    """
    provider = (provider or "openrouter").lower().strip()

    # Xử lý input dạng list of chunks
    if isinstance(transcript_or_chunks, list):
        if not transcript_or_chunks:
            raise ValueError("Danh sách chunks transcript trống!")
        if len(transcript_or_chunks) == 1:
            return generate_summary(transcript_or_chunks[0], custom_prompt, model_name, provider, provider_api_key)
        return summarize_chunks_map_reduce(transcript_or_chunks, custom_prompt, model_name, provider, provider_api_key)

    transcript = str(transcript_or_chunks or "").strip()
    if not transcript:
        raise ValueError("Transcript trống, không thể thực hiện tóm tắt.")

    # Trường hợp 1: Transcript lớn > 12000 ký tự -> Tự động Chunking Text & Map-Reduce
    if len(transcript) > MAX_SINGLE_PASS_CHARS:
        print(f"📦 Transcript dài ({len(transcript)} ký tự > {MAX_SINGLE_PASS_CHARS}). Tự động kích hoạt Map-Reduce Chunk Summarization...")
        chunk_size = 8000
        paragraphs = transcript.split("\n\n")
        
        chunks = []
        current_chunk = []
        current_len = 0
        
        for p in paragraphs:
            if current_len + len(p) > chunk_size and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = [p]
                current_len = len(p)
            else:
                current_chunk.append(p)
                current_len += len(p)
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))
            
        return summarize_chunks_map_reduce(chunks, custom_prompt, model_name, provider, provider_api_key)

    # Trường hợp 2: Single-pass cho transcript vừa và nhỏ
    print(f"🧠 Đang gửi transcript ({len(transcript)} ký tự) tới [{provider.upper()}]...")

    sys_prompt = custom_prompt.strip() if (custom_prompt and custom_prompt.strip()) else SYSTEM_PROMPT
    user_content = f"Dưới đây là bản transcript thô của cuộc họp:\n\n---\n{transcript}\n---\n\nHãy tạo Meeting Notes Markdown chuẩn hóa theo đúng yêu cầu."
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": user_content}
    ]

    return call_llm_api(messages, provider=provider, model_name=model_name, provider_api_key=provider_api_key, temperature=0.3, max_tokens=4096)

if __name__ == "__main__":
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            content = f.read()
        summary = generate_summary(content)
        print("\n--- SUMMARY RESULT ---")
        print(summary)
    else:
        print("Sử dụng: python summarizer.py <duong_dan_file_raw_transcript.txt>")
