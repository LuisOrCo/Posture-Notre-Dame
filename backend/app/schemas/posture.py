from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class PostureRequest(BaseModel):
    image: str = Field(
        ...,
        description="Imagen de la webcam en formato Base64 (data:image/jpeg;base64,... o texto plano base64)",
        examples=["data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/..."],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "image": "data:image/jpeg;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
            }
        }
    )


class PostureResponse(BaseModel):
    posture: str = Field(
        ...,
        description="Estado postural evaluado ('good' para postura ergonómica correcta, 'bad' para inclinación excesiva)",
        examples=["good"],
    )
    angle: float = Field(
        ...,
        description="Ángulo de inclinación del cuello/hombros calculado en grados respecto a la vertical",
        examples=[12.5],
    )
    message: Optional[str] = Field(
        None,
        description="Recomendación o diagnóstico descriptivo para el usuario teletrabajador",
        examples=["Postura adecuada. Mantén la alineación ergonómica."],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "posture": "good",
                "angle": 12.5,
                "message": "Postura adecuada. Mantén la alineación ergonómica.",
            }
        }
    )


class PostureStatsResponse(BaseModel):
    total_samples: int = Field(
        ...,
        description="Total de frames o evaluaciones registradas para el usuario",
        examples=[100],
    )
    good_posture_count: int = Field(
        ...,
        description="Cantidad total de evaluaciones en buena postura",
        examples=[80],
    )
    bad_posture_count: int = Field(
        ...,
        description="Cantidad total de evaluaciones en mala postura",
        examples=[20],
    )
    good_percentage: float = Field(
        ...,
        description="Porcentaje acumulado de tiempo/muestras en buena postura",
        examples=[80.0],
    )
    bad_percentage: float = Field(
        ...,
        description="Porcentaje acumulado de tiempo/muestras en mala postura",
        examples=[20.0],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_samples": 100,
                "good_posture_count": 80,
                "bad_posture_count": 20,
                "good_percentage": 80.0,
                "bad_percentage": 20.0,
            }
        }
    )
