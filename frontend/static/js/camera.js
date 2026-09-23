/**
 * camera.js - Módulo de evaluación ergonómica en tiempo real con Google MediaPipe Pose
 * Ejecuta la red neuronal profunda de MediaPipe en el navegador (WebAssembly/GPU)
 * y sincroniza las métricas e historial con FastAPI y MongoDB Atlas.
 */

const SYNC_INTERVAL_MS  = 3000;  // Sincroniza métricas con MongoDB cada 3 segundos
const STATS_INTERVAL_MS = 10000; // Actualiza estadísticas cada 10 segundos
const ANGLE_THRESHOLD   = 15.0;  // Umbral clínico en grados para buena postura

const video         = document.getElementById("camera-feed");
const poseCanvas    = document.getElementById("pose-canvas");
const captureCanvas = document.getElementById("capture-canvas");
const startBtn      = document.getElementById("start-btn");
const stopBtn       = document.getElementById("stop-btn");
const statusBadge   = document.getElementById("status-badge");
const postureValue  = document.getElementById("posture-value");
const angleValue    = document.getElementById("angle-value");
const messageValue  = document.getElementById("posture-message");
const alertBox      = document.getElementById("alert-box");
const sessionTimer  = document.getElementById("session-timer");
const statTotal     = document.getElementById("stat-total");
const statGoodPct   = document.getElementById("stat-good-pct");
const statBadPct    = document.getElementById("stat-bad-pct");
const connIndicator = document.getElementById("conn-indicator");

let stream            = null;
let isRunning         = false;
let sessionStart      = null;
let syncInterval      = null;
let statsInterval     = null;
let timerInterval     = null;
let animationFrameId  = null;
let poseModel         = null;
let isProcessingFrame = false;
let latestMetrics     = null;
let consecutiveErrors = 0;

// ─── CSRF Token ──────────────────────────────────────────────────────────────
function getCsrfToken() {
  const name = "csrftoken";
  for (let cookie of document.cookie.split(";")) {
    const [key, value] = cookie.trim().split("=");
    if (key === name) return decodeURIComponent(value);
  }
  return "";
}

// ─── Inicializar MediaPipe Pose ──────────────────────────────────────────────
function initMediaPipePose() {
  if (typeof Pose === "undefined") {
    console.warn("MediaPipe Pose CDN no disponible aún. Reintentando...");
    return false;
  }

  if (!poseModel) {
    try {
      poseModel = new Pose({
        locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`,
      });

      poseModel.setOptions({
        modelComplexity: 1,
        smoothLandmarks: true,
        enableSegmentation: false,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5,
      });

      poseModel.onResults(onPoseResults);
      console.log("MediaPipe Pose Landmarker inicializado en el navegador exitosamente.");
    } catch (e) {
      console.error("Error inicializando MediaPipe Pose:", e);
      return false;
    }
  }
  return true;
}

// ─── Callback de Resultados MediaPipe ────────────────────────────────────────
function onPoseResults(results) {
  if (!isRunning) return;

  const width  = video.videoWidth || 640;
  const height = video.videoHeight || 480;

  // Dibujar sobre el overlay canvas
  if (poseCanvas) {
    if (poseCanvas.width !== width || poseCanvas.height !== height) {
      poseCanvas.width = width;
      poseCanvas.height = height;
    }
    const ctx = poseCanvas.getContext("2d");
    ctx.clearRect(0, 0, width, height);

    if (results.poseLandmarks && results.poseLandmarks.length > 0) {
      // Dibujar esqueleto si drawing_utils está disponible
      if (typeof drawConnectors !== "undefined" && typeof POSE_CONNECTIONS !== "undefined") {
        drawConnectors(ctx, results.poseLandmarks, POSE_CONNECTIONS, {
          color: "rgba(82, 183, 136, 0.65)",
          lineWidth: 3,
        });
      }

      // Dibujar puntos clave (nariz, orejas, hombros)
      const keyIndices = [0, 7, 8, 11, 12];
      keyIndices.forEach((idx) => {
        const lm = results.poseLandmarks[idx];
        if (lm) {
          ctx.beginPath();
          ctx.arc(lm.x * width, lm.y * height, 6, 0, 2 * Math.PI);
          ctx.fillStyle = idx === 11 || idx === 12 ? "#2d6a4f" : "#52b788";
          ctx.fill();
          ctx.lineWidth = 2;
          ctx.strokeStyle = "#ffffff";
          ctx.stroke();
        }
      });
    }
  }

  // ─── Evaluación Biomecánica de Postura ──────────────────────────────────────
  if (!results.poseLandmarks || results.poseLandmarks.length === 0) {
    latestMetrics = {
      posture: "bad",
      angle: 0.0,
      message: "No se detectó silueta de persona en el encuadre.",
    };
    updateUI(latestMetrics);
    return;
  }

  const lm = results.poseLandmarks;
  const leftEar       = lm[7]  || { x: 0.5, y: 0.3 };
  const rightEar      = lm[8]  || { x: 0.5, y: 0.3 };
  const leftShoulder  = lm[11] || { x: 0.4, y: 0.6 };
  const rightShoulder = lm[12] || { x: 0.6, y: 0.6 };

  // Punto medio entre las orejas (cabeza / cuello superior)
  const earMidX = (leftEar.x + rightEar.x) / 2.0;
  const earMidY = (leftEar.y + rightEar.y) / 2.0;

  // Punto medio entre los hombros
  const shoulderMidX = (leftShoulder.x + rightShoulder.x) / 2.0;
  const shoulderMidY = (leftShoulder.y + rightShoulder.y) / 2.0;

  // Cálculo del ángulo de inclinación respecto al eje vertical
  const dx = Math.abs(earMidX - shoulderMidX);
  const dy = Math.abs(earMidY - shoulderMidY);
  const angleRad = Math.atan2(dx, dy || 0.0001);
  const angleDeg = Math.round(((angleRad * 180.0) / Math.PI) * 10) / 10;

  const isGood = angleDeg <= ANGLE_THRESHOLD;
  const postureStatus = isGood ? "good" : "bad";
  const message = isGood
    ? "Postura adecuada. Mantén la alineación ergonómica."
    : `Inclinación de cabeza/cuello excesiva (${angleDeg}° > ${ANGLE_THRESHOLD}°). Corrige la postura.`;

  latestMetrics = {
    posture: postureStatus,
    angle: angleDeg,
    message: message,
  };

  updateUI(latestMetrics);
}

// ─── Bucle de Procesamiento de Frames con MediaPipe ──────────────────────────
async function processVideoFrame() {
  if (!isRunning) return;

  if (video.readyState >= 2 && poseModel && !isProcessingFrame) {
    try {
      isProcessingFrame = true;
      await poseModel.send({ image: video });
    } catch (e) {
      console.warn("Error en frame de MediaPipe:", e);
    } finally {
      isProcessingFrame = false;
    }
  }

  if (isRunning) {
    animationFrameId = requestAnimationFrame(processVideoFrame);
  }
}

// ─── Iniciar Cámara y Modelo ─────────────────────────────────────────────────
async function startCamera() {
  initMediaPipePose();

  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: "user" },
      audio: false,
    });
    video.srcObject = stream;
    await video.play();

    isRunning = true;
    consecutiveErrors = 0;
    sessionStart = Date.now();
    startBtn.disabled = true;
    stopBtn.disabled  = false;
    setStatus("Analizando con MediaPipe...", "info");
    setConnectionStatus("online");
    hideAlert();

    // Iniciar bucle de visión y sincronizadores
    animationFrameId = requestAnimationFrame(processVideoFrame);
    syncInterval     = setInterval(syncMetricsWithBackend, SYNC_INTERVAL_MS);
    statsInterval    = setInterval(fetchStats, STATS_INTERVAL_MS);
    timerInterval    = setInterval(updateSessionTimer, 1000);

  } catch (err) {
    showAlert("No se pudo acceder a la cámara. Por favor autoriza los permisos en tu navegador.", "error");
    console.error("Error al acceder a la cámara:", err);
  }
}

// ─── Detener Cámara ──────────────────────────────────────────────────────────
function stopCamera() {
  isRunning = false;

  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
    animationFrameId = null;
  }

  if (stream) {
    stream.getTracks().forEach((t) => t.stop());
    stream = null;
  }

  clearInterval(syncInterval);
  clearInterval(statsInterval);
  clearInterval(timerInterval);
  syncInterval = statsInterval = timerInterval = null;

  video.srcObject = null;
  sessionStart = null;

  if (poseCanvas) {
    const ctx = poseCanvas.getContext("2d");
    ctx.clearRect(0, 0, poseCanvas.width, poseCanvas.height);
  }

  startBtn.disabled = false;
  stopBtn.disabled  = true;
  setStatus("Monitoreo en pausa", "idle");
  setConnectionStatus("offline");
  resetMetrics();
  if (sessionTimer) sessionTimer.textContent = "00:00:00";

  fetchStats(); // Sincronización final de estadísticas
}

// ─── Sincronizar Métricas con FastAPI y MongoDB ──────────────────────────────
async function syncMetricsWithBackend() {
  if (!isRunning || !latestMetrics) return;

  const apiUrl = (window.FASTAPI_URL || "") + "/api/v1/analyze-posture";

  try {
    const headers = {
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(),
    };
    if (window.JWT_TOKEN) {
      headers["Authorization"] = `Bearer ${window.JWT_TOKEN}`;
    }

    const payload = {
      angle: latestMetrics.angle,
      posture: latestMetrics.posture,
      message: latestMetrics.message,
    };

    const response = await fetch(apiUrl, {
      method: "POST",
      headers: headers,
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(6000),
    });

    if (response.ok) {
      consecutiveErrors = 0;
      setConnectionStatus("online");
    }
  } catch (err) {
    consecutiveErrors++;
    if (consecutiveErrors >= 3) {
      setConnectionStatus("offline");
    }
  }
}

// ─── Consultar Estadísticas Históricas de MongoDB ────────────────────────────
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
    console.warn("Estadísticas pendientes de sincronización:", err.name);
  }
}

// ─── Actualizar UI ────────────────────────────────────────────────────────────
function updateUI(data) {
  const { posture, angle, message } = data;

  if (angleValue) {
    angleValue.textContent = typeof angle === "number" ? angle.toFixed(1) + "°" : "—";
  }

  if (posture === "good") {
    if (postureValue) {
      postureValue.textContent = "Alineación Óptima";
      postureValue.style.color = "var(--health-good)";
    }
    setStatus("Postura Saludable", "good");
    hideAlert();
  } else {
    if (postureValue) {
      postureValue.textContent = "Inclinación Excesiva";
      postureValue.style.color = "var(--health-bad)";
    }
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

// ─── Contador de Sesión ──────────────────────────────────────────────────────
function updateSessionTimer() {
  if (!sessionStart || !sessionTimer) return;
  const elapsed = Math.floor((Date.now() - sessionStart) / 1000);
  const hh = String(Math.floor(elapsed / 3600)).padStart(2, "0");
  const mm = String(Math.floor((elapsed % 3600) / 60)).padStart(2, "0");
  const ss = String(elapsed % 60).padStart(2, "0");
  sessionTimer.textContent = `${hh}:${mm}:${ss}`;
}

function setConnectionStatus(status) {
  if (!connIndicator) return;
  if (status === "online") {
    connIndicator.textContent = "● MediaPipe Activo";
    connIndicator.className = "conn-badge conn-online";
  } else {
    connIndicator.textContent = "● Sensor en Pausa";
    connIndicator.className = "conn-badge conn-offline";
  }
}

function setStatus(text, type) {
  if (!statusBadge) return;
  statusBadge.textContent = text;
  statusBadge.className = "status-badge status-" + type;
}

function resetMetrics() {
  if (postureValue) {
    postureValue.textContent = "—";
    postureValue.style.color = "var(--text-light)";
  }
  if (angleValue) angleValue.textContent = "—";
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

// ─── Listeners ───────────────────────────────────────────────────────────────
if (startBtn) startBtn.addEventListener("click", startCamera);
if (stopBtn)  stopBtn.addEventListener("click", stopCamera);

window.addEventListener("beforeunload", () => {
  if (isRunning) stopCamera();
});

document.addEventListener("DOMContentLoaded", () => {
  initMediaPipePose();
  fetchStats();

  const placeholder = document.getElementById("video-placeholder");
  if (video && placeholder) {
    video.addEventListener("play", () => {
      placeholder.style.display = "none";
    });
  }
});
