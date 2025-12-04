/* --- CONFIG & DATA --- */

// --- PDF.js Worker Configuration ---
// We must set the worker source for PDF.js to function correctly.
pdfjsLib.GlobalWorkerOptions.workerSrc =
  "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";

// Updated with official descriptions from the Policy PDF
const aiLevelConfig = {
  0: {
    title: "Level 0: No use of GenAI",
    desc: "Cadets will create their own, original work without the use of GenAI in any manner.",
  },
  1: {
    title: "Level 1: Organizational / Explanatory use",
    desc: "Original work required for submission. GenAI allowed for personal efficiency (summarizing, clarifying) only.",
  },
  2: {
    title: "Level 2: Idea generation / Brainstorming",
    desc: "GenAI consulted for initial brainstorming, but cadets must create their own original work. Usage must be acknowledged.",
  },
  3: {
    title: "Level 3: Feedback tool on student work",
    desc: "Cadets write independently, then use GenAI for feedback/editing. Revisions must be manual; no AI text in submission.",
  },
  4: {
    title: "Level 4: Co-create and/or revise work",
    desc: "GenAI used for drafts/outlines. Cadets must critically evaluate and revise. Submission reflects cadet understanding, not unedited AI.",
  },
  5: {
    title: "Level 5: Unrestricted, attributed use",
    desc: "Unedited AI content allowed with clear attribution. Emphasis on transparency.",
  },
  6: {
    title: "Level 6: Unrestricted, unattributed use",
    desc: "Freely use GenAI without attribution (unless specified otherwise). Consider ethical/legal implications.",
  },
};

var allToolNames = ["placeholder", "placeholder", "placeholder"];

let state = {
  selectedTools: new Set(),
  allowedTools: new Set(), // Track what is currently permitted
  isProcessing: false,
  files: [],
};

/* --- INITIALIZATION --- */
document.addEventListener("DOMContentLoaded", () => {
  populateTools();
  updateAiDescription(0); // Set initial text
  handleAiLevelChange(0); // Initial permission check

  // Listen for text input to show/hide tools panel
  const essayInput = document.getElementById("essayText");
  essayInput.addEventListener("input", (e) => {
    const toolsPanel = document.getElementById("toolsPanel");
    if (e.target.value.length > 0) {
      toolsPanel.style.display = "block";
      // Trigger reflow for transition
      requestAnimationFrame(() => {
        toolsPanel.style.opacity = "1";
      });
    } else {
      toolsPanel.style.opacity = "0";
      setTimeout(() => {
        if (essayInput.value.length === 0) toolsPanel.style.display = "none";
      }, 500);
    }
  });
});

/* --- UI FUNCTIONS --- */

function togglePanel(header) {
  if (state.isProcessing) return;
  header.parentElement.classList.toggle("open");
}

// Called on slider 'input' for smooth text updates
document.getElementById("aiSlider").addEventListener("input", (e) => {
  updateAiDescription(e.target.value);
});

function updateAiDescription(val) {
  const descEl = document.getElementById("aiDesc");
  const config = aiLevelConfig[val];
  descEl.innerHTML = `<strong>${config.title}</strong>${config.desc}`;
}

// Called on slider 'change' (mouse up) to trigger server check
function handleAiLevelChange(val) {
  updateAiDescription(val);
  checkToolsPermission(val);
}

async function populateTools() {
  const grid = document.getElementById("toolsGrid");
  grid.innerHTML = "";
  allToolNames = await getAllTools();
  allToolNames.forEach((tool) => {
    const div = document.createElement("div");
    div.className = "tool-option";
    div.id = `tool-${tool.replace(/\s+/g, "-")}`;
    div.innerText = tool;
    div.onclick = () => toggleTool(div, tool);
    grid.appendChild(div);
  });

}

function toggleTool(el, toolName) {
  if (state.isProcessing) return;

  // Prevent selection if disabled
  if (el.classList.contains("disabled")) return;

  if (state.selectedTools.has(toolName)) {
    state.selectedTools.delete(toolName);
    el.classList.remove("selected");
  } else {
    state.selectedTools.add(toolName);
    el.classList.add("selected");
  }
}

function switchTab(tabId) {
  // Update Buttons
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.classList.remove("active");
    if (btn.dataset.tab === tabId) btn.classList.add("active");
  });

  // Update Panes
  document.querySelectorAll(".tab-pane").forEach((pane) => {
    pane.classList.remove("active");
  });
  document.getElementById(tabId).classList.add("active");
}

/* --- SERVER: PERMISSION CHECK --- */

// Simulates asking the server "Which tools are allowed for Level X?"
async function checkToolsPermission(levelVal) {
  const grid = document.getElementById("toolsGrid");
  grid.classList.add("loading"); // Visual cue (opacity drop)

  try {
    // Simulate network delay
    const allowed = await fetchAllowedTools(parseInt(levelVal));

    state.allowedTools = new Set(allowed);
    updateToolVisuals();
  } catch (err) {
    console.error("Permission check failed", err);
  } finally {
    grid.classList.remove("loading");
  }
}



function updateToolVisuals() {
  allToolNames.forEach((tool) => {
    const el = document.getElementById(`tool-${tool.replace(/\s+/g, "-")}`);
    const isAllowed = state.allowedTools.has(tool);

    if (isAllowed) {
      el.classList.remove("disabled");
    } else {
      el.classList.add("disabled");
      // Auto-deselect if it was selected but now forbidden
      if (state.selectedTools.has(tool)) {
        state.selectedTools.delete(tool);
        el.classList.remove("selected");
      }
    }
  });
}

/* --- FILE HANDLING (REAL PDF PARSING) --- */
async function handleFileUpload(input) {
  if (state.isProcessing) return;
  const file = input.files[0];
  if (!file) return;

  const textArea = document.getElementById("essayText");

  // Check for PDF type
  if (file.type === "application/pdf") {
    textArea.value = "Reading PDF file...";
    textArea.classList.add("disabled-ui"); // Visual cue (reuse disabled style)

    try {
      // Read file as ArrayBuffer
      const arrayBuffer = await file.arrayBuffer();

      // Load PDF document using pdf.js
      const loadingTask = pdfjsLib.getDocument({ data: arrayBuffer });
      const pdf = await loadingTask.promise;

      let fullText = "";

      // Iterate through pages
      for (let i = 1; i <= pdf.numPages; i++) {
        // Update UI with progress
        textArea.value = `Reading PDF page ${i} of ${pdf.numPages}...`;

        const page = await pdf.getPage(i);
        const textContent = await page.getTextContent();

        // Simple text extraction: join items with space
        // Note: pdf.js returns text chunks. Joining by space is a basic approximation.
        const pageText = textContent.items.map((item) => item.str).join(" ");
        fullText += pageText + "\n\n";
      }

      // Final Update
      textArea.value = fullText;
      // Trigger the input event to show tools/update UI
      textArea.dispatchEvent(new Event("input"));
    } catch (error) {
      console.error("PDF Read Error:", error);
      textArea.value = "Error reading PDF file. Please ensure it is a valid, text-based PDF.";
    } finally {
      textArea.classList.remove("disabled-ui");
      // Reset file input so same file can be selected again if needed
      input.value = "";
    }
  } else if (file.type.match("text.*")) {
    // Handle plain text files
    const reader = new FileReader();
    reader.onload = (e) => {
      textArea.value = e.target.result;
      textArea.dispatchEvent(new Event("input"));
    };
    reader.readAsText(file);
    input.value = "";
  } else {
    alert("Unsupported file type. Please upload a PDF or Text file.");
    input.value = "";
  }
}

/* --- SERVER INTERACTION ( --- */
async function runAgent() {
  if (state.isProcessing) return;

  const essayText = document.getElementById("essayText").value;
  if (!essayText.trim()) {
    alert("Please enter some text first.");
    return;
  }

  setProcessing(true);

  const requestData = {
    text: essayText,
    aiLevel: document.getElementById("aiSlider").value,
    tools: Array.from(state.selectedTools),
    instructions: document.getElementById("extraInstruct").value,
  };

  try {
    const response = await serverInteraction(requestData);
    handleResponse(response);
  } catch (error) {
    console.error("Error:", error);
    alert("An error occurred.");
  } finally {
    setProcessing(false);
  }
}



/* --- RESPONSE HANDLING --- */
function setProcessing(isProc) {
  state.isProcessing = isProc;
  const btn = document.getElementById("runBtn");
  const loader = document.getElementById("loader");
  const mainPanel = document.getElementById("mainPanel");
  const inputs = document.querySelectorAll("input, textarea, .tool-option");

  if (isProc) {
    btn.disabled = true;
    btn.innerText = "Processing...";
    loader.classList.add("active");
    mainPanel.classList.add("disabled-ui");
    inputs.forEach((el) => (el.style.pointerEvents = "none"));
  } else {
    btn.disabled = false;
    btn.innerText = "Run Analysis";
    loader.classList.remove("active");
    mainPanel.classList.remove("disabled-ui");
    inputs.forEach((el) => (el.style.pointerEvents = "auto"));
  }
}

function handleResponse(data) {
  // Update Text
  const textArea = document.getElementById("essayText");
  textArea.value = data.revised_text;

  // Create/Update Transcript Tab
  const transcriptId = "transcript";
  const transcriptContent = document.getElementById("transcriptContent");
  transcriptContent.innerText = data.transcript;

  // Add Tab Button if not exists
  const nav = document.getElementById("tabNav");
  if (!document.querySelector('button[data-tab="transcript"]')) {
    const btn = document.createElement("button");
    btn.className = "tab-btn";
    btn.dataset.tab = "transcript";
    btn.innerHTML = `<i class="fas fa-terminal"></i> Transcript <span class="close-tab" onclick="closeTranscript(event, this)">✕</span>`;
    btn.onclick = (e) => {
      // Prevent switching if clicking close
      if (e.target.classList.contains("close-tab")) return;
      switchTab("transcript");
    };
    nav.appendChild(btn);
  }

  // Handle Files - UPDATED SECTION
  const filesArea = document.getElementById("filesArea");
  filesArea.innerHTML = ""; // Clear old
  
  data.additional_downloadable_files.forEach((file) => {
    // 1. Create a Blob from the file content string
    const mimeType = getPlaintextMimeType(file.extension);
    const fileBlob = new Blob([file.data], { type: mimeType });

    // 2. Create a temporary URL for the Blob
    const fileURL = URL.createObjectURL(fileBlob);

    const a = document.createElement("a");
    a.className = "file-btn";
    a.href = fileURL;
    // --- KEY CHANGES ---
    // 3. Open in a new tab by adding target="_blank"
    a.target = "_blank"; 
    // 4. Remove a.download = ...
    // -------------------
    
    // 5. Clean up the object URL when the link is clicked
    a.onclick = (e) => {
      // This allows the link to navigate to the URL, opening the file in a new tab.
      // Clean up the object URL immediately after the click event processes
      setTimeout(() => URL.revokeObjectURL(fileURL), 100);
    };

    a.innerHTML = `<i class="fas fa-file-alt"></i> ${file.name}.${file.extension}`;
    filesArea.appendChild(a);
  });

  // Flash success color on text area
  textArea.style.borderColor = "var(--clr-success-a0)";
  setTimeout(() => (textArea.style.borderColor = ""), 1000);
}

// Helper function to determine specific plaintext MIME type
function getPlaintextMimeType(extension) {
    switch (extension.toLowerCase()) {
        case 'json':
            return 'application/json';
        case 'html':
            return 'text/html';
        case 'css':
            return 'text/css';
        case 'js':
            return 'text/javascript';
        case 'xml':
            return 'application/xml';
        default:
            return 'text/plain'; // Default for txt, log, etc.
    }
}

// Helper function to determine specific plaintext MIME type
function getPlaintextMimeType(extension) {
    switch (extension.toLowerCase()) {
        case 'json':
            return 'application/json';
        case 'html':
            return 'text/html';
        case 'css':
            return 'text/css';
        case 'js':
            return 'text/javascript';
        case 'xml':
            return 'application/xml';
        default:
            return 'text/plain'; // Default for txt, log, etc.
    }
}

// Helper function to determine MIME type
function getMimeType(extension) {
    switch (extension.toLowerCase()) {
        case 'pdf':
            return 'application/pdf';
        case 'txt':
            return 'text/plain';
        case 'docx':
            return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
        case 'zip':
            return 'application/zip';
        // Add more file types as needed
        default:
            return 'application/octet-stream'; // Default for unknown binary files
    }
}

function closeTranscript(e, closeBtn) {
  e.stopPropagation();
  const tabBtn = closeBtn.parentElement;
  const isAct = tabBtn.classList.contains("active");

  tabBtn.remove();
  // If we closed the active tab, switch back to essay
  if (isAct) switchTab("essay");
}
