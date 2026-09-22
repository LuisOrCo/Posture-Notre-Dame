from fastapi import FastAPI

app = FastAPI(
    title="Sistema de Monitoreo Ergonómico",
    description="API para autenticación y análisis de postura laboral",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "API del Sistema de Monitoreo Ergonómico funcionando"
    }   