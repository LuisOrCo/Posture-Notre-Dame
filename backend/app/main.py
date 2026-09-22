from fastapi import FastAPI

from app.database import client
from app.api.routes import auth, posture
from app.core.config import TAGS_METADATA


app = FastAPI(
    title="API de Sistema de Monitoreo de Ergonomía Laboral",
    description="""
# 🧘 Sistema de Monitoreo de Ergonomía Laboral
API RESTful construida con **FastAPI**, **MediaPipe Pose Estimation** y **MongoDB** para prevenir lesiones posturales en jornadas de teletrabajo.

## 🚀 Funcionalidades Principales:
* **Autenticación Segura**: Registro e inicio de sesión con contraseñas encriptadas con `bcrypt` y firma de tokens `JWT`.
* **Análisis Postural**: Inferencia mediante **MediaPipe Pose** para calcular el ángulo de inclinación de cuello y hombros en grados y detectar estados ergonómicos (`good` o `bad`).
* **Estadísticas en Tiempo Real**: Reporte del tiempo acumulado y porcentaje de postura ergonómica correcta vs. incorrecta.

## 📌 Documentación de Endpoints:
* **`POST /api/v1/analyze-posture`**: Recibe un frame de la cámara web (Base64) y retorna `{"posture": "bad|good", "angle": 15.2}`.
* **`GET /api/v1/posture-stats`**: Retorna el resumen del tiempo y porcentaje acumulado en buena vs. mala postura.
""",
    version="1.0.0",
    openapi_tags=TAGS_METADATA,
    contact={
        "name": "Equipo de Desarrollo ErgoMonitor",
        "url": "https://github.com/LuisOrCo/Posture-Notre-Dame",
    },
    license_info={
        "name": "MIT License",
    },
)

# Inclusión de routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(posture.router, prefix="/api/v1", tags=["posture"])


@app.get("/", tags=["health"], summary="Verificar estado de la API")
def root():
    return {
        "message": "API del Sistema de Monitoreo Ergonómico funcionando correctamente",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["health"], summary="Verificar salud de la base de datos MongoDB")
def health_check():
    try:
        client.admin.command("ping")
        return {
            "status": "ok",
            "database": "MongoDB conectada exitosamente",
        }
    except Exception as e:
        return {
            "status": "error",
            "database": str(e),
        }