/**
 * camera.js - Módulo de evaluación ergonómica y captura para Posture Notre Dame
 */

const CAPTURE_INTERVAL_MS = 3000;  // Envía un frame cada 3 segundos
const STATS_INTERVAL_MS   = 10000; // Actualiza estadísticas cada 10 segundos
const MAX_RETRIES = 2;             // Reintentos máximos por frame fallido

const video         = document.getElementById("camera-feed");
const canvas        = document.getElementById("capture-canvas");
const startBtn      = document.getElementById("start-btn");
const stopBtn       = document.getElementById("stop-btn");
const statusBadge   = document.getElementById("status-badge");
const postureValue  = document.getElementById("posture-value");
const angleValue    = document.getElementById("angle-value");
const messageValue  = document.getElementById("posture-message");
const sessionValue  = document.getElementById("session-value");
const alertBox      = document.getElementById("alert-box");
const sessionTimer  = document.getElementById("session-timer");
const statTotal     = document.getElementById("stat-total");
const statGoodPct   = document.getElementById("stat-good-pct");
const statBadPct    = document.getElementById("stat-bad-pct");
const connIndicator = document.getElementById("conn-indicator");

let stream            = null;
let captureInterval   = null;
let statsInterval     = null;
let timerInterval     = null;
let isRunning         = false;
let sessionStart      = null;
let consecutiveErrors = 0;

// ─── CSRF token ──────────────────────────────────────────────────────────────
function getCsrfToken() {
  const name = "csrftoken";
  for (let cookie of document.cookie.split(";")) {
    const [key, value] = cookie.trim().split("=");
    if (key === name) return decodeURIComponent(value);
  }
  return "";
}

// ─── Iniciar cámara ──────────────────────────────────────────────────────────
async function startCamera() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { width: 640, height: 480, facingMode: "user" },
      audio: false,
    });
    video.srcObject = stream;
    await video.play();

    isRunning = true;
    consecutiveErrors = 0;
    sessionStart = Date.now();
    startBtn.disabled = true;
    stopBtn.disabled  = false;
    setStatus("Analizando alineación...", "info");
    setConnectionStatus("online");
    hideAlert();

    captureInterval = setInterval(captureAndSend, CAPTURE_INTERVAL_MS);
    statsInterval   = setInterval(fetchStats, STATS_INTERVAL_MS);
    timerInterval   = setInterval(updateSessionTimer, 1000);

    captureAndSend(); // Primer frame inmediato

  } catch (err) {
    showAlert("No se pudo acceder a la cámara. Por favor autoriza el permiso en tu navegador para evaluar tu postura.", "error");
    console.error("Error al acceder a la cámara:", err);
  }
}

// ─── Detener cámara ──────────────────────────────────────────────────────────
function stopCamera() {
  if (stream) {
    stream.getTracks().forEach((t) => t.stop());
    stream = null;
  }
  clearInterval(captureInterval);
  clearInterval(statsInterval);
  clearInterval(timerInterval);
  captureInterval = statsInterval = timerInterval = null;
  video.srcObject = null;
  isRunning = false;
  sessionStart = null;

  startBtn.disabled = false;
  stopBtn.disabled  = true;
  setStatus("Monitoreo en pausa", "idle");
  setConnectionStatus("offline");
  resetMetrics();
  if (sessionTimer) sessionTimer.textContent = "00:00:00";

  fetchStats(); // Stats finales al detener
}

// ─── Captura frame ───────────────────────────────────────────────────────────
function captureAndSend() {
  if (!isRunning || !video.srcObject) return;
  if (video.videoWidth === 0) return;

  const ctx = canvas.getContext("2d");
  canvas.width  = video.videoWidth  || 640;
  canvas.height = video.videoHeight || 480;
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  const imageBase64 = canvas.toDataURL("image/jpeg", 0.7);
  sendFrameToAPI(imageBase64);
}

// ─── Enviar frame a FastAPI ─────────────────────────────────────────────────
async function sendFrameToAPI(imageBase64, attempt = 1) {
  const apiUrl = window.FASTAPI_URL + "/api/v1/analyze-posture";

  try {
    const headers = {
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(),
    };
    if (window.JWT_TOKEN) {
      headers["Authorization"] = `Bearer ${window.JWT_TOKEN}`;
    }

    const response = await fetch(apiUrl, {
      method: "POST",
      headers: headers,
      body: JSON.stringify({ image: imageBase64 }),
      signal: AbortSignal.timeout(8000),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.warn(`[Intento ${attempt}] Respuesta de servidor:`, errorData.detail || response.status);
      handleServerError(imageBase64, attempt);
      return;
    }

    const data = await response.json();
    consecutiveErrors = 0;
    setConnectionStatus("online");
    updateUI(data);
    fetchStats(); // Actualizar el historial en tiempo real con la base de datos

  } catch (err) {
    console.error(`[Intento ${attempt}] Error de conexión:`, err.name, err.message);
    handleServerError(imageBase64, attempt);
  }
}


// ─── Manejo de errores con retry ─────────────────────────────────────────────
function handleServerError(imageBase64, attempt) {
  if (attempt < MAX_RETRIES) {
    const delay = attempt * 1500;
    setTimeout(() => sendFrameToAPI(imageBase64, attempt + 1), delay);
    return;
  }

  consecutiveErrors++;
  setConnectionStatus("offline");

  if (consecutiveErrors >= 3) {
    showAlert(
      "No hay comunicación con el módulo de inferencia. Verifica la disponibilidad del servidor de Posture Notre Dame.",
      "error"
    );
    setStatus("Servicio no disponible", "bad");
  }
}

// ─── Estadísticas via proxy Django → FastAPI ─────────────────────────────────
async function fetchStats() {
  try {
    const response = await fetch("/stats/", {
      method: "GET",
      headers: {
        "X-CSRFToken": getCsrfToken(),
        "X-Requested-With": "XMLHttpRequest",
      },
      credentials: "same-origin",
      signal: AbortSignal.timeout(6000),
    });

    if (!response.ok) return;

    const data = await response.json();
    updateStatsUI(data);

  } catch (err) {
    console.warn("No se pudieron sincronizar las estadísticas:", err.name);
  }
}

// ─── Actualizar métricas ──────────────────────────────────────────────────────
function updateUI(data) {
  const { posture, angle, message } = data;

  angleValue.textContent = typeof angle === "number" ? angle.toFixed(1) + "°" : "—";

  if (posture === "good") {
    postureValue.textContent = "Alineación Óptima";
    postureValue.style.color = "var(--health-good)";
    setStatus("Postura Saludable", "good");
    hideAlert();
  } else {
    postureValue.textContent = "Inclinación Excesiva";
    postureValue.style.color = "var(--health-bad)";
    setStatus("Riesgo Ergonómico", "bad");
    showAlert(
      message || "Alerta postural: Eleva tu cabeza y alinea los hombros para proteger la columna cervical.",
      "warning"
    );
  }

  if (messageValue) messageValue.textContent = message || "";
}

function updateStatsUI(data) {
  if (statTotal)   statTotal.textContent   = data.total_samples ?? "0";
  if (statGoodPct) statGoodPct.textContent = (data.good_percentage ?? 0).toFixed(1) + "%";
  if (statBadPct)  statBadPct.textContent  = (data.bad_percentage  ?? 0).toFixed(1) + "%";
}

// ─── Contador de sesión HH:MM:SS ─────────────────────────────────────────────
function updateSessionTimer() {
  if (!sessionStart || !sessionTimer) return;
  const elapsed = Math.floor((Date.now() - sessionStart) / 1000);
  const hh = String(Math.floor(elapsed / 3600)).padStart(2, "0");
  const mm = String(Math.floor((elapsed % 3600) / 60)).padStart(2, "0");
  const ss = String(elapsed % 60).padStart(2, "0");
  sessionTimer.textContent = `${hh}:${mm}:${ss}`;
}

// ─── Indicador de conexión ────────────────────────────────────────────────────
function setConnectionStatus(status) {
  if (!connIndicator) return;
  if (status === "online") {
    connIndicator.textContent = "● Sensor Conectado";
    connIndicator.className = "conn-badge conn-online";
  } else {
    connIndicator.textContent = "● Sin Conexión";
    connIndicator.className = "conn-badge conn-offline";
  }
}

// ─── Helpers de UI ────────────────────────────────────────────────────────────
function setStatus(text, type) {
  if (!statusBadge) return;
  statusBadge.textContent = text;
  statusBadge.className = "status-badge status-" + type;
}

function resetMetrics() {
  postureValue.textContent = "—";
  postureValue.style.color = "var(--text-light)";
  angleValue.textContent = "—";
  if (messageValue) messageValue.textContent = "Inicia la sesión para recibir retroalimentación médica inmediata.";
  setStatus("Inactivo", "idle");
}

function showAlert(text, type) {
  if (!alertBox) return;
  alertBox.textContent = text;
  alertBox.className = "alert alert-" + type;
  alertBox.style.display = "block";
}

function hideAlert() {
  if (!alertBox) return;
  alertBox.style.display = "none";
}

// ─── Event listeners ──────────────────────────────────────────────────────────
if (startBtn) startBtn.addEventListener("click", startCamera);
if (stopBtn)  stopBtn.addEventListener("click", stopCamera);

window.addEventListener("beforeunload", () => { if (isRunning) stopCamera(); });

document.addEventListener("DOMContentLoaded", () => {
  fetchStats();

  const placeholder = document.getElementById("video-placeholder");
  if (video && placeholder) {
    video.addEventListener("play", () => {
      placeholder.style.display = "none";
    });
  }
});
