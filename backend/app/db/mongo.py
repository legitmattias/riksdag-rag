# backend/app/db/mongo.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "riksdagen")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def get_db():
    return db
