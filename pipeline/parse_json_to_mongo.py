# pipeline/parse_json_to_mongo.py

import os
import json
from bs4 import BeautifulSoup
from pymongo import MongoClient
from tqdm import tqdm

RAW_DATA_DIR = './raw'

client = MongoClient("mongodb://localhost:27017/")
db = client.riksdagen
collection = db.speeches

def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator="\n")

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    speeches = data.get("anforanden", {}).get("anforande", [])
    for speech in speeches:
        cleaned_text = clean_html(speech.get("anforandetext", ""))
        doc = {
            "id": speech.get("anforande_id"),
            "date": speech.get("dok_datum"),
            "speaker": speech.get("namn"),
            "party": speech.get("parti"),
            "title": speech.get("titel"),
            "text": cleaned_text,
            "source_file": os.path.basename(file_path),
            "intressent_id": speech.get("intressent_id")
        }
        collection.update_one({"id": doc["id"]}, {"$set": doc}, upsert=True)

if __name__ == "__main__":
    files = [f for f in os.listdir(RAW_DATA_DIR) if f.endswith('.json')]
    for file_name in tqdm(files, desc="Parsing files"):
        full_path = os.path.join(RAW_DATA_DIR, file_name)
        process_file(full_path)

    print("✅ Done. Speeches loaded into MongoDB.")
