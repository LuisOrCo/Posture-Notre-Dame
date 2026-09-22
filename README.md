# 🌿 Posture Notre Dame — Sistema de Salud y Monitoreo Ergonómico

Plataforma inteligente de evaluación biomecánica y corrección postural en tiempo real para la prevención de trastornos musculoesqueléticos en jornadas laborales y teletrabajo, desarrollada con **Django**, **FastAPI**, **MediaPipe Pose Estimation** y **MongoDB**.

## 🏗️ Arquitectura del Sistema

```
sistema-ergonomia-laboral/
├── backend/        # FastAPI + MediaPipe Pose + MongoDB (Evaluación Biomecánica)
│   └── app/
│       ├── api/routes/   # auth.py, posture.py
│       ├── core/         # config, security (JWT + bcrypt)
│       ├── schemas/      # Pydantic models
│       ├── services/     # posture_analyzer, pose_detector, auth_service
│       ├── database.py   # Conexión MongoDB
│       └── main.py       # Entrada FastAPI & Swagger Docs
├── frontend/       # Django (Portal de Salud y Monitoreo)
│   ├── accounts/   # Registro y autenticación de usuarios
│   ├── monitor/    # Panel clínico de monitoreo y proxy de estadísticas
│   ├── static/     # CSS clínico verde salud + JS biométrico (camera.js)
│   └── templates/  # Plantillas HTML responsivas (base, dashboard, auth)
├── vercel.json     # Configuración de despliegue serverless
└── README.md
```

## 🩺 Características Principales

| Módulo | Descripción |
|--------|-------------|
| **Diseño Clínico & Ergonomía** | Interfaz profesional con paleta verde salud (bienestar, salud postural y medicina del trabajo) |
| **Acceso Seguro** | Registro e inicio de sesión con control de accesos y sesiones autenticadas |
| **Captura Biomecánica** | Transmisión de webcam y captura periódica optimizada (cada 3 s) |
| **Evaluación de Ángulos** | Cálculo instantáneo del ángulo cuello/hombros con umbral clínico de 15.0° |
| **Monitoreo Continuo** | Temporizador de sesión en vivo y feedback ergonómico inmediato |
| **Métricas Acumuladas** | Panel de rendimiento: total de muestras, porcentaje óptimo y desalineado |
| **Integración Resiliente** | Proxy HTTP Django ↔ FastAPI, soporte CSRF y reintentos con backoff exponencial |

## ⚙️ Configuración y Ejecución Local

### Requisitos Previos
- Python 3.10+
- MongoDB (local o MongoDB Atlas)

---

### 1. Backend (FastAPI - Puerto 8000)

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Crea o revisa `backend/.env`:
```env
MONGODB_URI=mongodb://localhost:27017
DB_NAME=ergonomia_db
SECRET_KEY=clave_secreta_jwt_posture_notre_dame
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALLOWED_ORIGINS=http://localhost:8001,http://127.0.0.1:8001
```

Inicia el servidor de análisis:
```powershell
uvicorn app.main:app --reload --port 8000
```
*Documentación interactiva disponible en: [http://localhost:8000/docs](http://localhost:8000/docs)*

---

### 2. Frontend (Django - Puerto 8001)

```powershell
cd frontend
python -m venv venv
venv\Scripts\activate
pip install django
python manage.py migrate
python manage.py runserver 8001
```

Accede al portal web en: **[http://localhost:8001](http://localhost:8001)**

---

## 🌐 Despliegue en Producción (Vercel)

1. Conecta el repositorio en [vercel.com](https://vercel.com)
2. Define las siguientes variables de entorno:

| Variable | Descripción |
|----------|-------------|
| `MONGODB_URI` | Cadena de conexión a MongoDB Atlas |
| `DB_NAME` | Nombre de base de datos |
| `SECRET_KEY` | Clave JWT para el backend |
| `DJANGO_SECRET_KEY` | Clave de seguridad de Django |
| `ALLOWED_ORIGINS` | Dominio de producción (ej: `https://posture-notre-dame.vercel.app`) |
| `ALLOWED_HOSTS` | Hosts permitidos de Django |
| `FASTAPI_BASE_URL` | URL de la API en producción |

---

## 📌 Endpoints API

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/v1/auth/register` | Registrar nuevo usuario |
| `POST` | `/api/v1/auth/login` | Iniciar sesión y emitir token JWT |
| `GET`  | `/api/v1/auth/me` | Obtener perfil del usuario autenticado |
| `POST` | `/api/v1/analyze-posture` | Analizar frame en Base64 e inferir postura con MediaPipe |
| `GET`  | `/api/v1/posture-stats` | Consultar estadísticas ergonómicas acumuladas |
| `GET`  | `/health` | Chequeo de salud del servicio y MongoDB |

---

## 📜 Licencia

MIT License — **Posture Notre Dame** &bull; [LuisOrCo/Posture-Notre-Dame](https://github.com/LuisOrCo/Posture-Notre-Dame)
