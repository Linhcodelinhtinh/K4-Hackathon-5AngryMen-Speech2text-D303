# Architecture

## Repo layout

This repo is a hackathon submission (Mini Hackathon AI — Batch 03). The root
holds only hackathon rules/spec docs (`README.md`); the actual product lives
entirely under [`kute-ai-meeting/`](kute-ai-meeting/).

```
.
├── README.md                  # hackathon rules, checkpoints, grading rubric (not app docs)
└── kute-ai-meeting/           # the product: "Kute AI Meeting Notes"
    ├── main.py                 # CLI entrypoint: MP3 -> transcript -> notes, run locally
    ├── server.py                # local dev server entrypoint (uvicorn wrapper around api/index.py)
    ├── api/
    │   └── index.py              # FastAPI app: all HTTP routes + static file serving (also the Vercel handler)
    ├── stt_service.py           # Speech-to-Text: Groq Whisper, with chunking for large files
    ├── summarizer.py            # LLM summarization: multi-provider, Map-Reduce for long transcripts
    ├── public/                  # static frontend (vanilla HTML/CSS/JS, no build step)
    │   ├── index.html
    │   ├── app.js
    │   └── style.css
    ├── test_pipeline.py         # unittest smoke tests for the summarizer/prompt
    ├── requirements.txt
    ├── vercel.json               # serverless deployment config (Vercel)
    └── .env.example              # GROQ_API_KEY
```

## What it does

Kute AI Meeting Notes turns a recorded meeting (MP3/audio) into structured
Markdown meeting notes:

```
audio file(s) → [STT: Groq Whisper] → raw transcript → [LLM summarize] → meeting_notes.md
```

It's usable two ways:
1. **CLI** (`main.py`) — single file, local, writes `raw_transcript.txt` and
   `meeting_notes.md` next to the input.
2. **Web app** (`api/index.py` + `public/`) — FastAPI backend + vanilla JS
   frontend, supports up to 5 files / 300MB per batch, drag-and-drop upload,
   provider/model selection, custom prompts, transcript search, session
   restore via `localStorage`, and export (copy/download/print).

Both paths share the same two core modules: `stt_service.py` and
`summarizer.py`.

## Backend (FastAPI — `api/index.py`)

Three endpoints, all under `/api`:

- `POST /api/transcribe` — audio files → raw transcript only (STT step).
- `POST /api/summarize` — raw transcript text (JSON body) → meeting notes
  (LLM step only, used for "re-summarize with different prompt/provider"
  without re-running STT).
- `POST /api/process` — full pipeline: audio files → transcript → notes in
  one call.

Cross-cutting concerns handled in `api/index.py`:
- `validate_audio_files` enforces the 5-file / 300MB caps before any
  processing starts.
- `validate_llm_api_key` / `get_provider_api_key` resolve an API key from
  either the request (`provider_api_key`/`groq_api_key` form/JSON fields) or
  environment variables, per selected provider.
- `parse_and_raise_error` maps internal exceptions (missing key, provider
  401/429, pydub/ffmpeg failures, missing file) to appropriate HTTP status
  codes with Vietnamese user-facing messages.
- The same FastAPI app also mounts `public/` as static files and serves
  `index.html` as the SPA fallback for any unmatched route — so one process
  serves both API and frontend, in dev (`server.py`/`uvicorn`) and in
  production (Vercel, via `vercel.json` routing everything else to
  `public/index.html`).

## Speech-to-Text (`stt_service.py`)

Uses Groq's Whisper Large V3 API exclusively (STT is not multi-provider).

- Files ≤ 24MB: sent directly to the Groq transcription API.
- Files > 24MB (Groq's request size limit): split into 10-minute chunks with
  `pydub`/`ffmpeg` (via `static-ffmpeg`, so no manual ffmpeg install is
  needed, including on Windows), transcribed in parallel with a
  `ThreadPoolExecutor` (max 3 workers), then chunks are stitched back into
  a single transcript in original order.
- `transcribe_audio_with_chunks()` returns both the joined `full_transcript`
  and the individual `chunk_transcripts` — the latter is what
  `api/index.py` reuses as pre-split input to the summarizer's Map-Reduce
  path, avoiding a second, different chunking pass over the text.

## Summarization (`summarizer.py`)

Multi-provider LLM layer supporting **Groq**, **OpenRouter**, and **Gemini**,
selected per-request. Each provider has a default model and an ordered list
of fallback models (`PROVIDER_MODELS`); `call_llm_api()` tries the requested
model first, then falls back through the list on failure — one place handles
provider dispatch (Groq SDK / OpenAI-compatible client for OpenRouter /
`google-genai` for Gemini) and retry logic.

Two summarization strategies, chosen automatically by input size:
- **Single-pass**: transcript ≤ 12,000 chars → one LLM call with
  `SYSTEM_PROMPT`, producing the full structured Meeting Notes Markdown
  directly.
- **Map-Reduce**: transcript > 12,000 chars, or input already arrives as
  multiple chunks (multi-file uploads, or chunked STT output) →
  1. **Map**: each chunk summarized independently and in parallel
     (`ThreadPoolExecutor`, up to 4 workers) via `CHUNK_MAP_PROMPT`.
  2. **Reduce**: all chunk summaries are concatenated and sent through
     `REDUCE_AGGREGATE_PROMPT` (or a user-supplied custom prompt) to produce
     one coherent Meeting Notes document.

The prompts are written to specifically correct Whisper mishearing of
AI/tech jargon in Vietnamese speech (e.g. "rác" → "RAG", "làm ma" → "Llama")
and to preserve per-file attribution (`=== FILE n/N: name ===` headers) all
the way through Map and Reduce so multi-file batches don't collapse into a
summary of only the last file.

## Frontend (`public/`)

Static, framework-free HTML/CSS/JS (no build step, no bundler).
`app.js` (~770 lines) drives a single-page workflow:
- Drag-and-drop / multi-file picker with client-side count/size validation
  mirroring the backend's 5-file/300MB limits.
- Prompt presets (chips) plus a free-text custom prompt box.
- Provider/API key + model selection passed straight through to the backend.
- Calls `/api/process` (full pipeline) or `/api/transcribe` +
  `/api/summarize` separately (e.g. "re-summarize" reuses the already-fetched
  transcript instead of re-running STT).
- Renders results as tabs (Notes / Transcript, with per-file sub-tabs),
  supports in-transcript keyword search with highlighting, and export via
  copy/Markdown download/Slack-formatted copy/print-to-PDF.
- Persists the last successful session to `localStorage` so a page reload
  can restore results without re-calling the API.

## Deployment

- **Local**: `python server.py` (or `uvicorn api.index:app --reload`) runs
  the whole app — API + static frontend — on one port.
- **Serverless (Vercel)**: `vercel.json` builds `api/index.py` as a Python
  serverless function (`@vercel/python`) and serves `public/**` as static
  assets; all `/api/*` routes go to the function, everything else falls
  through to `public/index.html`.

## Notable design choices

- **No database, no auth, no persistence layer** — this is a stateless
  request/response pipeline; the only "storage" is `localStorage` on the
  client for session restore, and local files (`raw_transcript.txt`,
  `meeting_notes.md`) when run via the CLI.
- **STT and LLM providers are decoupled**: STT is Groq-only, but
  summarization can use any of Groq/OpenRouter/Gemini independently — so a
  Groq key is always required (for Whisper) even if notes are generated via
  Gemini or OpenRouter.
- **Chunking logic is deliberately kept in two places for two different
  units**: `stt_service.py` chunks *audio* (by duration, for API size
  limits), `summarizer.py` chunks *text* (by character count, for LLM
  context limits) — they're independent concerns that happen to compose
  (audio chunks often become the text chunks fed to Map-Reduce directly).
