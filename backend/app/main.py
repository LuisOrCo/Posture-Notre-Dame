from fastapi import FastAPI

from app.database import client
from app.api.routes import auth


app = FastAPI(
    title="Sistema de Monitoreo Ergonómico",
    description="API para autenticación y análisis de postura laboral",
    version="1.0.0",
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])



@app.get("/")
def root():
    return {
        "message": "API del Sistema de Monitoreo Ergonómico funcionando"
    }


@app.get("/health")
def health_check():
    try:
        client.admin.command("ping")

        return {
            "status": "ok",
            "database": "MongoDB conectada",
        }

    except Exception as e:
        return {
            "status": "error",
            "database": str(e),
        }