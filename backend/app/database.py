import os
from pymongo import MongoClient
from app.core.config import MONGODB_URL, MONGODB_DATABASE


# Conexión a MongoDB con timeout de 5s para evitar cuelgues en serverless
client = MongoClient(
    MONGODB_URL,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=5000,
    socketTimeoutMS=5000,
)

database = client[MONGODB_DATABASE]

users_collection = database["users"]
posture_logs_collection = database["posture_logs"]