/**
 * camera.js - Módulo de captura y stream de cámara web para ErgoMonitor
 * Commit 5: Captura de stream de cámara, envío periódico de frames al backend
 * Commit 6: Integración HTTP con CSRF token Django, proxy de estadísticas
 */

const CAPTURE_INTERVAL_MS = 3000; // Envía un frame cada 3 segundos

const video = document.getElementById("camera-feed");
const canvas = document.getElementById("capture-canvas");
const startBtn = document.getElementById("start-btn");
const stopBtn = document.getElementById("stop-btn");
const statusBadge = document.getElementById("status-badge");
const postureValue = document.getElementById("posture-value");
const angleValue = document.getElementById("angle-value");
const messageValue = document.getElementById("posture-message");
const sessionValue = document.getElementById("session-value");
const alertBox = document.getElementById("alert-box");

// Elementos de estadísticas (añadidos en commit 7)
const statTotal = document.getElementById("stat-total");
const statGoodPct = document.getElementById("stat-good-pct");
const statBadPct = document.getElementById("stat-bad-pct");

let stream = null;
let captureInterval = null;
let statsInterval = null;
let isRunning = false;

// ─── Leer CSRF token de la cookie de Django ─────────────────────────────────
function getCsrfToken() {
  const name = "csrftoken";
  const cookies = document.cookie.split(";");
  for (let cookie of cookies) {
    const [key, value] = cookie.trim().split("=");
    if (key === name) return decodeURIComponent(value);
  }
  return "";
}

// ─── Iniciar cámara ────────────────────────────────────────────────────────────
async function startCamera() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { width: 640, height: 480, facingMode: "user" },
      audio: false,
    });
    video.srcObject = stream;
    await video.play();

    isRunning = true;
    startBtn.disabled = true;
    stopBtn.disabled = false;
    sessionValue.textContent = "Activa";
    sessionValue.style.color = "var(--success-color)";
    setStatus("Analizando postura...", "info");
    hideAlert();

    // Iniciar captura periódica de frames
    captureInterval = setInterval(captureAndSend, CAPTURE_INTERVAL_MS);

    // Enviar el primer frame inmediatamente
    captureAndSend();

    // Actualizar estadísticas cada 10 segundos mientras la sesión esté activa
    statsInterval = setInterval(fetchStats, 10000);

  } catch (err) {
    showAlert(
      "No se pudo acceder a la cámara. Verifica los permisos del navegador.",
      "error"
    );
    console.error("Error al acceder a la cámara:", err);
  }
}

// ─── Detener cámara ────────────────────────────────────────────────────────────
function stopCamera() {
  if (stream) {
    stream.getTracks().forEach((track) => track.stop());
    stream = null;
  }
  if (captureInterval) {
    clearInterval(captureInterval);
    captureInterval = null;
  }
  if (statsInterval) {
    clearInterval(statsInterval);
    statsInterval = null;
  }
  video.srcObject = null;
  isRunning = false;

  startBtn.disabled = false;
  stopBtn.disabled = true;
  sessionValue.textContent = "Inactiva";
  sessionValue.style.color = "var(--text-muted)";
  setStatus("Monitoreo detenido", "idle");
  resetMetrics();

  // Obtener stats finales al detener
  fetchStats();
}

// ─── Captura frame y envía al backend ─────────────────────────────────────────
function captureAndSend() {
  if (!isRunning || !video.srcObject) return;

  const ctx = canvas.getContext("2d");
  canvas.width = video.videoWidth || 640;
  canvas.height = video.videoHeight || 480;
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  const imageBase64 = canvas.toDataURL("image/jpeg", 0.7);
  sendFrameToAPI(imageBase64);
}

// ─── Enviar frame a la API FastAPI (directo, con CSRF) ─────────────────────────
async function sendFrameToAPI(imageBase64) {
  const apiUrl = window.FASTAPI_URL + "/api/v1/analyze-posture";

  try {
    const response = await fetch(apiUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
      },
      body: JSON.stringify({ image: imageBase64 }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.warn("Error del servidor:", errorData.detail || response.status);
      return;
    }

    const data = await response.json();
    updateUI(data);
  } catch (err) {
    console.error("Error de conexión con el servidor:", err);
    showAlert("No se puede conectar con el servidor de análisis.", "error");
  }
}

// ─── Obtener estadísticas via proxy Django ─────────────────────────────────────
async function fetchStats() {
  try {
    const response = await fetch("/stats/", {
      method: "GET",
      headers: {
        "X-CSRFToken": getCsrfToken(),
        "X-Requested-With": "XMLHttpRequest",
      },
      credentials: "same-origin",
    });

    if (!response.ok) return;

    const data = await response.json();
    updateStatsUI(data);
  } catch (err) {
    console.warn("No se pudieron obtener estadísticas:", err);
  }
}

// ─── Actualizar métricas en la UI ─────────────────────────────────────────────
function updateUI(data) {
  const { posture, angle, message } = data;

  // Ángulo de inclinación
  angleValue.textContent = angle.toFixed(1) + "°";

  // Estado de postura
  if (posture === "good") {
    postureValue.textContent = "✅ Buena";
    postureValue.style.color = "var(--success-color)";
    setStatus("Postura correcta", "good");
    hideAlert();
  } else {
    postureValue.textContent = "⚠️ Mala";
    postureValue.style.color = "var(--danger-color)";
    setStatus("Postura incorrecta - ¡Corrígela!", "bad");
    showAlert(
      message || "Inclinación excesiva. Ajusta la posición de tu cuello y espalda.",
      "warning"
    );
  }

  // Mensaje descriptivo
  if (messageValue) {
    messageValue.textContent = message || "";
  }
}

// ─── Actualizar panel de estadísticas en la UI ────────────────────────────────
function updateStatsUI(data) {
  if (statTotal) statTotal.textContent = data.total_samples ?? "—";
  if (statGoodPct) statGoodPct.textContent = (data.good_percentage ?? 0).toFixed(1) + "%";
  if (statBadPct) statBadPct.textContent = (data.bad_percentage ?? 0).toFixed(1) + "%";
}

// ─── Helpers de UI ─────────────────────────────────────────────────────────────
function setStatus(text, type) {
  statusBadge.textContent = text;
  statusBadge.className = "status-badge status-" + type;
}

function resetMetrics() {
  postureValue.textContent = "—";
  postureValue.style.color = "var(--text-muted)";
  angleValue.textContent = "—";
  if (messageValue) messageValue.textContent = "";
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
if (stopBtn) stopBtn.addEventListener("click", stopCamera);

// Asegurar que la cámara se detiene si el usuario cierra la pestaña
window.addEventListener("beforeunload", () => {
  if (isRunning) stopCamera();
});

// Cargar estadísticas iniciales al entrar al dashboard
document.addEventListener("DOMContentLoaded", () => {
  fetchStats();

  // Ocultar placeholder cuando la cámara esté activa
  const placeholder = document.getElementById("video-placeholder");
  if (video && placeholder) {
    video.addEventListener("play", () => {
      placeholder.style.display = "none";
    });
  }
});
