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
)
def analyze_posture_endpoint(
    request: PostureRequest,
    current_user: Optional[dict] = Depends(get_optional_user),
):
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
    summary="Obtener estadísticas acumuladas de tiempo/muestras en buena vs. mala postura",
)
def get_posture_stats_endpoint(
    current_user: Optional[dict] = Depends(get_optional_user),
):
    username = current_user["username"] if current_user else None
    stats = get_posture_stats(username=username)
    return stats
