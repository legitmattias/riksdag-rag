# pipeline/parse_json_to_mongo.py

import os
import json
import re
import argparse
from bs4 import BeautifulSoup
from pymongo import MongoClient
from tqdm import tqdm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.join(BASE_DIR, "raw")
DEBUG_OUTPUT_DIR = os.path.join(BASE_DIR, "debug")

client = MongoClient("mongodb://localhost:27017/")
db = client.riksdagen
collection = db.speeches

DEBUG_FILES = {'ha091.json', 'ha0926.json', 'ha0939.json', 'ha0944.json', 'ha0973.json', 'ha0986.json', 'ha09121.json', 'ha0950.json', 'ha0994.json', 'ha0962.json'}

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

    # Concatenate digits that are split by spaces
    text = re.sub(r"(\d+)(?=\s+(\d+))+(\s|$)", r"\1", text)  # Merge multi-part numbers

    # Remove space after § (fix formatting for clauses)
    text = re.sub(r"§\s(\d)", r"§\1", text)  # Remove space after § symbol before clause number

    # Handle special characters:
    text = text.replace("\u2212", "-")             # Replace Minus Sign (U+2212) with regular hyphen
    text = text.replace("\u200B", "")          # Remove Zero Width Space (U+200B)
    text = text.replace("\uF0B7", " ")         # Replace Unknown Character (U+F0B7) with space (or remove)
       
    return text

def process_file(file_path, debug=False):
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

    if debug and os.path.basename(file_path) in DEBUG_FILES:
        os.makedirs(DEBUG_OUTPUT_DIR, exist_ok=True)  # Create debug folder if debug is enabled
        debug_path = os.path.join(DEBUG_OUTPUT_DIR, os.path.basename(file_path) + ".parsed.json")
        with open(debug_path, 'w', encoding='utf-8') as out:
            json.dump({
                "doc": doc,
            }, out, ensure_ascii=False, indent=2)

    # Insert data into MongoDB
    collection.update_one({"dok_id": doc["dok_id"]}, {"$set": doc}, upsert=True)

def main(debug=False):
    files = [f for f in os.listdir(RAW_DATA_DIR) if f.endswith(".json")]
    for file_name in tqdm(files, desc="Parsing files"):
        full_path = os.path.join(RAW_DATA_DIR, file_name)
        process_file(full_path, debug)

    print("✅ Done. Speeches loaded into MongoDB.")

if __name__ == "__main__":
    # Add argument parser for --debug flag
    parser = argparse.ArgumentParser(description="Parse protocol data and load into MongoDB.")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode to output parsed data to the debug folder.")
    args = parser.parse_args()

    # Run main function with debug flag
    main(debug=args.debug)
