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
  const customPromptInput = document.getElementById('customPrompt');
  const apiKeyInput = document.getElementById('apiKey');
  const presetChips = document.querySelectorAll('.chip');

  const placeholderState = document.getElementById('placeholderState');
  const statusContainer = document.getElementById('statusContainer');
  const resultsContent = document.getElementById('resultsContent');
  const outputActions = document.getElementById('outputActions');
  const elapsedTimer = document.getElementById('elapsedTimer');
  
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
  }

  function resetFileSelection() {
    selectedFile = null;
    audioFileInput.value = '';
    dropContent.classList.remove('hidden');
    fileInfo.classList.add('hidden');
    processBtn.disabled = true;
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

  processBtn.addEventListener('click', async () => {
    if (!selectedFile) return;
    startProcessingUI('all'); // Hàm helper ở dưới để reset UI gọn hơn

    const formData = new FormData();
    formData.append('audio_file', selectedFile);
    formData.append('custom_prompt', customPromptInput.value.trim());
    if (apiKeyInput.value.trim()) formData.append('groq_api_key', apiKeyInput.value.trim());

    try {
      setTimeout(() => { step1.className = 'step done'; step2.className = 'step active'; }, 800);

      const response = await fetch('/api/process', { method: 'POST', body: formData });
      step2.className = 'step done'; step3.className = 'step active';

      if (!response.ok) throw new Error((await response.json().catch(()=>({}))).detail || `Lỗi: ${response.status}`);
      const data = await response.json();
      step3.className = 'step done';

      // Lưu data & Render
      saveAndRenderData(data);
      finishProcessingUI();
      reSummarizeBtn.disabled = false; // Bật nút Re-summarize sau khi có text

    } catch (err) {
      handleErrorUI(err);
    }
  });


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

      if (!response.ok) throw new Error((await response.json().catch(()=>({}))).detail || `Lỗi: ${response.status}`);
      const data = await response.json();

      // Render Transcript
      rawTranscriptText = data.raw_transcript;
      transcriptViewer.textContent = rawTranscriptText;
      
      // Cập nhật stats STT
      statSTTTime.textContent = `${data.stt_time.toFixed(1)}s`;
      statWordCount.textContent = rawTranscriptText.trim().split(/\s+/).length;

      finishProcessingUI();
      
      reSummarizeBtn.disabled = false;
      switchToTab('transcript'); 

    } catch (err) {
      handleErrorUI(err);
    }
  });

  reSummarizeBtn.addEventListener('click', async () => {
    const currentTranscript = transcriptViewer.textContent.trim();
    if (!currentTranscript) {
      alert("Không có văn bản nào để tóm tắt!");
      return;
    }

    startProcessingUI('llm_only');

    const payload = {
      transcript: currentTranscript,
      custom_prompt: customPromptInput.value.trim(),
      groq_api_key: apiKeyInput.value.trim()
    };

    try {
      const response = await fetch('/api/summarize', { 
        method: 'POST', 
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload) 
      });

      if (!response.ok) throw new Error((await response.json().catch(()=>({}))).detail || `Lỗi: ${response.status}`);
      const data = await response.json();
      step3.className = 'step done';

      // Render Markdown
      meetingNotesMarkdown = data.meeting_notes;
      markdownViewer.innerHTML = marked.parse(meetingNotesMarkdown);
      statLLMTime.textContent = `${data.llm_time.toFixed(1)}s`;

      finishProcessingUI();
      
      switchToTab('notes'); 

    } catch (err) {
      handleErrorUI(err);
    }
  });

function startProcessingUI(mode) {
  placeholderState.classList.add('hidden');
  resultsContent.classList.add('hidden');
  outputActions.classList.add('hidden');
  statusContainer.classList.remove('hidden');
  
  processBtn.disabled = true;
  transcribeOnlyBtn.disabled = true;
  reSummarizeBtn.disabled = true;

  // Cài đặt Stepper tùy theo mode
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
    resultsContent.classList.remove('hidden');
    outputActions.classList.remove('hidden');
    processBtn.disabled = false;
    transcribeOnlyBtn.disabled = false;
    // reSummarizeBtn sẽ được enable thủ công ở logic từng nút
  }, 500);
}

function handleErrorUI(err) {
  clearInterval(timerInterval);
  statusContainer.classList.add('hidden');
  placeholderState.classList.remove('hidden');
  processBtn.disabled = false;
  transcribeOnlyBtn.disabled = false;
  // Giữ nguyên trạng thái reSummarizeBtn (có thể nó đang được bật từ trước)
  alert(`❌ Đã xảy ra lỗi: ${err.message}`);
}

function saveAndRenderData(data) {
  meetingNotesMarkdown = data.meeting_notes;
  rawTranscriptText = data.raw_transcript;
  markdownViewer.innerHTML = marked.parse(meetingNotesMarkdown);
  transcriptViewer.textContent = rawTranscriptText;
  
  statTotalTime.textContent = `${data.total_time.toFixed(1)}s`;
  statSTTTime.textContent = `${data.stt_time.toFixed(1)}s`;
  statLLMTime.textContent = `${data.llm_time.toFixed(1)}s`;
  statWordCount.textContent = rawTranscriptText.trim().split(/\s+/).length;
}

// Giả định hàm chuyển tab (bạn cần sửa id cho khớp với mã HTML của bạn)
function switchToTab(tabName) {
  if (tabName === 'transcript') {
    // Ví dụ: document.getElementById('tab-btn-transcript').click();
  } else if (tabName === 'notes') {
    // Ví dụ: document.getElementById('tab-btn-notes').click();
  }
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
