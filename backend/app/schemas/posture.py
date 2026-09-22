from typing import Optional
from pydantic import BaseModel, Field


class PostureRequest(BaseModel):
    image: str = Field(
        ...,
        description="Imagen codificada en Base64 enviada desde el cliente web",
    )


class PostureResponse(BaseModel):
    posture: str = Field(
        ...,
        description="Estado ergonómico de la postura: 'good' o 'bad'",
        example="good",
    )
    angle: float = Field(
        ...,
        description="Ángulo de inclinación del cuello/hombros en grados",
        example=15.2,
    )
    message: Optional[str] = Field(
        None,
        description="Mensaje descriptivo sobre la evaluación postural",
    )


class PostureStatsResponse(BaseModel):
    total_samples: int = Field(..., description="Total de evaluaciones registradas")
    good_posture_count: int = Field(..., description="Cantidad de registros con buena postura")
    bad_posture_count: int = Field(..., description="Cantidad de registros con mala postura")
    good_percentage: float = Field(..., description="Porcentaje de tiempo/muestras en buena postura")
    bad_percentage: float = Field(..., description="Porcentaje de tiempo/muestras en mala postura")
