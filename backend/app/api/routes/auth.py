from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.schemas.auth import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
)
from app.services.auth_service import (
    register_user,
    authenticate_user,
    get_user_by_username,
)
from app.core.security import create_access_token, decode_access_token

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Dependencia para obtener el usuario autenticado a partir del token Bearer JWT.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado. Token ausente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username: str = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: falta subject.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_user_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario teletrabajador",
    description="Crea una nueva cuenta de usuario registrando las credenciales en MongoDB y hasheando la contraseña con bcrypt.",
    responses={
        201: {"description": "Usuario registrado exitosamente en la plataforma."},
        400: {"description": "El nombre de usuario o el correo electrónico ya se encuentran registrados."},
    },
)
def register(user_data: UserCreate):
    """
    Registrar nuevo usuario:
    - **username**: Nombre de usuario único.
    - **email**: Correo electrónico del usuario.
    - **password**: Contraseña de al menos 6 caracteres.
    """
    try:
        user = register_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=Token,
    summary="Iniciar sesión y obtener JWT token de acceso",
    description="Autentica las credenciales de usuario y retorna un JSON Web Token (JWT) válido para autorizar las solicitudes.",
    responses={
        200: {"description": "Autenticación exitosa y emisión del token JWT."},
        401: {"description": "Credenciales inválidas (usuario o contraseña incorrectos)."},
    },
)
def login(user_data: UserLogin):
    """
    Iniciar sesión con credenciales:
    - **username**: Nombre de usuario.
    - **password**: Contraseña asociada.
    """
    user = authenticate_user(user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obtener perfil del usuario autenticado",
    description="Retorna la información del usuario autenticado actual basándose en la cabecera HTTP Bearer Token.",
    responses={
        200: {"description": "Perfil del usuario devuelto exitosamente."},
        401: {"description": "Token de autenticación inválido, ausente o expirado."},
    },
)
def read_users_me(current_user: dict = Depends(get_current_user)):
    """
    Obtener perfil actual del usuario autenticado. Requiere cabecera: `Authorization: Bearer <token>`
    """
    return current_user
