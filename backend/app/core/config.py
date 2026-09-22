import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-in-production-1234567890")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
)

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DATABASE = os.getenv(
    "MONGODB_DATABASE",
    "sistema_ergonomia",
)

TAGS_METADATA = [
    {
        "name": "auth",
        "description": "Endpoints de autenticación de usuarios, registro, emisión de tokens JWT y consulta de perfil.",
    },
    {
        "name": "posture",
        "description": "Endpoints de inferencia en tiempo real con MediaPipe Pose y estadísticas acumuladas de ergonomía laboral.",
    },
]