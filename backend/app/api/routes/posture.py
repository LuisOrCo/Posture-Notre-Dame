from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.schemas.posture import (
    PostureRequest,
    PostureResponse,
    PostureStatsResponse,
)
from app.services.posture_analyzer import (
    analyze_posture,
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
    return get_user_by_username(username)


@router.post(
    "/analyze-posture",
    response_model=PostureResponse,
    status_code=status.HTTP_200_OK,
    summary="Analizar frame de cámara e inferir postura laboral con MediaPipe Pose",
    description="Procesa una captura de webcam en Base64, extrae los puntos de pose corporal con MediaPipe Pose, calcula la inclinación del cuello/hombros en grados y determina el estado de la postura ('good' o 'bad').",
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
        400: {"description": "Error en la decodificación de la imagen Base64 enviada."},
        500: {"description": "Error en la inferencia del modelo MediaPipe o procesamiento interno."},
    },
)
def analyze_posture_endpoint(
    request: PostureRequest,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """
    Analizar frame de cámara:
    - **image**: Cadena Base64 representando la imagen capturada por la cámara del usuario.
    """
    try:
        username = current_user["username"] if current_user else None
        result = analyze_posture(request.image, username=username)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la inferencia del modelo: {str(e)}",
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
