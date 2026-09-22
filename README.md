# 🧘 ErgoMonitor — Sistema de Monitoreo de Ergonomía Laboral

Sistema web para detectar y corregir malas posturas durante jornadas de teletrabajo, usando visión por computador con **MediaPipe Pose Estimation**.

## 🏗️ Arquitectura

```
sistema-ergonomia-laboral/
├── backend/        # FastAPI + MediaPipe + MongoDB
│   └── app/
│       ├── api/routes/   # auth.py, posture.py
│       ├── core/         # config, security (JWT + bcrypt)
│       ├── schemas/      # Pydantic models
│       ├── services/     # posture_analyzer, pose_detector, auth_service
│       ├── database.py   # MongoDB client
│       └── main.py       # FastAPI app entry point
├── frontend/       # Django + SQLite (auth de sesión web)
│   ├── accounts/   # Registro y login de usuarios
│   ├── monitor/    # Dashboard de monitoreo
│   ├── static/     # CSS + JS (camera.js)
│   └── templates/  # HTML base + dashboard + auth
├── vercel.json     # Configuración de deployment
└── README.md
```

## 🚀 Funcionalidades

| Módulo | Descripción |
|--------|-------------|
| **Autenticación Django** | Registro, login y logout de usuarios con sesiones seguras |
| **Captura de cámara** | Stream de webcam en JS, captura periódica de frames cada 3 s |
| **Análisis postural** | MediaPipe Pose calcula el ángulo cuello/hombros y determina `good`/`bad` |
| **Integración HTTP** | Django actúa como proxy hacia FastAPI para evitar CORS en el cliente |
| **Estadísticas en tiempo real** | Panel de muestras acumuladas, porcentaje de buena/mala postura |
| **Retry logic** | Reintentos automáticos con backoff ante fallos de red |
| **Indicadores de UI** | Contador de sesión HH:MM:SS, badge de conexión, alertas animadas |

## ⚙️ Configuración Local

### Requisitos
- Python 3.10+
- MongoDB (local o Atlas)

### Backend (FastAPI)

```bash
cd backend
python -m venv venv
venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

Crea el archivo `backend/.env`:
```env
MONGODB_URI=mongodb://localhost:27017
DB_NAME=ergonomia_db
SECRET_KEY=tu_clave_secreta_jwt
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALLOWED_ORIGINS=http://localhost:8001,http://127.0.0.1:8001
```

Levanta el servidor:
```bash
uvicorn app.main:app --reload --port 8000
```

Documentación interactiva disponible en: [http://localhost:8000/docs](http://localhost:8000/docs)

### Frontend (Django)

```bash
cd frontend
python -m venv venv
venv\Scripts\activate       # Windows
pip install django
python manage.py migrate
python manage.py runserver 8001
```

Accede en: [http://localhost:8001](http://localhost:8001)

> **Nota:** El frontend Django corre en el puerto `8001` y el backend FastAPI en el `8000`.

## 🌐 Deploy en Vercel

1. Conecta el repositorio en [vercel.com](https://vercel.com)
2. Configura las variables de entorno en el panel de Vercel:

| Variable | Descripción |
|----------|-------------|
| `MONGODB_URI` | URI de conexión a MongoDB Atlas |
| `DB_NAME` | Nombre de la base de datos |
| `SECRET_KEY` | Clave JWT del backend |
| `DJANGO_SECRET_KEY` | Clave secreta de Django |
| `ALLOWED_ORIGINS` | Dominio de producción del frontend (ej: `https://mi-app.vercel.app`) |
| `ALLOWED_HOSTS` | Dominio de producción de Django |

3. El archivo `vercel.json` ya configura el routing automáticamente:
   - `/api/*` → FastAPI backend
   - `/health` → Health check del backend
   - `/static/*` → Archivos estáticos
   - `/*` → Django frontend

## 📌 Endpoints API

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/v1/auth/register` | Registrar nuevo usuario |
| `POST` | `/api/v1/auth/login` | Iniciar sesión (obtener JWT) |
| `GET`  | `/api/v1/auth/me` | Perfil del usuario autenticado |
| `POST` | `/api/v1/analyze-posture` | Analizar frame de cámara (Base64) |
| `GET`  | `/api/v1/posture-stats` | Estadísticas acumuladas de postura |
| `GET`  | `/health` | Estado de la API y base de datos |

## 📦 Commits del Proyecto

```
1. init: estructura base django frontend y fastapi backend
2. feat: modulo de autenticacion de usuario y control de acceso
3. feat: carga e inferencia del modelo preentrenado en fastapi
4. docs: esquemas pydantic y documentacion de endpoints en swagger
5. feat: interfaz ui en django y captura de stream de camara en js
6. feat: integracion http entre cliente django y servidor fastapi
7. fix: optimizacion de respuesta, manejo de errores y ui polish
8. deploy: configuracion vercel.json y pruebas finales de produccion
```

## 📄 Licencia

MIT License — [LuisOrCo/Posture-Notre-Dame](https://github.com/LuisOrCo/Posture-Notre-Dame)
