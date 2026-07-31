document.addEventListener('DOMContentLoaded', () => {
  const MAX_FILES = 5;
  const MAX_TOTAL_SIZE_MB = 300;

  // ── DOM refs ──────────────────────────────────────────────────────────────
  const dropZone            = document.getElementById('dropZone');
  const audioFileInput      = document.getElementById('audioFile');
  const dropContent         = document.getElementById('dropContent');
  const fileInfo            = document.getElementById('fileInfo');
  const totalSummaryText    = document.getElementById('totalSummaryText');
  const fileListContainer   = document.getElementById('fileListContainer');
  const removeAllFilesBtn   = document.getElementById('removeAllFilesBtn');

  const transcribeBtn       = document.getElementById('transcribeBtn');
  const summarizeBtn        = document.getElementById('summarizeBtn');
  const restoreSessionBtn   = document.getElementById('restoreSessionBtn');

  const transcriptSection   = document.getElementById('transcriptSection');
  const transcriptViewer    = document.getElementById('transcriptViewer');
  const transcriptSubTabs   = document.getElementById('transcriptSubTabs');
  const transcriptHighlightedView = document.getElementById('transcriptHighlightedView');
  const transcriptSearchInput = document.getElementById('transcriptSearchInput');
  const searchMatchCount    = document.getElementById('searchMatchCount');
  const copyTranscriptBtn   = document.getElementById('copyTranscriptBtn');

  const sttProgress         = document.getElementById('sttProgress');
  const sttProgressText     = document.getElementById('sttProgressText');
  const sttTimerEl          = document.getElementById('sttTimer');

  const llmProgress         = document.getElementById('llmProgress');
  const llmTimerEl          = document.getElementById('llmTimer');

  const errorBanner         = document.getElementById('errorBanner');
  const errorTitle          = document.getElementById('errorTitle');
  const errorDetail         = document.getElementById('errorDetail');

  const placeholderState    = document.getElementById('placeholderState');
  const summarizeLoading    = document.getElementById('summarizeLoading');
  const notesOutput         = document.getElementById('notesOutput');
  const outputActions       = document.getElementById('outputActions');
  const markdownViewer      = document.getElementById('markdownViewer');
  const elapsedTimer        = document.getElementById('elapsedTimer');

  const statTotalTime       = document.getElementById('statTotalTime');
  const statSTTTime         = document.getElementById('statSTTTime');
  const statLLMTime         = document.getElementById('statLLMTime');
  const statWordCount       = document.getElementById('statWordCount');

  const providerSelect      = document.getElementById('providerSelect');
  const modelSelect         = document.getElementById('modelSelect');
  const apiKeyInput         = document.getElementById('apiKey');
  const apiKeyLabel         = document.getElementById('apiKeyLabel');
  const customPromptInput   = document.getElementById('customPrompt');
  const presetChips         = document.querySelectorAll('.chip');

  const copyNotesBtn        = document.getElementById('copyNotesBtn');
  const copySlackBtn        = document.getElementById('copySlackBtn');
  const downloadNotesBtn    = document.getElementById('downloadNotesBtn');
  const downloadDocxBtn     = document.getElementById('downloadDocxBtn');
  const printPdfBtn         = document.getElementById('printPdfBtn');

  // ── State ─────────────────────────────────────────────────────────────────
  let selectedFiles        = [];
  let rawTranscriptText    = '';
  let meetingNotesMarkdown = '';
  let currentFilesDetail   = [];
  let sttTimeSaved         = 0;
  let timerInterval        = null;

  // ── LocalStorage backup ──────────────────────────────────────────────────
  checkBackupSessionUI();

  function checkBackupSessionUI() {
    if (!restoreSessionBtn) return;
    try {
      const saved = localStorage.getItem('kute_ai_backup_session');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed && (parsed.meeting_notes || parsed.raw_transcript)) {
          restoreSessionBtn.classList.remove('hidden');
        }
      }
    } catch (e) { console.warn('LocalStorage check failed:', e); }
  }

  restoreSessionBtn?.addEventListener('click', () => {
    try {
      const saved = localStorage.getItem('kute_ai_backup_session');
      if (!saved) return;
      const data = JSON.parse(saved);

      rawTranscriptText  = data.raw_transcript || '';
      currentFilesDetail = data.files_detail || [];

      transcriptViewer.value = rawTranscriptText;
      transcriptSection.classList.remove('hidden');
      renderSubTabsUI(currentFilesDetail);

      if (data.meeting_notes) {
        renderMeetingNotes(data.meeting_notes);
        setStats(data.stats || {});
      }
    } catch (e) {
      alert('❌ Lỗi khi khôi phục phiên làm việc!');
    }
  });

  // ── Preset Prompts ────────────────────────────────────────────────────────
  const PRESET_PROMPTS = {
    standard: `Bạn là Chuyên gia Thư ký Cuộc họp AI chuyên nghiệp.
Nhiệm vụ: Nhận transcript thô và tạo Meeting Notes bằng Markdown.
Yêu cầu:
1. SỬA LỖI CHÍNH TẢ & PHÁT ÂM: Tự động sửa lỗi tiếng Việt và từ phát âm sai từ Whisper.
2. THUẬT NGỮ TECH/AI: Giữ chuẩn các thuật ngữ AI & Công nghệ (Prompt, RAG, GPU, API, Fine-tuning, LLM, v.v.).
3. TRUNG THỰC: Chỉ dựa vào thông tin có trong transcript.
4. CẤU TRÚC:
- # Meeting Notes: [Tiêu đề]
- ## 1. Executive Summary
- ## 2. Key Takeaways
- ## 3. Action Items (Bảng 3 cột: Task | Assignee | Deadline)
- ## 4. Open Questions & Follow-ups`,

    action: `Bạn là Thư ký Cuộc họp tập trung vào Quản lý Dự án & Tiến độ.
Nhiệm vụ: Trích xuất CHI TIẾT VÀ TỈ MỈ TOÀN BỘ các Action Items, Task, Nhiệm vụ được giao trong cuộc họp.
Yêu cầu:
- Sửa lỗi chính tả và thuật ngữ AI/Tech.
- Lập bảng Action Items chi tiết gồm: Task | Người phụ trách | Hạn chót | Ghi chú/KPI.
- Liệt kê các cột mốc quan trọng (Milestones) và người chịu trách nhiệm trực tiếp.`,

    tech: `Bạn là Technical Leader tóm tắt cuộc họp Kỹ thuật / Kiến trúc Hệ thống.
Nhiệm vụ: Tóm tắt chuyên sâu về mặt Kỹ thuật, Công nghệ và Kiến trúc AI.
Yêu cầu:
- Giữ chính xác các khái niệm kỹ thuật: RAG, Vector DB, Fine-tuning, Embedding, Prompt Engineering, GPU, Benchmark, API.
- Tóm tắt rõ giải pháp kỹ thuật đã chọn, ưu/nhược điểm thảo luận và các đề xuất tối ưu.
- Liệt kê Action Items kỹ thuật theo từng Module.`,

    english: `You are an AI Executive Meeting Secretary.
Task: Summarize the meeting transcript into clear, professional Markdown Meeting Notes in English.
Structure required:
- # Meeting Notes: [Title]
- ## Executive Summary
- ## Key Decisions & Takeaways
- ## Action Items (Table: Task | Assignee | Deadline)
- ## Open Questions`
  };

  customPromptInput.value = PRESET_PROMPTS.standard;

  presetChips.forEach(chip => {
    chip.addEventListener('click', () => {
      presetChips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      const key = chip.dataset.preset;
      if (PRESET_PROMPTS[key]) customPromptInput.value = PRESET_PROMPTS[key];
    });
  });

  // ── Provider / Model dropdowns ────────────────────────────────────────────
  const PROVIDER_MODELS_UI = {
    groq: [
      { val: 'llama-3.3-70b-versatile', text: 'llama-3.3-70b-versatile ⭐' },
      { val: 'llama-3.1-8b-instant',    text: 'llama-3.1-8b-instant' },
      { val: 'gemma2-9b-it',            text: 'gemma2-9b-it' }
    ],
    openrouter: [
      { val: 'meta-llama/llama-3.3-70b-instruct', text: 'meta-llama/llama-3.3-70b-instruct' },
      { val: 'anthropic/claude-3.5-sonnet',        text: 'anthropic/claude-3.5-sonnet' },
      { val: 'deepseek/deepseek-r1',               text: 'deepseek/deepseek-r1' },
      { val: 'google/gemini-2.0-flash-001',        text: 'google/gemini-2.0-flash-001' }
    ],
    gemini: [
      { val: 'gemini-2.5-flash', text: 'gemini-2.5-flash ⭐' },
      { val: 'gemini-1.5-flash', text: 'gemini-1.5-flash' },
      { val: 'gemini-2.5-pro',   text: 'gemini-2.5-pro' },
      { val: 'gemini-1.5-pro',   text: 'gemini-1.5-pro' }
    ]
  };

  providerSelect?.addEventListener('change', () => {
    const provider = providerSelect.value;
    const models   = PROVIDER_MODELS_UI[provider] || PROVIDER_MODELS_UI.groq;
    modelSelect.innerHTML = '';
    models.forEach(m => {
      const opt = document.createElement('option');
      opt.value = m.val;
      opt.textContent = m.text;
      modelSelect.appendChild(opt);
    });
    const labels = { openrouter: ['OpenRouter API Key', 'sk-or-v1-...'], gemini: ['Gemini API Key', 'AIzaSy...'], groq: ['Groq API Key', 'gsk_...'] };
    const [label, placeholder] = labels[provider] || labels.groq;
    if (apiKeyLabel) apiKeyLabel.innerHTML = `${label} <span class="opt-tag">(tuỳ chọn nếu đã có trong .env)</span>`;
    if (apiKeyInput) apiKeyInput.placeholder = placeholder;
  });

  // ── Drag & Drop ──────────────────────────────────────────────────────────
  ['dragenter', 'dragover'].forEach(ev => {
    dropZone.addEventListener(ev, e => { e.preventDefault(); e.stopPropagation(); dropZone.classList.add('dragover'); }, false);
  });
  ['dragleave', 'drop'].forEach(ev => {
    dropZone.addEventListener(ev, e => { e.preventDefault(); e.stopPropagation(); dropZone.classList.remove('dragover'); }, false);
  });
  dropZone.addEventListener('drop', e => { const files = Array.from(e.dataTransfer.files); if (files.length) addFiles(files); });
  audioFileInput.addEventListener('change', e => { const files = Array.from(e.target.files); if (files.length) addFiles(files); });
  removeAllFilesBtn.addEventListener('click', e => { e.stopPropagation(); resetFileSelection(); });

  function addFiles(newFiles) {
    const valid = newFiles.filter(f => f.type.startsWith('audio/') || /\.(mp3|m4a|wav|ogg|flac|aac)$/i.test(f.name));
    if (!valid.length) { showError('Không tìm thấy file âm thanh hợp lệ!'); return; }

    const existingNames = new Set(selectedFiles.map(f => f.name));
    const combined = [...selectedFiles];
    for (const f of valid) { if (!existingNames.has(f.name)) { combined.push(f); existingNames.add(f.name); } }

    if (combined.length > MAX_FILES) { showError(`Chỉ được tải lên tối đa ${MAX_FILES} file cùng lúc!`); return; }
    const totalMB = combined.reduce((s, f) => s + f.size, 0) / (1024 * 1024);
    if (totalMB > MAX_TOTAL_SIZE_MB) { showError(`Tổng dung lượng (${totalMB.toFixed(2)}MB) vượt giới hạn ${MAX_TOTAL_SIZE_MB}MB!`); return; }

    selectedFiles = combined;
    renderFileListUI();
  }

  function removeFileIndex(i) {
    selectedFiles.splice(i, 1);
    if (!selectedFiles.length) resetFileSelection(); else renderFileListUI();
  }

  function renderFileListUI() {
    hideError();
    dropContent.classList.add('hidden');
    fileInfo.classList.remove('hidden');
    const totalMB = selectedFiles.reduce((s, f) => s + f.size, 0) / (1024 * 1024);
    totalSummaryText.textContent = `${selectedFiles.length}/${MAX_FILES} file · ${totalMB.toFixed(2)} MB / ${MAX_TOTAL_SIZE_MB} MB`;
    fileListContainer.innerHTML = '';
    selectedFiles.forEach((file, i) => {
      const div = document.createElement('div');
      div.className = 'file-item';
      div.innerHTML = `<span class="file-item-name">🎵 ${file.name}</span>
                       <span class="file-item-size">${(file.size / (1024 * 1024)).toFixed(2)} MB</span>
                       <button type="button" class="file-item-remove" data-index="${i}">✕</button>`;
      fileListContainer.appendChild(div);
    });
    fileListContainer.querySelectorAll('.file-item-remove').forEach(btn => {
      btn.addEventListener('click', e => { e.stopPropagation(); removeFileIndex(parseInt(btn.dataset.index)); });
    });
    transcribeBtn.disabled = false;
  }

  function resetFileSelection() {
    selectedFiles = [];
    audioFileInput.value = '';
    dropContent.classList.remove('hidden');
    fileInfo.classList.add('hidden');
    transcribeBtn.disabled = true;
  }

  // ── STEP 1: Transcribe Only ───────────────────────────────────────────────
  transcribeBtn.addEventListener('click', async () => {
    if (!selectedFiles.length) return;
    hideError();
    startTimer(sttTimerEl);
    sttProgress.classList.remove('hidden');
    transcribeBtn.disabled = true;
    sttProgressText.textContent = 'Đang tải file lên server...';

    const formData = new FormData();
    selectedFiles.forEach(f => formData.append('audio_files', f));
    formData.append('provider', providerSelect?.value || 'groq');
    if (apiKeyInput?.value.trim()) {
      formData.append('provider_api_key', apiKeyInput.value.trim());
      formData.append('groq_api_key', apiKeyInput.value.trim());
    }

    setTimeout(() => { sttProgressText.textContent = 'Nhận diện giọng nói (Whisper Parallel Chunking)...'; }, 600);

    try {
      const res  = await fetch('/api/transcribe', { method: 'POST', body: formData });
      stopTimer();
      sttProgress.classList.add('hidden');

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: `Lỗi HTTP ${res.status}` }));
        throw { status: res.status, detail: err.detail };
      }

      const data = await res.json();
      rawTranscriptText  = data.raw_transcript || '';
      currentFilesDetail = data.files_detail   || [];
      sttTimeSaved       = data.stt_time        || 0;

      // Hiển thị transcript section
      transcriptViewer.value = rawTranscriptText;
      transcriptSection.classList.remove('hidden');
      renderSubTabsUI(currentFilesDetail);

      if (statSTTTime) statSTTTime.textContent = `🎙 STT: ${sttTimeSaved.toFixed(1)}s`;
      if (statWordCount) statWordCount.textContent = `📝 ${rawTranscriptText.trim().split(/\s+/).length} từ`;

      // Scroll to transcript
      transcriptSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
      transcribeBtn.disabled = false;

    } catch (err) {
      stopTimer();
      sttProgress.classList.add('hidden');
      transcribeBtn.disabled = false;
      showError(err.detail || err.message || String(err));
    }
  });

  // ── STEP 3: Summarize All ─────────────────────────────────────────────────
  summarizeBtn?.addEventListener('click', async () => {
    const transcript = transcriptViewer.value?.trim();
    if (!transcript) {
      showError('Chưa có transcript để tóm tắt! Hãy nhận diện giọng nói trước.');
      return;
    }
    hideError();

    // Show right panel loading
    placeholderState.classList.add('hidden');
    notesOutput.classList.add('hidden');
    outputActions.classList.add('hidden');
    summarizeLoading.classList.remove('hidden');
    summarizeBtn.disabled = true;

    startTimer(elapsedTimer, 'Thời gian xử lý: ');

    const payload = {
      raw_transcript:  transcript,
      custom_prompt:   customPromptInput?.value.trim() || '',
      provider:        providerSelect?.value || 'groq',
      model_name:      modelSelect?.value || '',
      provider_api_key: apiKeyInput?.value.trim() || '',
      groq_api_key:    apiKeyInput?.value.trim() || ''
    };

    try {
      const res = await fetch('/api/summarize', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(payload)
      });

      stopTimer();
      summarizeLoading.classList.add('hidden');
      summarizeBtn.disabled = false;

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: `Lỗi HTTP ${res.status}` }));
        throw { status: res.status, detail: err.detail };
      }

      const data = await res.json();
      renderMeetingNotes(data.meeting_notes || '');
      setStats({ total_time: data.total_time, stt_time: sttTimeSaved, llm_time: data.llm_time });

      // Auto-save to LocalStorage
      try {
        localStorage.setItem('kute_ai_backup_session', JSON.stringify({
          meeting_notes:  data.meeting_notes,
          raw_transcript: transcript,
          files_detail:   currentFilesDetail,
          stats:          { total_time: data.total_time || 0, stt_time: sttTimeSaved, llm_time: data.llm_time || 0 },
          timestamp:      Date.now()
        }));
        restoreSessionBtn?.classList.remove('hidden');
      } catch (e) { console.warn('LocalStorage save failed:', e); }

    } catch (err) {
      stopTimer();
      summarizeLoading.classList.add('hidden');
      summarizeBtn.disabled = false;
      placeholderState.classList.remove('hidden');
      showError(err.detail || err.message || String(err));
    }
  });

  // ── Render Meeting Notes on right panel ──────────────────────────────────
  function renderMeetingNotes(md) {
    meetingNotesMarkdown = md;
    markdownViewer.innerHTML = marked.parse(md);
    notesOutput.classList.remove('hidden');
    outputActions.classList.remove('hidden');
    placeholderState.classList.add('hidden');
    // Smooth scroll right panel into view on mobile
    notesOutput.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function setStats(stats) {
    if (!stats) return;
    const total = stats.total_time || (stats.stt_time || 0) + (stats.llm_time || 0);
    if (statTotalTime) statTotalTime.textContent = `⏱ ${total.toFixed(1)}s`;
    if (statSTTTime)   statSTTTime.textContent   = `🎙 STT: ${(stats.stt_time || sttTimeSaved || 0).toFixed(1)}s`;
    if (statLLMTime)   statLLMTime.textContent   = `🧠 LLM: ${(stats.llm_time || 0).toFixed(1)}s`;
  }

  // ── Multi-file Sub-Tabs ──────────────────────────────────────────────────
  function renderSubTabsUI(filesDetail) {
    if (!transcriptSubTabs) return;
    if (!filesDetail || filesDetail.length <= 1) {
      transcriptSubTabs.classList.add('hidden');
      transcriptSubTabs.innerHTML = '';
      return;
    }

    transcriptSubTabs.classList.remove('hidden');
    transcriptSubTabs.innerHTML = '';

    // "All" tab
    const allBtn = document.createElement('button');
    allBtn.className = 'sub-tab-pill active';
    allBtn.textContent = `🌐 Tất cả (${filesDetail.length} file)`;
    allBtn.addEventListener('click', () => {
      transcriptSubTabs.querySelectorAll('.sub-tab-pill').forEach(b => b.classList.remove('active'));
      allBtn.classList.add('active');
      transcriptViewer.value = rawTranscriptText;
    });
    transcriptSubTabs.appendChild(allBtn);

    // Individual file tabs
    filesDetail.forEach(fileItem => {
      const pill = document.createElement('button');
      pill.className = 'sub-tab-pill';
      pill.textContent = `🎵 ${fileItem.filename}`;
      pill.addEventListener('click', () => {
        transcriptSubTabs.querySelectorAll('.sub-tab-pill').forEach(b => b.classList.remove('active'));
        pill.classList.add('active');
        transcriptViewer.value = fileItem.transcript;
      });
      transcriptSubTabs.appendChild(pill);
    });
  }

  // ── Transcript Search & Highlight ────────────────────────────────────────
  transcriptSearchInput?.addEventListener('input', () => {
    const query = transcriptSearchInput.value.trim();
    const text  = transcriptViewer.value || '';

    if (!query) {
      transcriptHighlightedView.classList.add('hidden');
      transcriptViewer.classList.remove('hidden');
      if (searchMatchCount) searchMatchCount.classList.add('hidden');
      return;
    }

    const escaped      = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex        = new RegExp(`(${escapedQuery})`, 'gi');
    const matches      = (text.match(regex) || []).length;

    if (searchMatchCount) {
      searchMatchCount.textContent = `${matches} kết quả`;
      searchMatchCount.classList.toggle('hidden', matches === 0);
    }

    transcriptHighlightedView.innerHTML = escaped.replace(regex, '<mark>$1</mark>');
    transcriptViewer.classList.add('hidden');
    transcriptHighlightedView.classList.remove('hidden');
  });

  // ── Copy Transcript ──────────────────────────────────────────────────────
  copyTranscriptBtn?.addEventListener('click', () => {
    const text = transcriptViewer.value || '';
    if (!text) return;
    navigator.clipboard.writeText(text).then(() => {
      const orig = copyTranscriptBtn.textContent;
      copyTranscriptBtn.textContent = '✅ Đã copy!';
      setTimeout(() => copyTranscriptBtn.textContent = orig, 2000);
    });
  });

  // ── Export Buttons ───────────────────────────────────────────────────────
  copyNotesBtn?.addEventListener('click', () => {
    if (!meetingNotesMarkdown) return;
    navigator.clipboard.writeText(meetingNotesMarkdown).then(() => {
      const orig = copyNotesBtn.textContent;
      copyNotesBtn.textContent = '✅ Đã copy!';
      setTimeout(() => copyNotesBtn.textContent = orig, 2000);
    });
  });

  copySlackBtn?.addEventListener('click', () => {
    if (!meetingNotesMarkdown) return;
    const slackFmt = meetingNotesMarkdown
      .replace(/^# (.*$)/gim,   '*$1*')
      .replace(/^## (.*$)/gim,  '\n*$1*')
      .replace(/^### (.*$)/gim, '\n*$1*');
    navigator.clipboard.writeText(slackFmt).then(() => {
      const orig = copySlackBtn.textContent;
      copySlackBtn.textContent = '✅ Đã copy Slack!';
      setTimeout(() => copySlackBtn.textContent = orig, 2000);
    });
  });

  downloadNotesBtn?.addEventListener('click', () => {
    if (!meetingNotesMarkdown) return;
    const blob = new Blob([meetingNotesMarkdown], { type: 'text/markdown;charset=utf-8' });
    downloadBlob(blob, `Meeting_Notes_${Date.now()}.md`);
  });

  downloadDocxBtn?.addEventListener('click', () => {
    if (!meetingNotesMarkdown) return;
    const html = `<html xmlns:o='urn:schemas-microsoft-microsoft-com:office:office'
                        xmlns:w='urn:schemas-microsoft-microsoft-com:office:word'
                        xmlns='http://www.w3.org/TR/REC-html40'>
      <head><meta charset='utf-8'><title>Meeting Notes</title>
      <style>body{font-family:'Calibri','Arial',sans-serif;line-height:1.6;color:#111}
      h1{color:#1E3A8A;border-bottom:2px solid #1E3A8A;padding-bottom:5px}
      h2{color:#2563EB;margin-top:20px;border-bottom:1px solid #DDD;padding-bottom:3px}
      table{border-collapse:collapse;width:100%;margin:15px 0}
      th,td{border:1px solid #CBD5E1;padding:8px 12px;text-align:left}
      th{background:#F1F5F9;color:#1E293B}ul,ol{padding-left:20px}</style></head>
      <body>${marked.parse(meetingNotesMarkdown)}</body></html>`;
    const blob = new Blob(['\ufeff', html], { type: 'application/msword' });
    downloadBlob(blob, `Meeting_Notes_${Date.now()}.doc`);
  });

  printPdfBtn?.addEventListener('click', () => { if (meetingNotesMarkdown) window.print(); });

  function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a   = Object.assign(document.createElement('a'), { href: url, download: filename });
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  // ── Timer helpers ─────────────────────────────────────────────────────────
  function startTimer(el, prefix = '') {
    clearInterval(timerInterval);
    let s = 0;
    if (el) el.textContent = `${prefix}0s`;
    timerInterval = setInterval(() => {
      s++;
      if (el) el.textContent = `${prefix}${s}s`;
    }, 1000);
  }

  function stopTimer() {
    clearInterval(timerInterval);
    timerInterval = null;
  }

  // ── Error UI ──────────────────────────────────────────────────────────────
  function showError(msg) {
    if (!errorBanner) { alert(`❌ ${msg}`); return; }
    errorTitle.textContent  = msg;
    errorDetail.textContent = 'Kiểm tra lại API Key, giới hạn file (≤5 file, ≤300MB), hoặc kết nối mạng.';
    errorBanner.classList.remove('hidden');
  }

  function hideError() {
    errorBanner?.classList.add('hidden');
  }
});
