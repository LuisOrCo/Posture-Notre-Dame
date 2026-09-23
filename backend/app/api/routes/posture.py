from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.schemas.posture import (
    PostureRequest,
    PostureResponse,
    PostureStatsResponse,
)
from app.services.posture_analyzer import (
    process_posture_metric,
    get_posture_stats,
)
from app.core.security import decode_access_token
from app.services.auth_service import get_user_by_username

router = APIRouter()

oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,
)


def get_optional_user(token: Optional[str] = Depends(oauth2_scheme_optional)) -> Optional[dict]:
    """
    Dependencia opcional para asociar las evaluaciones de postura al usuario si proporciona un token JWT.
    """
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload:
        return None
    username = payload.get("sub")
    if not username:
        return None
    user = get_user_by_username(username)
    if user:
        return user
    return {"username": username}



@router.post(
    "/analyze-posture",
    response_model=PostureResponse,
    status_code=status.HTTP_200_OK,
    summary="Registrar y analizar postura con MediaPipe Pose",
    description="Recibe métricas biomecánicas inferidas en tiempo real con MediaPipe Pose o captura en Base64, calcula el estado y lo registra en MongoDB.",
    responses={
        200: {
            "description": "Análisis postural procesado correctamente.",
            "content": {
                "application/json": {
                    "example": {
                        "posture": "good",
                        "angle": 12.5,
                        "message": "Postura adecuada. Mantén la alineación ergonómica.",
                    }
                }
            },
        },
        400: {"description": "Datos de postura inválidos."},
        500: {"description": "Error interno al procesar métricas."},
    },
)
def analyze_posture_endpoint(
    request: PostureRequest,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """
    Registrar y evaluar postura:
    - **angle**: Ángulo en grados inferido por MediaPipe Pose.
    - **posture**: 'good' o 'bad'.
    - **image**: (Opcional) Captura Base64.
    """
    try:
        username = current_user["username"] if current_user else None
        result = process_posture_metric(
            angle=request.angle,
            posture=request.posture,
            image_base64=request.image,
            message=request.message,
            username=username,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en el procesamiento: {str(e)}",
        )


@router.get(
    "/posture-stats",
    response_model=PostureStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener estadísticas acumuladas de tiempo en buena vs. mala postura",
    description="Calcula y retorna el total de muestras registradas, recuento de buena/mala postura y porcentajes acumulados de ergonomía para el usuario actual o globales.",
    responses={
        200: {
            "description": "Estadísticas acumuladas generadas exitosamente.",
            "content": {
                "application/json": {
                    "example": {
                        "total_samples": 100,
                        "good_posture_count": 80,
                        "bad_posture_count": 20,
                        "good_percentage": 80.0,
                        "bad_percentage": 20.0,
                    }
                }
            },
        }
    },
)
def get_posture_stats_endpoint(
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """
    Obtener resumen de postura acumulada:
    - Retorna métricas de tiempo y porcentaje de postura adecuada frente al computador.
    """
    username = current_user["username"] if current_user else None
    stats = get_posture_stats(username=username)
    return stats
