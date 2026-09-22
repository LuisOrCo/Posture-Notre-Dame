from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class UserCreate(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Nombre único de usuario en la plataforma",
        examples=["teletrabajador_01"],
    )
    email: str = Field(
        ...,
        min_length=5,
        description="Correo electrónico válido del usuario",
        examples=["usuario@empresa.com"],
    )
    password: str = Field(
        ...,
        min_length=6,
        description="Contraseña de acceso (mínimo 6 caracteres)",
        examples=["ClaveSegura123!"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "teletrabajador_01",
                "email": "usuario@empresa.com",
                "password": "ClaveSegura123!",
            }
        }
    )


class UserLogin(BaseModel):
    username: str = Field(
        ...,
        description="Nombre de usuario registrado",
        examples=["teletrabajador_01"],
    )
    password: str = Field(
        ...,
        description="Contraseña de acceso",
        examples=["ClaveSegura123!"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "teletrabajador_01",
                "password": "ClaveSegura123!",
            }
        }
    )


class UserResponse(BaseModel):
    id: str = Field(
        ...,
        description="Identificador único del usuario (MongoDB ObjectId)",
        examples=["650c1f77bcf86cd799439011"],
    )
    username: str = Field(
        ...,
        description="Nombre de usuario",
        examples=["teletrabajador_01"],
    )
    email: str = Field(
        ...,
        description="Correo electrónico",
        examples=["usuario@empresa.com"],
    )
    created_at: Optional[datetime] = Field(
        None,
        description="Fecha y hora de registro del usuario en formato UTC",
        examples=["2026-09-22T12:00:00Z"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "650c1f77bcf86cd799439011",
                "username": "teletrabajador_01",
                "email": "usuario@empresa.com",
                "created_at": "2026-09-22T12:00:00Z",
            }
        }
    )


class Token(BaseModel):
    access_token: str = Field(
        ...,
        description="Token de acceso JWT firmado",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    token_type: str = Field(
        "bearer",
        description="Tipo de token (Bearer Auth)",
        examples=["bearer"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c3VhcmlvMDAxIn0...",
                "token_type": "bearer",
            }
        }
    )


class TokenData(BaseModel):
    username: Optional[str] = Field(
        None,
        description="Nombre de usuario extraído del payload del token JWT",
        examples=["teletrabajador_01"],
    )
