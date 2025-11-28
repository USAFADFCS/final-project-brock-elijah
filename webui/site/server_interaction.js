function fetchAllowedToolsMock(level) {
  return new Promise((resolve) => {
    setTimeout(() => {
      let allowed = [];
      // Logic based on PDF Policy Definitions:
      // Level 0-1: No/Minimal use. Tools disabled.
      // Level 2: Idea generation (Logic/Argument checks fit "brainstorming/structure").
      // Level 3: Feedback tool (Grammar, Tone, Citation, Vocab fit "editing tips").
      // Level 4+: Co-creation (All tools allowed).

      if (level >= 4) {
        allowed = allToolNames; // All allowed
      } else if (level === 3) {
        // Feedback & Editing allowed
        allowed = [
          "Grammar Check",
          "Tone Analysis",
          "Citation Fixer",
          "Vocabulary Boost",
          "Logic Flow",
          "Argument Check",
        ];
      } else if (level === 2) {
        // Brainstorming/Idea Gen allowed (Broad structural tools)
        allowed = ["Logic Flow", "Argument Check"];
      } else {
        // Level 0 & 1: Restricted
        allowed = [];
      }
      resolve(allowed);
    }, 400); // 400ms delay
  });
}

function mockServerInteraction(data) {
  console.log("Sending to server:", data);
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        revised_text:
          data.text +
          "\n\n[REVISED SECTION]\nThis essay demonstrates strong potential. The structure has been aligned with academic standards. Consider refining the thesis statement for greater clarity.",
        additional_downloadable_files: [
          { name: "Grammar_Report", extension: "pdf", data: "fakebytes" },
          { name: "Citation_Style_Guide", extension: "pdf", data: "fakebytes" },
        ],
        transcript: `[SYSTEM] Initializing Agent Swarm...
[AGENT-1] Analyzing input text for grammar and syntax.
[AGENT-1] Found 3 potential passive voice instances.
[AGENT-2] Checking against AI Level ${data.aiLevel} constraints. 
[AGENT-2] Level allows structural edits. Proceeding.
[TOOL-USE] Applying '${Array.from(state.selectedTools).join(", ")}'
[AGENT-3] Generating summary and revision suggestions...
[SYSTEM] Compilation complete.`,
      });
    }, 400); // 400ms delay
  });
}

/*
  Real server interaction helpers. These call the local Flask server
  hosted by `webui/host_ui.py` and its `/api/*` endpoints.
*/

async function getAllTools() {
  const res = await fetch('/api/get_all_tools');
  if (!res.ok) throw new Error('Failed to fetch all tools');
  const json = await res.json();
  return json.tools || [];
}

async function fetchAllowedTools(level) {
  const res = await fetch(`/api/get_allowed_tools?aiLevel=${encodeURIComponent(level)}`);
  if (!res.ok) throw new Error('Failed to fetch allowed tools');
  const json = await res.json();
  return json.allowed || [];
}

async function serverInteraction(data) {
  // data should be { aiLevel, instructions, text, tools }
  const res = await fetch('/api/run_analysis', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Server error: ${res.status} ${errText}`);
  }

  const json = await res.json();
  return json;
}

// Export functions for other scripts to use (browser globals)
window.api_getAllTools = getAllTools;
window.api_fetchAllowedTools = fetchAllowedTools;
window.api_runAnalysis = serverInteraction;
