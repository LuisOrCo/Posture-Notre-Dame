from datetime import datetime, timezone
from typing import Optional
from app.database import users_collection
from app.core.security import hash_password, verify_password
from app.schemas.auth import UserCreate, UserLogin


def register_user(user_data: UserCreate) -> dict:
    existing_user = users_collection.find_one({
        "$or": [
            {"username": user_data.username},
            {"email": user_data.email},
        ]
    })
    if existing_user:
        if existing_user.get("username") == user_data.username:
            raise ValueError("El nombre de usuario ya está registrado.")
        raise ValueError("El correo electrónico ya está registrado.")

    hashed_pwd = hash_password(user_data.password)
    now = datetime.now(timezone.utc)

    user_doc = {
        "username": user_data.username,
        "email": user_data.email,
        "hashed_password": hashed_pwd,
        "created_at": now,
    }

    result = users_collection.insert_one(user_doc)
    
    return {
        "id": str(result.inserted_id),
        "username": user_data.username,
        "email": user_data.email,
        "created_at": now,
    }


def authenticate_user(user_data: UserLogin) -> Optional[dict]:
    user = users_collection.find_one({"username": user_data.username})
    if not user:
        return None
    if not verify_password(user_data.password, user.get("hashed_password", "")):
        return None
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "created_at": user.get("created_at"),
    }


def get_user_by_username(username: str) -> Optional[dict]:
    user = users_collection.find_one({"username": username})
    if not user:
        return None
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "created_at": user.get("created_at"),
    }
