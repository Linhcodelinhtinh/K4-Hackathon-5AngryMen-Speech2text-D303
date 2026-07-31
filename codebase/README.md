# Kute AI Meeting Notes

## Features
- **Speech-to-Text**: Converts meeting audio to text using Groq Whisper.
- **AI Summarization**: Automatically generates structured Meeting Notes using Llama 3.
- **Large File Handling**: Automatically chunks files larger than 24MB into 10-minute segments and processes them in parallel to bypass API limits and speed up transcription.
- **Map-Reduce Summarization**: Long transcripts are split and summarized in chunks (Map phase), then combined into a final comprehensive summary (Reduce phase) to avoid context window limits.
- **Batch Processing**: Upload up to 5 audio files simultaneously with a total maximum size of 300MB.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure your Groq API Key:
   Create a `.env` file based on `.env.example` and add your `GROQ_API_KEY`.
3. Run the application:
   ```bash
   python server.py
   ```
   Or using uvicorn directly:
   ```bash
   uvicorn api.index:app --reload --port 8000
   ```

## Handling Large Files on Windows
To support chunking large audio files on Windows without requiring a manual FFmpeg installation, this project uses `static-ffmpeg`. It automatically downloads and provides the required FFmpeg binaries to `pydub` so audio manipulation works out-of-the-box.
