from pymongo import MongoClient

from app.core.config import MONGODB_URL, MONGODB_DATABASE


client = MongoClient(MONGODB_URL)

database = client[MONGODB_DATABASE]

users_collection = database["users"]
posture_logs_collection = database["posture_logs"]