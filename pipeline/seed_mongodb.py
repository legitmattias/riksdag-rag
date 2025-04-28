import os
import json
from pymongo import MongoClient
from tqdm import tqdm
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables (.env file in backend)
env_path = Path(__file__).resolve().parents[1] / "backend" / ".env"
load_dotenv(dotenv_path=env_path)

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARSED_DATA_DIR = os.path.join(BASE_DIR, "./data")

# Load parsed data files
with open(os.path.join(PARSED_DATA_DIR, "protocols.json"), encoding="utf-8") as f:
    protocols = json.load(f)
with open(os.path.join(PARSED_DATA_DIR, "speeches.json"), encoding="utf-8") as f:
    speeches = json.load(f)

# Set up MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
protocols_collection = db.protocols
speeches_collection = db.speeches

# Clear existing collections
protocols_collection.delete_many({})
speeches_collection.delete_many({})

# Insert protocols
print("Seeding protocols...")
for protocol in tqdm(protocols):
    protocols_collection.insert_one(protocol)

# Insert speeches
print("Seeding speeches...")
for speech in tqdm(speeches):
    speeches_collection.insert_one(speech)

print("\nSeeding complete. MongoDB is now populated.")
