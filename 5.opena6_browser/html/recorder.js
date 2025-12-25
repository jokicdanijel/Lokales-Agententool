// 🎬 Browser Agent 6.0 - Workflow Recorder & Timeline

let isRecording = false;
let recordingData = [];
let recordingStartTime = null;
let currentRecording = null;
let timelineChart = null;
let recordingTimer = null;

// ===============================================
// Recording Control Functions
// ===============================================

function toggleRecording() {
  const button = document.querySelector('[onclick="toggleRecording()"]');
  const recorderPanel = document.getElementById("workflowRecorder");
  const timeline = document.getElementById("workflowTimeline");

  if (isRecording) {
    // Stop recording
    stopRecording();
    button.textContent = "🔴 Record";
    button.className = "btn btn-danger btn-sm";

    showNotification("Recording stopped", "info");
  } else {
    // Start recording
    startRecording();
    button.textContent = "⏹️ Stop Recording";
    button.className = "btn btn-warning btn-sm";
    recorderPanel.style.display = "block";
    timeline.style.display = "block";

    showNotification("Recording started", "success");
  }
}

function startRecording() {
  isRecording = true;
  recordingData = [];
  recordingStartTime = Date.now();

  currentRecording = {
    id: generateRecordingId(),
    startTime: new Date().toISOString(),
    actions: [],
    metadata: {
      userAgent: navigator.userAgent,
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight,
      },
    },
  };

  // Start recording timer
  updateRecordingTime();
  recordingTimer = setInterval(updateRecordingTime, 1000);

  // Initialize timeline
  initializeTimeline();

  console.log("Workflow recording started:", currentRecording.id);
}

function stopRecording() {
  isRecording = false;

  if (recordingTimer) {
    clearInterval(recordingTimer);
    recordingTimer = null;
  }

  if (currentRecording) {
    currentRecording.endTime = new Date().toISOString();
    currentRecording.duration = Date.now() - recordingStartTime;

    // Save recording
    saveRecording(currentRecording);

    // Update UI
    updateRecordingsList();
    updateTimelineChart();
  }

  console.log("Workflow recording stopped");
}

function generateRecordingId() {
  return "rec_" + Date.now() + "_" + Math.random().toString(36).substr(2, 9);
}

function updateRecordingTime() {
  const recordingTime = document.getElementById("recordingTime");
  if (recordingTime && recordingStartTime) {
    const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    recordingTime.textContent = `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
  }
}

// ===============================================
// Action Recording
// ===============================================

function recordAction(type, data = {}) {
  if (!isRecording || !currentRecording) return;

  const timestamp = Date.now();
  const relativeTime = timestamp - recordingStartTime;

  const action = {
    id: generateActionId(),
    type: type,
    timestamp: timestamp,
    relativeTime: relativeTime,
    data: { ...data },
    screenshot: null, // Could be populated if screenshot capture is enabled
  };

  currentRecording.actions.push(action);
  recordingData.push(action);

  // Update live timeline
  addActionToTimeline(action);

  // Update action count
  updateActionCount();

  console.log("Action recorded:", action);
}

function generateActionId() {
  return "action_" + Date.now() + "_" + Math.random().toString(36).substr(2, 6);
}

function updateActionCount() {
  const actionCount = document.getElementById("actionCount");
  if (actionCount) {
    actionCount.textContent = currentRecording
      ? currentRecording.actions.length
      : 0;
  }
}

// ===============================================
// Automatic Action Detection
// ===============================================

// Override API functions to record actions automatically
const originalApi = api;
window.api = async function (path, method = "GET", payload = null) {
  const result = await originalApi(path, method, payload);

  // Record API calls as actions
  if (isRecording && (method === "POST" || method === "PUT")) {
    let actionType = "api_call";
    let actionData = { path, method };

    // Detect specific action types
    if (path === "/command" && payload) {
      actionType = payload.command || "command";
      actionData = {
        ...actionData,
        command: payload.command,
        args: payload.args,
      };
    } else if (path === "/specialized" && payload) {
      actionType = payload.action || "specialized";
      actionData = {
        ...actionData,
        action: payload.action,
        source: payload.source,
      };
    }

    recordAction(actionType, actionData);
  }

  return result;
};

// Record DOM interactions
document.addEventListener("click", function (event) {
  if (!isRecording) return;

  const target = event.target;
  const selector = generateSelector(target);

  recordAction("click", {
    selector: selector,
    tagName: target.tagName.toLowerCase(),
    id: target.id,
    className: target.className,
    text: target.textContent ? target.textContent.substring(0, 100) : "",
    coordinates: {
      x: event.clientX,
      y: event.clientY,
    },
  });
});

document.addEventListener("input", function (event) {
  if (!isRecording) return;

  const target = event.target;
  const selector = generateSelector(target);

  recordAction("input", {
    selector: selector,
    tagName: target.tagName.toLowerCase(),
    type: target.type,
    value: target.value ? target.value.substring(0, 100) : "",
  });
});

function generateSelector(element) {
  if (element.id) {
    return `#${element.id}`;
  }

  if (element.className) {
    const classes = element.className.split(" ").filter((c) => c.length > 0);
    if (classes.length > 0) {
      return `.${classes[0]}`;
    }
  }

  const tagName = element.tagName.toLowerCase();
  const parent = element.parentElement;

  if (parent) {
    const siblings = Array.from(parent.children);
    const index = siblings.indexOf(element);
    return `${generateSelector(parent)} > ${tagName}:nth-child(${index + 1})`;
  }

  return tagName;
}

// ===============================================
// Recording Management
// ===============================================

function saveRecording(recording) {
  const recordings = getStoredRecordings();
  recordings.push(recording);
  localStorage.setItem("browser_agent_recordings", JSON.stringify(recordings));
}

function getStoredRecordings() {
  const stored = localStorage.getItem("browser_agent_recordings");
  return stored ? JSON.parse(stored) : [];
}

function loadRecording(recordingId) {
  const recordings = getStoredRecordings();
  return recordings.find((r) => r.id === recordingId);
}

function deleteRecording(recordingId) {
  const recordings = getStoredRecordings();
  const filtered = recordings.filter((r) => r.id !== recordingId);
  localStorage.setItem("browser_agent_recordings", JSON.stringify(filtered));
  updateRecordingsList();

  showNotification("Recording deleted", "info");
}

function updateRecordingsList() {
  const recordingsList = document.getElementById("recordingsList");
  if (!recordingsList) return;

  const recordings = getStoredRecordings();

  if (recordings.length === 0) {
    recordingsList.innerHTML =
      '<div class="text-muted">No recordings available</div>';
    return;
  }

  const html = recordings
    .map(
      (recording) => `
        <div class="recording-item" data-id="${recording.id}">
            <div class="recording-header">
                <strong>${recording.id}</strong>
                <span class="recording-date">${new Date(recording.startTime).toLocaleString()}</span>
            </div>
            <div class="recording-details">
                <span>Actions: ${recording.actions.length}</span>
                <span>Duration: ${formatDuration(recording.duration || 0)}</span>
            </div>
            <div class="recording-actions">
                <button onclick="playRecording('${recording.id}')" class="btn btn-primary btn-xs">▶️ Play</button>
                <button onclick="exportRecording('${recording.id}')" class="btn btn-secondary btn-xs">📁 Export</button>
                <button onclick="deleteRecording('${recording.id}')" class="btn btn-danger btn-xs">🗑️ Delete</button>
            </div>
        </div>
    `,
    )
    .join("");

  recordingsList.innerHTML = html;
}

function formatDuration(ms) {
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);

  if (hours > 0) {
    return `${hours}h ${minutes % 60}m ${seconds % 60}s`;
  } else if (minutes > 0) {
    return `${minutes}m ${seconds % 60}s`;
  } else {
    return `${seconds}s`;
  }
}

// ===============================================
// Recording Playback
// ===============================================

async function playRecording(recordingId) {
  const recording = loadRecording(recordingId);
  if (!recording) {
    showNotification("Recording not found", "error");
    return;
  }

  showNotification(`Playing recording: ${recordingId}`, "info");

  for (const action of recording.actions) {
    try {
      await playAction(action);

      // Wait for next action (respect original timing or use fixed delay)
      const nextAction =
        recording.actions[recording.actions.indexOf(action) + 1];
      if (nextAction) {
        const delay = Math.min(
          nextAction.relativeTime - action.relativeTime,
          5000,
        ); // Max 5s delay
        await new Promise((resolve) =>
          setTimeout(resolve, Math.max(delay, 100)),
        ); // Min 100ms delay
      }
    } catch (error) {
      console.error("Failed to play action:", action, error);
      showNotification(`Action failed: ${action.type}`, "warning");
    }
  }

  showNotification("Recording playback completed", "success");
}

async function playAction(action) {
  switch (action.type) {
    case "click":
      if (action.data.selector) {
        await api("/command", "POST", {
          command: "click",
          args: { selector: action.data.selector },
        });
      }
      break;

    case "input":
    case "type":
      if (action.data.selector && action.data.value) {
        await api("/command", "POST", {
          command: "type",
          args: {
            selector: action.data.selector,
            text: action.data.value,
          },
        });
      }
      break;

    case "goto":
      if (action.data.args && action.data.args.url) {
        await api("/command", "POST", {
          command: "goto",
          args: action.data.args,
        });
      }
      break;

    default:
      // Try to replay the original command
      if (action.data.command && action.data.args) {
        await api("/command", "POST", {
          command: action.data.command,
          args: action.data.args,
        });
      } else if (action.data.action) {
        await api("/specialized", "POST", {
          action: action.data.action,
          source: action.data.source,
        });
      }
      break;
  }
}

// ===============================================
// Timeline Visualization
// ===============================================

function initializeTimeline() {
  const timelineContainer = document.getElementById("timelineChart");
  if (!timelineContainer) return;

  // Clear existing timeline
  timelineContainer.innerHTML =
    '<canvas id="timelineCanvas" width="800" height="200"></canvas>';

  const canvas = document.getElementById("timelineCanvas");
  const ctx = canvas.getContext("2d");

  // Set up timeline chart
  timelineChart = { canvas, ctx, actions: [] };

  drawTimelineBackground();
}

function addActionToTimeline(action) {
  if (!timelineChart) return;

  timelineChart.actions.push(action);
  updateTimelineChart();
}

function updateTimelineChart() {
  if (!timelineChart) return;

  const { canvas, ctx, actions } = timelineChart;

  // Clear canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Draw background
  drawTimelineBackground();

  // Draw actions
  if (actions.length === 0) return;

  const maxTime = Math.max(...actions.map((a) => a.relativeTime));
  const timeScale = maxTime > 0 ? (canvas.width - 100) / maxTime : 1;

  actions.forEach((action, index) => {
    const x = 50 + action.relativeTime * timeScale;
    const y = 50 + (index % 10) * 15;

    // Draw action point
    ctx.fillStyle = getActionColor(action.type);
    ctx.beginPath();
    ctx.arc(x, y, 4, 0, 2 * Math.PI);
    ctx.fill();

    // Draw action line
    if (index > 0) {
      const prevAction = actions[index - 1];
      const prevX = 50 + prevAction.relativeTime * timeScale;
      const prevY = 50 + ((index - 1) % 10) * 15;

      ctx.strokeStyle = "#444";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(prevX, prevY);
      ctx.lineTo(x, y);
      ctx.stroke();
    }

    // Draw action label
    if (actions.length < 20) {
      // Only show labels if not too crowded
      ctx.fillStyle = "#fff";
      ctx.font = "10px monospace";
      ctx.fillText(action.type.substring(0, 8), x - 20, y - 8);
    }
  });
}

function drawTimelineBackground() {
  const { canvas, ctx } = timelineChart;

  // Background
  ctx.fillStyle = "#1a1a1a";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Grid lines
  ctx.strokeStyle = "#333";
  ctx.lineWidth = 1;

  for (let i = 0; i <= 10; i++) {
    const y = i * 20;
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(canvas.width, y);
    ctx.stroke();
  }

  for (let i = 0; i <= 20; i++) {
    const x = i * 40;
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, canvas.height);
    ctx.stroke();
  }

  // Labels
  ctx.fillStyle = "#666";
  ctx.font = "12px monospace";
  ctx.fillText("Timeline", 10, 20);
  ctx.fillText("Actions", 10, canvas.height - 10);
}

function getActionColor(actionType) {
  const colors = {
    click: "#4a9eff",
    input: "#28a745",
    type: "#28a745",
    goto: "#ffc107",
    scroll: "#6f42c1",
    screenshot: "#fd7e14",
    api_call: "#20c997",
    command: "#17a2b8",
    specialized: "#e83e8c",
  };

  return colors[actionType] || "#6c757d";
}

// ===============================================
// Export Functions
// ===============================================

function exportRecording(recordingId) {
  const recording = loadRecording(recordingId);
  if (!recording) {
    showNotification("Recording not found", "error");
    return;
  }

  const exportData = {
    ...recording,
    exportedAt: new Date().toISOString(),
    version: "1.0",
  };

  const blob = new Blob([JSON.stringify(exportData, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = `browser-recording-${recordingId}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);

  URL.revokeObjectURL(url);
  showNotification("Recording exported", "success");
}

function exportAllRecordings() {
  const recordings = getStoredRecordings();
  if (recordings.length === 0) {
    showNotification("No recordings to export", "warning");
    return;
  }

  const exportData = {
    recordings: recordings,
    exportedAt: new Date().toISOString(),
    version: "1.0",
    count: recordings.length,
  };

  const blob = new Blob([JSON.stringify(exportData, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = `browser-recordings-${new Date().toISOString().slice(0, 10)}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);

  URL.revokeObjectURL(url);
  showNotification(`${recordings.length} recordings exported`, "success");
}

// ===============================================
// Initialize Recorder
// ===============================================

document.addEventListener("DOMContentLoaded", function () {
  updateRecordingsList();
  console.log("🎬 Workflow Recorder initialized");
});
