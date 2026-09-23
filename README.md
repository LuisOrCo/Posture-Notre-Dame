# 🌿 Posture Notre Dame — Sistema de Salud y Monitoreo Ergonómico

Plataforma inteligente de evaluación biomecánica y corrección postural en tiempo real para la prevención de trastornos musculoesqueléticos en jornadas laborales y teletrabajo, desarrollada con **Django**, **FastAPI**, **MediaPipe Pose Estimation** y **MongoDB**.

# 👨‍🎓👨‍🎓 Aprendices que realizaron el proyecto de la ficha 3406204

* ## Luis Ángel Ortega Correa
* ## Breiner Ocampo Arteaga

---

## 🚀 Enlaces de Despliegue en Producción (Vercel)

| Servicio | Entorno | Enlace de Acceso |
| :--- | :--- | :--- |
| 🖥️ **Frontend (Portal Web)** | Producción | [https://posture-notre-dame-7ns2itr5o-los-programmer-ranger.vercel.app/](https://posture-notre-dame-7ns2itr5o-los-programmer-ranger.vercel.app/) |
| ⚙️ **Backend (FastAPI)** | Producción | [https://posture-4ic9cpimb-los-programmer-ranger.vercel.app/](https://posture-4ic9cpimb-los-programmer-ranger.vercel.app/) |
| 📑 **Documentación Swagger UI** | API Docs | [https://posture-4ic9cpimb-los-programmer-ranger.vercel.app/docs](https://posture-4ic9cpimb-los-programmer-ranger.vercel.app/docs) |
| 🩺 **Salud de API & MongoDB** | Health Check | [https://posture-4ic9cpimb-los-programmer-ranger.vercel.app/health](https://posture-4ic9cpimb-los-programmer-ranger.vercel.app/health) |

---

## 🏗️ Arquitectura del Sistema

```
sistema-ergonomia-laboral/
├── backend/        # FastAPI + MediaPipe Pose + MongoDB Atlas (API de Evaluación)
│   ├── app/
│   │   ├── api/routes/   # auth.py, posture.py
│   │   ├── core/         # config, security (JWT + bcrypt)
│   │   ├── schemas/      # Pydantic models (auth, posture)
│   │   ├── services/     # posture_analyzer, pose_detector, auth_service
│   │   ├── database.py   # Conexión MongoDB Atlas
│   │   └── main.py       # Entrada FastAPI & Swagger Docs
│   ├── vercel.json       # Configuración de despliegue independiente del backend
│   └── requirements.txt  # Dependencias optimizadas para serverless
├── frontend/       # Django (Portal de Salud y Monitoreo Ergonómico)
│   ├── accounts/   # Registro y autenticación integrada con MongoDB
│   ├── monitor/    # Panel clínico de monitoreo y dashboard
│   ├── static/     # CSS clínico verde salud + JS MediaPipe en tiempo real
│   ├── templates/  # Plantillas HTML responsivas (base, dashboard, login, register)
│   ├── vercel.json # Configuración de despliegue independiente del frontend
│   └── requirements.txt
├── vercel.json     # Configuración monorepo Vercel
├── requirements.txt
└── README.md
```

## 🩺 Características Principales

| Módulo | Descripción |
|--------|-------------|
| **Diseño Clínico & Ergonomía** | Interfaz profesional con paleta verde salud (bienestar, salud postural y medicina del trabajo) |
| **Acceso Seguro MongoDB** | Registro e inicio de sesión con contraseñas encriptadas en `bcrypt` y tokens `JWT` |
| **Inferencia MediaPipe en Vivo** | Detección de los 33 landmarks corporales con aceleración WebAssembly/GPU en el navegador |
| **Evaluación Biomecánica** | Cálculo instantáneo del ángulo cuello/hombros con umbral clínico de 15.0° |
| **Monitoreo Continuo** | Temporizador de sesión en vivo y feedback ergonómico inmediato |
| **Métricas Acumuladas** | Panel de rendimiento: total de muestras, porcentaje óptimo y desalineado en MongoDB |
| **Despliegue Serverless** | Arquitectura desacoplada en Vercel con alto rendimiento y baja latencia |

---

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
MONGODB_URL=mongodb+srv://<usuario>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=sistema_ergonomia
SECRET_KEY=clave_secreta_jwt_posture_notre_dame
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://localhost:8001,http://127.0.0.1:8001,*
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
pip install -r requirements.txt
python manage.py runserver 8001
```

Accede al portal web en: **[http://localhost:8001](http://localhost:8001)**

---

## 🌐 Variables de Entorno en Producción (Vercel)

### Para el Proyecto Backend (`backend`):
| Variable | Descripción |
|----------|-------------|
| `MONGODB_URL` | Cadena de conexión a MongoDB Atlas |
| `MONGODB_DATABASE` | Nombre de la base de datos (`sistema_ergonomia`) |
| `SECRET_KEY` | Clave secreta para la firma de tokens JWT |
| `ALLOWED_ORIGINS` | Orígenes CORS permitidos (`*` o dominio del frontend) |

### Para el Proyecto Frontend (`frontend`):
| Variable | Descripción |
|----------|-------------|
| `FASTAPI_BASE_URL` | URL pública del backend (`https://posture-4ic9cpimb-los-programmer-ranger.vercel.app`) |
| `DJANGO_SECRET_KEY` | Clave secreta de seguridad de Django |
| `DEBUG` | Modo depuración (`False`) |

---

## 📌 Endpoints API

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/v1/auth/register` | Registrar nuevo usuario en MongoDB |
| `POST` | `/api/v1/auth/login` | Iniciar sesión y emitir token JWT |
| `GET`  | `/api/v1/auth/me` | Obtener perfil del usuario autenticado |
| `POST` | `/api/v1/analyze-posture` | Registrar y evaluar métricas de postura con MediaPipe Pose |
| `GET`  | `/api/v1/posture-stats` | Consultar estadísticas ergonómicas acumuladas en MongoDB |
| `GET`  | `/health` | Chequeo de salud del servicio y conexión con MongoDB Atlas |
| `GET`  | `/docs` | Documentación interactiva Swagger UI |

---

## 📜 Licencia

MIT License — **Posture Notre Dame** &bull; [LuisOrCo/Posture-Notre-Dame](https://github.com/LuisOrCo/Posture-Notre-Dame)
