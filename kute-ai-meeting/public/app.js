document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const dropZone = document.getElementById('dropZone');
  const audioFileInput = document.getElementById('audioFile');
  const dropContent = document.getElementById('dropContent');
  const fileInfo = document.getElementById('fileInfo');
  const fileName = document.getElementById('fileName');
  const fileSize = document.getElementById('fileSize');
  const removeFileBtn = document.getElementById('removeFileBtn');
  
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

  let selectedFile = null;
  let timerInterval = null;
  let meetingNotesMarkdown = '';
  let rawTranscriptText = '';

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
    const files = dt.files;
    if (files.length > 0) {
      handleFileSelected(files[0]);
    }
  });

  audioFileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      handleFileSelected(e.target.files[0]);
    }
  });

  removeFileBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    resetFileSelection();
  });

  function handleFileSelected(file) {
    selectedFile = file;
    fileName.textContent = file.name;
    fileSize.textContent = (file.size / (1024 * 1024)).toFixed(2) + ' MB';
    
    dropContent.classList.add('hidden');
    fileInfo.classList.remove('hidden');
    processBtn.disabled = false;
    if (transcribeOnlyBtn) transcribeOnlyBtn.disabled = false;
  }

  function resetFileSelection() {
    selectedFile = null;
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

  // 1. Full Pipeline Button (Process both STT and LLM)
  processBtn.addEventListener('click', async () => {
    if (!selectedFile) return;
    startProcessingUI('all');

    const formData = new FormData();
    formData.append('audio_file', selectedFile);
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

  // 2. Transcribe Only Button (STT)
  if (transcribeOnlyBtn) {
    transcribeOnlyBtn.addEventListener('click', async () => {
      if (!selectedFile) return;
      startProcessingUI('stt_only');

      const formData = new FormData();
      formData.append('audio_file', selectedFile);
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
      if (selectedFile && transcribeOnlyBtn) transcribeOnlyBtn.disabled = false;
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
      errorDetail.textContent = "Vui lòng kiểm tra lại Groq API Key (trên ô nhập liệu UI hoặc file .env), kết nối mạng hoặc định dạng file ghi âm.";
      errorBanner.classList.remove('hidden');
    } else {
      alert(`❌ ${detailMsg}`);
    }

    processBtn.disabled = false;
    if (selectedFile && transcribeOnlyBtn) transcribeOnlyBtn.disabled = false;
  }

  function saveAndRenderData(data) {
    meetingNotesMarkdown = data.meeting_notes;
    rawTranscriptText = data.raw_transcript;
    markdownViewer.innerHTML = marked.parse(meetingNotesMarkdown);
    transcriptViewer.value = rawTranscriptText;
    
    statTotalTime.textContent = `${data.total_time ? data.total_time.toFixed(1) : 0}s`;
    statSTTTime.textContent = `${data.stt_time ? data.stt_time.toFixed(1) : 0}s`;
    statLLMTime.textContent = `${data.llm_time ? data.llm_time.toFixed(1) : 0}s`;
    statWordCount.textContent = rawTranscriptText.trim().split(/\s+/).length;
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
});
