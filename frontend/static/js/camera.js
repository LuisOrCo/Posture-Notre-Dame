/**
 * camera.js - Módulo de captura y stream de cámara web para ErgoMonitor
 * Commit 5: Captura de stream de cámara, envío periódico de frames al backend
 * y actualización de la UI con resultados de análisis postural.
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

let stream = null;
let captureInterval = null;
let isRunning = false;

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
  video.srcObject = null;
  isRunning = false;

  startBtn.disabled = false;
  stopBtn.disabled = true;
  sessionValue.textContent = "Inactiva";
  sessionValue.style.color = "var(--text-muted)";
  setStatus("Monitoreo detenido", "idle");
  resetMetrics();
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

// ─── Enviar frame a la API FastAPI ─────────────────────────────────────────────
async function sendFrameToAPI(imageBase64) {
  const apiUrl = window.FASTAPI_URL + "/api/v1/analyze-posture";

  try {
    const response = await fetch(apiUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ image: imageBase64 }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.warn("Error del servidor:", errorData.detail);
      return;
    }

    const data = await response.json();
    updateUI(data);
  } catch (err) {
    console.error("Error de conexión con el servidor:", err);
    showAlert("No se puede conectar con el servidor de análisis.", "error");
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
