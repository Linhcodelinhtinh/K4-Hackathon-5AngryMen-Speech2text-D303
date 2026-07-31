document.addEventListener('DOMContentLoaded', () => {
  const MAX_FILES = 5;
  const MAX_TOTAL_SIZE_MB = 300;

  // Elements
  const dropZone = document.getElementById('dropZone');
  const audioFileInput = document.getElementById('audioFile');
  const dropContent = document.getElementById('dropContent');
  const fileInfo = document.getElementById('fileInfo');
  const totalSummaryText = document.getElementById('totalSummaryText');
  const fileListContainer = document.getElementById('fileListContainer');
  const removeAllFilesBtn = document.getElementById('removeAllFilesBtn');
  
  const processBtn = document.getElementById('processBtn');
  const transcribeOnlyBtn = document.getElementById('transcribeOnlyBtn');
  const reSummarizeBtn = document.getElementById('reSummarizeBtn');

  const customPromptInput = document.getElementById('customPrompt');
  const apiKeyInput = document.getElementById('apiKey');
  const presetChips = document.querySelectorAll('.chip');

  const placeholderState = document.getElementById('placeholderState');
  const statusContainer = document.getElementById('statusContainer');
  const resultsContent = document.getElementById('resultsContent');
  const outputActions = document.getElementById('outputActions');
  const elapsedTimer = document.getElementById('elapsedTimer');
  const errorBanner = document.getElementById('errorBanner');
  const errorTitle = document.getElementById('errorTitle');
  const errorDetail = document.getElementById('errorDetail');
  
  const step1 = document.getElementById('step1');
  const step2 = document.getElementById('step2');
  const step3 = document.getElementById('step3');

  const markdownViewer = document.getElementById('markdownViewer');
  const transcriptViewer = document.getElementById('transcriptViewer');
  const copyNotesBtn = document.getElementById('copyNotesBtn');
  const downloadNotesBtn = document.getElementById('downloadNotesBtn');

  const statTotalTime = document.getElementById('statTotalTime');
  const statSTTTime = document.getElementById('statSTTTime');
  const statLLMTime = document.getElementById('statLLMTime');
  const statWordCount = document.getElementById('statWordCount');

  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabPanes = document.querySelectorAll('.tab-pane');

  const transcriptSubTabs = document.getElementById('transcriptSubTabs');
  const copySubTranscriptBtn = document.getElementById('copySubTranscriptBtn');
  const restoreSessionBtn = document.getElementById('restoreSessionBtn');

  const copySlackBtn = document.getElementById('copySlackBtn');
  const downloadDocxBtn = document.getElementById('downloadDocxBtn');
  const printPdfBtn = document.getElementById('printPdfBtn');

  const transcriptSearchInput = document.getElementById('transcriptSearchInput');
  const searchMatchCount = document.getElementById('searchMatchCount');
  const transcriptHighlightedView = document.getElementById('transcriptHighlightedView');

  let selectedFiles = []; // Mảng chứa danh sách các File đối tượng
  let timerInterval = null;
  let meetingNotesMarkdown = '';
  let rawTranscriptText = '';
  let currentFilesDetail = [];

  // Check LocalStorage Backup on init
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
    } catch (e) {
      console.warn("LocalStorage check failed:", e);
    }
  }

  if (restoreSessionBtn) {
    restoreSessionBtn.addEventListener('click', () => {
      try {
        const saved = localStorage.getItem('kute_ai_backup_session');
        if (!saved) return;
        const data = JSON.parse(saved);
        
        placeholderState.classList.add('hidden');
        if (errorBanner) errorBanner.classList.add('hidden');
        resultsContent.classList.remove('hidden');
        outputActions.classList.remove('hidden');

        saveAndRenderData(data);
        if (reSummarizeBtn) reSummarizeBtn.disabled = false;
        switchToTab('notes');
      } catch (e) {
        alert("❌ Lỗi khi khôi phục dữ liệu gần nhất!");
      }
    });
  }

  // Prompt Preset Templates
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

  // Set default prompt
  customPromptInput.value = PRESET_PROMPTS.standard;

  // Preset Chips click event
  presetChips.forEach(chip => {
    chip.addEventListener('click', () => {
      presetChips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      const presetKey = chip.dataset.preset;
      if (PRESET_PROMPTS[presetKey]) {
        customPromptInput.value = PRESET_PROMPTS[presetKey];
      }
    });
  });

  // Drag & Drop handlers
  ['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.add('dragover');
    }, false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.remove('dragover');
    }, false);
  });

  dropZone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = Array.from(dt.files);
    if (files.length > 0) {
      addFiles(files);
    }
  });

  audioFileInput.addEventListener('change', (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      addFiles(files);
    }
  });

  removeAllFilesBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    resetFileSelection();
  });

  function addFiles(newFiles) {
    const validAudioFiles = newFiles.filter(f => f.type.startsWith('audio/') || /\.(mp3|m4a|wav|ogg|flac|aac)$/i.test(f.name));
    
    if (validAudioFiles.length === 0) {
      handleErrorUI({ status: 400, detail: "Lỗi 400: 'Không tìm thấy file âm thanh hợp lệ!'" });
      return;
    }

    // Kết hợp và lọc trùng tên file
    const existingNames = new Set(selectedFiles.map(f => f.name));
    const combined = [...selectedFiles];
    
    for (const f of validAudioFiles) {
      if (!existingNames.has(f.name)) {
        combined.push(f);
        existingNames.add(f.name);
      }
    }

    // Kiểm tra giới hạn 5 file
    if (combined.length > MAX_FILES) {
      handleErrorUI({ 
        status: 400, 
        detail: `Lỗi 400: 'Chỉ được tải lên tối đa ${MAX_FILES} file cùng lúc (Đã chọn ${combined.length} file)!'` 
      });
      return;
    }

    // Kiểm tra tổng dung lượng 300MB
    const totalBytes = combined.reduce((sum, f) => sum + f.size, 0);
    const totalMB = totalBytes / (1024 * 1024);

    if (totalMB > MAX_TOTAL_SIZE_MB) {
      handleErrorUI({ 
        status: 400, 
        detail: `Lỗi 400: 'Tổng dung lượng các file (${totalMB.toFixed(2)}MB) vượt quá giới hạn ${MAX_TOTAL_SIZE_MB}MB!'` 
      });
      return;
    }

    selectedFiles = combined;
    renderFileListUI();
  }

  function removeFileIndex(index) {
    selectedFiles.splice(index, 1);
    if (selectedFiles.length === 0) {
      resetFileSelection();
    } else {
      renderFileListUI();
    }
  }

  function renderFileListUI() {
    if (errorBanner) errorBanner.classList.add('hidden');
    dropContent.classList.add('hidden');
    fileInfo.classList.remove('hidden');
    
    const totalBytes = selectedFiles.reduce((sum, f) => sum + f.size, 0);
    const totalMB = totalBytes / (1024 * 1024);

    totalSummaryText.textContent = `${selectedFiles.length}/${MAX_FILES} file (Tổng: ${totalMB.toFixed(2)} MB / ${MAX_TOTAL_SIZE_MB} MB)`;
    
    fileListContainer.innerHTML = '';
    selectedFiles.forEach((file, index) => {
      const itemDiv = document.createElement('div');
      itemDiv.className = 'file-item';
      itemDiv.innerHTML = `
        <span class="file-item-name">🎵 ${file.name}</span>
        <span class="file-item-size">${(file.size / (1024 * 1024)).toFixed(2)} MB</span>
        <button type="button" class="file-item-remove" data-index="${index}">✕</button>
      `;
      fileListContainer.appendChild(itemDiv);
    });

    // Thêm event remove từng file
    fileListContainer.querySelectorAll('.file-item-remove').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const idx = parseInt(btn.dataset.index);
        removeFileIndex(idx);
      });
    });

    processBtn.disabled = false;
    if (transcribeOnlyBtn) transcribeOnlyBtn.disabled = false;
  }

  function resetFileSelection() {
    selectedFiles = [];
    audioFileInput.value = '';
    dropContent.classList.remove('hidden');
    fileInfo.classList.add('hidden');
    processBtn.disabled = true;
    if (transcribeOnlyBtn) transcribeOnlyBtn.disabled = true;
  }

  // Tabs Navigation
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      tabPanes.forEach(p => p.classList.remove('active'));
      
      btn.classList.add('active');
      const targetPane = document.getElementById(btn.dataset.tab);
      if (targetPane) targetPane.classList.add('active');
    });
  });

  function switchToTab(tabName) {
    const targetTabBtn = document.querySelector(`.tab-btn[data-tab="${tabName}Tab"]`);
    if (targetTabBtn) targetTabBtn.click();
  }

  // 1. Full Pipeline Button (Process all audio files)
  processBtn.addEventListener('click', async () => {
    if (selectedFiles.length === 0) return;
    startProcessingUI('all');

    const formData = new FormData();
    selectedFiles.forEach(file => {
      formData.append('audio_files', file);
    });
    formData.append('custom_prompt', customPromptInput.value.trim());
    if (apiKeyInput.value.trim()) formData.append('groq_api_key', apiKeyInput.value.trim());

    try {
      setTimeout(() => { step1.className = 'step done'; step2.className = 'step active'; }, 800);

      const response = await fetch('/api/process', { method: 'POST', body: formData });
      step2.className = 'step done'; step3.className = 'step active';

      if (!response.ok) {
        const errData = await response.json().catch(()=>({ detail: `Lỗi HTTP ${response.status}` }));
        throw { status: response.status, detail: errData.detail || `Lỗi ${response.status}: Server Error` };
      }

      const data = await response.json();
      step3.className = 'step done';

      saveAndRenderData(data);
      finishProcessingUI();
      if (reSummarizeBtn) reSummarizeBtn.disabled = false;
      switchToTab('notes');

    } catch (err) {
      handleErrorUI(err);
    }
  });

  // 2. Transcribe Only Button (STT for all audio files)
  if (transcribeOnlyBtn) {
    transcribeOnlyBtn.addEventListener('click', async () => {
      if (selectedFiles.length === 0) return;
      startProcessingUI('stt_only');

      const formData = new FormData();
      selectedFiles.forEach(file => {
        formData.append('audio_files', file);
      });
      if (apiKeyInput.value.trim()) formData.append('groq_api_key', apiKeyInput.value.trim());

      try {
        setTimeout(() => { step1.className = 'step done'; step2.className = 'step active'; }, 800);

        const response = await fetch('/api/transcribe', { method: 'POST', body: formData });
        step2.className = 'step done';

        if (!response.ok) {
          const errData = await response.json().catch(()=>({ detail: `Lỗi HTTP ${response.status}` }));
          throw { status: response.status, detail: errData.detail || `Lỗi ${response.status}: Server Error` };
        }

        const data = await response.json();

        rawTranscriptText = data.raw_transcript;
        transcriptViewer.value = rawTranscriptText;
        currentFilesDetail = data.files_detail || [];

        renderSubTabsUI(currentFilesDetail);
        
        statSTTTime.textContent = `${data.stt_time.toFixed(1)}s`;
        statWordCount.textContent = rawTranscriptText.trim().split(/\s+/).length;

        finishProcessingUI();
        if (reSummarizeBtn) reSummarizeBtn.disabled = false;
        switchToTab('transcript'); 

      } catch (err) {
        handleErrorUI(err);
      }
    });
  }

  // 3. Re-Summarize Button (LLM only from transcriptViewer text)
  if (reSummarizeBtn) {
    reSummarizeBtn.addEventListener('click', async () => {
      const currentTranscript = transcriptViewer.value ? transcriptViewer.value.trim() : transcriptViewer.textContent.trim();
      if (!currentTranscript) {
        handleErrorUI({ status: 400, detail: "Lỗi 400: 'Không có văn bản Transcript để tóm tắt!'" });
        return;
      }

      startProcessingUI('llm_only');

      const payload = {
        raw_transcript: currentTranscript,
        custom_prompt: customPromptInput.value.trim(),
        groq_api_key: apiKeyInput.value.trim()
      };

      try {
        const response = await fetch('/api/summarize', { 
          method: 'POST', 
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload) 
        });

        if (!response.ok) {
          const errData = await response.json().catch(()=>({ detail: `Lỗi HTTP ${response.status}` }));
          throw { status: response.status, detail: errData.detail || `Lỗi ${response.status}: Server Error` };
        }

        const data = await response.json();
        step3.className = 'step done';

        meetingNotesMarkdown = data.meeting_notes;
        markdownViewer.innerHTML = marked.parse(meetingNotesMarkdown);
        statLLMTime.textContent = `${data.llm_time.toFixed(1)}s`;

        finishProcessingUI();
        switchToTab('notes'); 

      } catch (err) {
        handleErrorUI(err);
      }
    });
  }

  if (transcriptViewer) {
    transcriptViewer.addEventListener('input', () => {
      if (reSummarizeBtn) {
        reSummarizeBtn.disabled = !transcriptViewer.value.trim();
      }
    });
  }

  function startProcessingUI(mode) {
    if (errorBanner) errorBanner.classList.add('hidden');
    placeholderState.classList.add('hidden');
    resultsContent.classList.add('hidden');
    outputActions.classList.add('hidden');
    statusContainer.classList.remove('hidden');
    
    processBtn.disabled = true;
    if (transcribeOnlyBtn) transcribeOnlyBtn.disabled = true;
    if (reSummarizeBtn) reSummarizeBtn.disabled = true;

    step1.className = (mode === 'llm_only') ? 'step done' : 'step active';
    step2.className = (mode === 'llm_only') ? 'step done' : 'step';
    step3.className = (mode === 'llm_only') ? 'step active' : 'step';

    let seconds = 0;
    elapsedTimer.textContent = `Thời gian xử lý: 0s`;
    clearInterval(timerInterval);
    timerInterval = setInterval(() => {
      seconds++;
      elapsedTimer.textContent = `Thời gian xử lý: ${seconds}s`;
    }, 1000);
  }

  function finishProcessingUI() {
    clearInterval(timerInterval);
    setTimeout(() => {
      statusContainer.classList.add('hidden');
      if (errorBanner) errorBanner.classList.add('hidden');
      resultsContent.classList.remove('hidden');
      outputActions.classList.remove('hidden');
      processBtn.disabled = false;
      if (selectedFiles.length > 0 && transcribeOnlyBtn) transcribeOnlyBtn.disabled = false;
    }, 500);
  }

  function handleErrorUI(err) {
    clearInterval(timerInterval);
    statusContainer.classList.add('hidden');
    placeholderState.classList.add('hidden');
    resultsContent.classList.add('hidden');
    
    let detailMsg = (typeof err === 'object' && err.detail) ? err.detail : (err.message || String(err));
    let status = (typeof err === 'object' && err.status) ? err.status : 500;

    if (!detailMsg.startsWith('Lỗi ')) {
      detailMsg = `Lỗi ${status}: "${detailMsg}"`;
    }

    if (errorBanner && errorTitle && errorDetail) {
      errorTitle.textContent = detailMsg;
      errorDetail.textContent = "Vui lòng kiểm tra lại Groq API Key (trên ô nhập liệu UI hoặc file .env), giới hạn số lượng file (<= 5 file) hoặc dung lượng (<= 300MB).";
      errorBanner.classList.remove('hidden');
    } else {
      alert(`❌ ${detailMsg}`);
    }

    processBtn.disabled = false;
    if (selectedFiles.length > 0 && transcribeOnlyBtn) transcribeOnlyBtn.disabled = false;
  }

  function saveAndRenderData(data) {
    meetingNotesMarkdown = data.meeting_notes || '';
    rawTranscriptText = data.raw_transcript || '';
    currentFilesDetail = data.files_detail || [];

    markdownViewer.innerHTML = marked.parse(meetingNotesMarkdown);
    transcriptViewer.value = rawTranscriptText;
    
    renderSubTabsUI(currentFilesDetail);

    statTotalTime.textContent = `${data.total_time ? data.total_time.toFixed(1) : (data.stats ? data.stats.total_time : 0)}s`;
    statSTTTime.textContent = `${data.stt_time ? data.stt_time.toFixed(1) : (data.stats ? data.stats.stt_time : 0)}s`;
    statLLMTime.textContent = `${data.llm_time ? data.llm_time.toFixed(1) : (data.stats ? data.stats.llm_time : 0)}s`;
    statWordCount.textContent = rawTranscriptText.trim().split(/\s+/).length;

    // Auto Backup to LocalStorage
    try {
      localStorage.setItem('kute_ai_backup_session', JSON.stringify({
        meeting_notes: meetingNotesMarkdown,
        raw_transcript: rawTranscriptText,
        files_detail: currentFilesDetail,
        stats: {
          total_time: data.total_time || 0,
          stt_time: data.stt_time || 0,
          llm_time: data.llm_time || 0
        },
        timestamp: Date.now()
      }));
      if (restoreSessionBtn) restoreSessionBtn.classList.remove('hidden');
    } catch (e) {
      console.warn("Could not save session to LocalStorage:", e);
    }
  }

  function renderSubTabsUI(filesDetail) {
    if (!transcriptSubTabs) return;

    if (!filesDetail || filesDetail.length <= 1) {
      transcriptSubTabs.classList.add('hidden');
      transcriptSubTabs.innerHTML = '';
      return;
    }

    transcriptSubTabs.classList.remove('hidden');
    transcriptSubTabs.innerHTML = '';

    // Tab 1: All Files
    const allTabBtn = document.createElement('button');
    allTabBtn.className = 'sub-tab-pill active';
    allTabBtn.textContent = `🌐 Tất cả (${filesDetail.length} file)`;
    allTabBtn.addEventListener('click', () => {
      transcriptSubTabs.querySelectorAll('.sub-tab-pill').forEach(b => b.classList.remove('active'));
      allTabBtn.classList.add('active');
      transcriptViewer.value = rawTranscriptText;
    });
    transcriptSubTabs.appendChild(allTabBtn);

    // Individual File Tabs
    filesDetail.forEach((fileItem, idx) => {
      const pillBtn = document.createElement('button');
      pillBtn.className = 'sub-tab-pill';
      pillBtn.textContent = `🎵 ${fileItem.filename}`;
      pillBtn.addEventListener('click', () => {
        transcriptSubTabs.querySelectorAll('.sub-tab-pill').forEach(b => b.classList.remove('active'));
        pillBtn.classList.add('active');
        transcriptViewer.value = fileItem.transcript;
      });
      transcriptSubTabs.appendChild(pillBtn);
    });
  }

  // Copy Sub-transcript Button
  if (copySubTranscriptBtn) {
    copySubTranscriptBtn.addEventListener('click', () => {
      const currentText = transcriptViewer.value ? transcriptViewer.value.trim() : '';
      if (!currentText) return;
      navigator.clipboard.writeText(currentText).then(() => {
        const origText = copySubTranscriptBtn.textContent;
        copySubTranscriptBtn.textContent = '✅ Đã copy!';
        setTimeout(() => copySubTranscriptBtn.textContent = origText, 2000);
      });
    });
  }

  // Copy Markdown Button
  copyNotesBtn.addEventListener('click', () => {
    if (!meetingNotesMarkdown) return;
    navigator.clipboard.writeText(meetingNotesMarkdown).then(() => {
      const origText = copyNotesBtn.textContent;
      copyNotesBtn.textContent = '✅ Đã copy!';
      setTimeout(() => copyNotesBtn.textContent = origText, 2000);
    });
  });

  // Download Markdown Button
  downloadNotesBtn.addEventListener('click', () => {
    if (!meetingNotesMarkdown) return;
    const blob = new Blob([meetingNotesMarkdown], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Meeting_Notes_${Date.now()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  });

  // Copy Slack / Teams Formatted Text
  if (copySlackBtn) {
    copySlackBtn.addEventListener('click', () => {
      if (!meetingNotesMarkdown) return;
      const slackFormatted = meetingNotesMarkdown
        .replace(/^# (.*$)/gim, '*$1*')
        .replace(/^## (.*$)/gim, '\n*$1*')
        .replace(/^### (.*$)/gim, '\n*$1*');
      
      navigator.clipboard.writeText(slackFormatted).then(() => {
        const origText = copySlackBtn.textContent;
        copySlackBtn.textContent = '✅ Đã copy Slack!';
        setTimeout(() => copySlackBtn.textContent = origText, 2000);
      });
    });
  }

  // Download Word (.doc) File
  if (downloadDocxBtn) {
    downloadDocxBtn.addEventListener('click', () => {
      if (!meetingNotesMarkdown) return;
      const htmlContent = `
        <html xmlns:o='urn:schemas-microsoft-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
        <head><meta charset='utf-8'><title>Meeting Notes</title>
        <style>
          body { font-family: 'Calibri', 'Arial', sans-serif; line-height: 1.6; color: #111; }
          h1 { color: #1E3A8A; border-bottom: 2px solid #1E3A8A; padding-bottom: 5px; }
          h2 { color: #2563EB; margin-top: 20px; border-bottom: 1px solid #DDD; padding-bottom: 3px; }
          table { border-collapse: collapse; width: 100%; margin: 15px 0; }
          th, td { border: 1px solid #CBD5E1; padding: 8px 12px; text-align: left; }
          th { background-color: #F1F5F9; color: #1E293B; }
          ul, ol { padding-left: 20px; }
        </style>
        </head>
        <body>${marked.parse(meetingNotesMarkdown)}</body>
        </html>
      `;
      const blob = new Blob(['\ufeff', htmlContent], { type: 'application/msword' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Meeting_Notes_${Date.now()}.doc`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
  }

  // Print / PDF Button
  if (printPdfBtn) {
    printPdfBtn.addEventListener('click', () => {
      if (!meetingNotesMarkdown) return;
      window.print();
    });
  }

  // Transcript Keyword Search & Highlight
  if (transcriptSearchInput && transcriptViewer && transcriptHighlightedView) {
    transcriptSearchInput.addEventListener('input', () => {
      const query = transcriptSearchInput.value.trim();
      const currentText = transcriptViewer.value || '';

      if (!query) {
        transcriptHighlightedView.classList.add('hidden');
        transcriptViewer.classList.remove('hidden');
        if (searchMatchCount) searchMatchCount.classList.add('hidden');
        return;
      }

      // Escape HTML special characters
      const escapedText = currentText
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");

      const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const regex = new RegExp(`(${escapedQuery})`, 'gi');
      
      const matches = (currentText.match(regex) || []).length;
      
      if (searchMatchCount) {
        searchMatchCount.textContent = `${matches} kết quả`;
        searchMatchCount.classList.remove('hidden');
      }

      const highlightedHTML = escapedText.replace(regex, '<mark>$1</mark>');
      transcriptHighlightedView.innerHTML = highlightedHTML;

      transcriptViewer.classList.add('hidden');
      transcriptHighlightedView.classList.remove('hidden');
    });
  }
});
