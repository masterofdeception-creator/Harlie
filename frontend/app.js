const recordButton = document.getElementById("recordButton");
const recordingIndicator = document.getElementById("recordingIndicator");
const transcriptBox = document.getElementById("transcript");
const responseBox = document.getElementById("response");
const textForm = document.getElementById("textForm");
const textInput = document.getElementById("textInput");
const avatarVideo = document.getElementById("avatarVideo");

let mediaRecorder = null;
let mediaStream = null;
let chunks = [];
let conversationId = null;

const API_BASE = window.location.origin;

async function sendPayload(formData) {
  const response = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unbekannter Fehler" }));
    throw new Error(error.detail || "Fehler bei der Kommunikation mit dem Server");
  }

  return response.json();
}

function updateUI({ transcript, response, talk }) {
  transcriptBox.textContent = transcript ? `Du: ${transcript}` : "";
  responseBox.textContent = response ? `Harlie: ${response}` : "";

  if (talk?.status === "done" && talk.result_url) {
    avatarVideo.src = talk.result_url;
    avatarVideo.play().catch(() => {});
  } else if (talk?.status === "error") {
    responseBox.textContent += "\n(D-ID Fehler: siehe Konsole)";
    console.error("D-ID Fehler", talk);
  } else if (talk?.status === "timeout") {
    responseBox.textContent += "\n(D-ID Rendering hat zu lange gedauert.)";
  }
}

async function handleAudioStop() {
  recordButton.disabled = false;
  recordingIndicator.hidden = true;

  if (!chunks.length) {
    return;
  }

  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop());
    mediaStream = null;
  }

  const blob = new Blob(chunks, { type: "audio/webm" });
  chunks = [];

  const formData = new FormData();
  if (conversationId) {
    formData.append("conversation_id", conversationId);
  }
  formData.append("audio", blob, "aufnahme.webm");

  try {
    const data = await sendPayload(formData);
    conversationId = data.conversationId;
    updateUI(data);
  } catch (error) {
    alert(error.message);
    console.error(error);
  }
}

recordButton.addEventListener("click", async () => {
  if (mediaRecorder?.state === "recording") {
    mediaRecorder.stop();
    if (mediaStream) {
      mediaStream.getTracks().forEach((track) => track.stop());
      mediaStream = null;
    }
    recordButton.textContent = "🎙️ Aufnahme starten";
    return;
  }

  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(mediaStream);
    chunks = [];

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        chunks.push(event.data);
      }
    };

    mediaRecorder.onstop = handleAudioStop;

    mediaRecorder.start();
    recordingIndicator.hidden = false;
    recordButton.textContent = "⏹️ Aufnahme beenden";
    recordButton.disabled = false;
  } catch (error) {
    console.error("Mikrofon Zugriff fehlgeschlagen", error);
    alert("Mikrofon Zugriff nicht möglich. Bitte Berechtigungen prüfen.");
  }
});

textForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = textInput.value.trim();
  if (!text) {
    return;
  }

  const formData = new FormData();
  formData.append("text", text);
  if (conversationId) {
    formData.append("conversation_id", conversationId);
  }

  textInput.value = "";
  recordButton.disabled = true;

  try {
    const data = await sendPayload(formData);
    conversationId = data.conversationId;
    updateUI(data);
  } catch (error) {
    alert(error.message);
    console.error(error);
  } finally {
    recordButton.disabled = false;
  }
});
