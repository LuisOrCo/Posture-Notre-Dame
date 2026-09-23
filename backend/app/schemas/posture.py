from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class PostureRequest(BaseModel):
    image: Optional[str] = Field(
        None,
        description="Imagen de la webcam en formato Base64 (opcional)",
        examples=["data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/..."],
    )
    angle: Optional[float] = Field(
        None,
        description="Ángulo de inclinación en grados inferido por MediaPipe Pose en el cliente",
        examples=[12.5],
    )
    posture: Optional[str] = Field(
        None,
        description="Estado de postura determinado por MediaPipe Pose ('good' o 'bad')",
        examples=["good"],
    )
    message: Optional[str] = Field(
        None,
        description="Mensaje de retroalimentación ergonómica",
        examples=["Postura adecuada. Mantén la alineación ergonómica."],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "angle": 12.5,
                "posture": "good",
                "message": "Postura adecuada. Mantén la alineación ergonómica.",
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
