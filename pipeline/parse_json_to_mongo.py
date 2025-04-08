# pipeline/parse_json_to_mongo.py

import os
import json
import re
import unicodedata
from bs4 import BeautifulSoup
from pymongo import MongoClient
from tqdm import tqdm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.join(BASE_DIR, "raw")
DEBUG_OUTPUT_DIR = os.path.join(BASE_DIR, "debug")
os.makedirs(DEBUG_OUTPUT_DIR, exist_ok=True)
DEBUG_FILES = {'ha091.json', 'ha0910.json'}

client = MongoClient("mongodb://localhost:27017/")
db = client.riksdagen
collection = db.speeches

def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator="\n")
    
    # Clean the text (remove unwanted characters and normalize)
    text = re.sub(r"\n+", "\n", text)           # Replace multiple newlines with one
    text = text.replace("\xa0", " ")            # Replace non-breaking space with regular space
    text = text.replace("\u2011", "-")          # Replace non-breaking hyphen (U+2011) with regular hyphen
    text = re.sub(r"\u00AD", "", text)          # Remove Soft Hyphen (U+00AD)
    
    # Handle all dash characters (replace various dashes with regular hyphen)
    text = re.sub(r"\u2013|\u2014|\u2012|\u2015|\u002D", "-", text)  # Replace various dashes with regular hyphen
    
    # Normalize white spaces (condense multiple spaces into one)
    text = re.sub(r"\s+", " ", text).strip()

    text = clean_numbers(text)
    
    return text

def clean_numbers(text):
    # Concatenate digits that are split by spaces
    text = re.sub(r"(\d) (\d+)(?=\s|$)", r"\1\2", text)  # Combine numbers split by single space
    text = re.sub(r"(\d+)(?=\s+(\d+))+(\s|$)", r"\1", text)  # Merge multi-part numbers
    return text

def get_suspicious_chars(text):
  return [
    {"char": c, "code": f"U+{ord(c):04X}", "name": unicodedata.name(c, "UNKNOWN")}
    for c in text
    if (
      ord(c) < 32 and c not in '\n\t'  # ASCII control chars
      or unicodedata.category(c).startswith("C")  # other control chars
      or unicodedata.category(c) in {"Zl", "Zp"}  # line/paragraph separators
      or c in {'\u00A0', '\u200B', '\u200C', '\u200D', '\uFEFF'}
    )
  ]

def process_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    dokument = data.get("dokumentstatus", {}).get("dokument", {})
    if not dokument:
        return

    cleaned_text = clean_html(dokument.get("html", ""))

    doc = {
        "hangar_id": dokument.get("hangar_id"),
        "dok_id": dokument.get("dok_id"),
        "rm": dokument.get("rm"),
        "nummer": dokument.get("nummer"),
        "datum": dokument.get("datum"),
        "titel": dokument.get("titel"),
        "doktyp": dokument.get("doktyp"),
        "typ": dokument.get("typ"),
        "typ_rubrik": dokument.get("typrubrik"),
        "text": cleaned_text,
        "source_file": os.path.basename(file_path),
    }

    if os.path.basename(file_path) in DEBUG_FILES:
      debug_path = os.path.join(DEBUG_OUTPUT_DIR, os.path.basename(file_path) + ".parsed.json")
      with open(debug_path, 'w', encoding='utf-8') as out:
          json.dump({
              "doc": doc,
              "suspicious_chars": get_suspicious_chars(cleaned_text)
          }, out, ensure_ascii=False, indent=2)


    collection.update_one({"dok_id": doc["dok_id"]}, {"$set": doc}, upsert=True)


if __name__ == "__main__":
    files = [f for f in os.listdir(RAW_DATA_DIR) if f.endswith(".json")]
    for file_name in tqdm(files, desc="Parsing files"):
        full_path = os.path.join(RAW_DATA_DIR, file_name)
        process_file(full_path)

    print("✅ Done. Speeches loaded into MongoDB.")
