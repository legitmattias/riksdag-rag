# pipeline/parse_json_to_speeches.py

import os
import json
import re
import argparse
from bs4 import BeautifulSoup
from pymongo import MongoClient
from tqdm import tqdm

# Define base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.join(BASE_DIR, "raw")
DEBUG_OUTPUT_DIR = os.path.join(BASE_DIR, "debug")

# Set up MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client.riksdagen
collection = db.speeches

# Specify files to include in debug output
DEBUG_FILES = {'ha0939.json'}
""" DEBUG_FILES = {'ha091.json', 'ha0926.json', 'ha0939.json', 'ha0944.json', 'ha0973.json', 'ha0986.json', 'ha09121.json', 'ha0950.json', 'ha0994.json', 'ha0962.json'} """

summaries = []

# Clean and normalize raw HTML content and inject parsing markers
def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator="\n")

    # Remove all text after the known footer (prevents duplicated clause junk)
    text = re.split(r"Sammanträdet leddes(?:.|\n)*?(?=Vid protokollet|Tryck:)", text)[0]

    # DEBUG: Print last 5000 characters for manual inspection
    #print("\n[DEBUG] Raw text with escape characters:\n", repr(text[:15000]), "\n...\n")

    # Insert a marker after clause title if followed by multiple newlines
    text = re.sub(
        r"(§\s*\d+\s+(?:\(forts\.\)\s*)?[^\n]+)(\n{2,})",
        r"\1 <<END_OF_TITLE>>\2",
        text
    )

    # Insert marker for speeches that should stop at 'Ajournering'
    text = re.sub(r"\n\s*Ajournering\s*\n", "\n<<END_OF_SPEECH>>\n", text, flags=re.IGNORECASE)

    # Normalize newlines and whitespace characters
    text = re.sub(r"\n+", "\n", text)
    text = text.replace("\xa0", " ").replace("\u2011", "-")
    text = re.sub(r"\u00AD", "", text)
    text = re.sub(r"\u2013|\u2014|\u2012|\u2015|\u002D", "-", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"(\d+)(?=\s+(\d+))+(\s|$)", r"\1", text)
    text = text.replace("\u2212", "-").replace("\u200b", "").replace("\uf0b7", " ")

    return text

# Extract clauses based on '§' headers, with fallback for content edge cases
def extract_clauses(cleaned_text):
    header_pattern = r"§\s*(\d+)\s+([^\n§]{4,})"
    matches = list(re.finditer(header_pattern, cleaned_text))

    clauses = []
    seen_clause_numbers = set()

    for i, match in enumerate(matches):
        clause_number = int(match.group(1))
        clause_title_candidate = match.group(2).strip()

        if clause_number in seen_clause_numbers:
            continue  # Skip repeated clause numbers (usually footer junk)
        seen_clause_numbers.add(clause_number)

        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(cleaned_text)
        clause_content = cleaned_text[start:end].strip()

        # Combine title and content to allow for title/content marker split
        full_clause_text = clause_title_candidate + "\n" + clause_content

        if "<<END_OF_TITLE>>" in full_clause_text:
            clause_title, clause_content = full_clause_text.split("<<END_OF_TITLE>>", 1)
            clause_title = clause_title.strip()
            clause_content = clause_content.replace("<<END_OF_TITLE>>", "").strip()
        else:
            clause_title = clause_title_candidate
            clause_content = clause_content.strip()

        clauses.append((clause_number, clause_title, clause_content))

    return clauses

# Extract individual speeches (Anf.) within each clause
def extract_speeches(clause_title, clause_content):
    speech_pattern = (
        r"Anf\.\s*(\d+)\s+(.+?)\s+\((\w+)\)(?:\s+\w+)*:"  # Standard: Anf. 12 NAME (PARTY):
        r"|Anf\.\s*(\d+)\s+(?i:talmannen):"               # Special case: Anf. 23 TALMANNEN:
    )

    full_text = (clause_title + "\n" + clause_content).replace("<<END_OF_TITLE>>", "").strip()
    speeches = []
    matches = list(re.finditer(speech_pattern, full_text))

    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)
        speech_text = full_text[start:end].strip()

        if "<<END_OF_SPEECH>>" in speech_text:
            speech_text = speech_text.split("<<END_OF_SPEECH>>")[0].strip()

        if match.group(1):  # Standard format
            speech_number = int(match.group(1))
            speaker = match.group(2).strip()
            party = match.group(3)
        else:  # TALMANNEN format
            speech_number = int(match.group(4))
            speaker = "TALMANNEN"
            party = ""  # Neutral speaker — no party assigned

        speeches.append({
            "speech_number": speech_number,
            "speaker": speaker,
            "party": party,
            "text": speech_text
        })

    return speeches

# Process a single protocol file
def process_file(file_path, debug=False):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    dokument = data.get("dokumentstatus", {}).get("dokument", {})
    if not dokument:
        return  # Skip empty documents

    cleaned_text = clean_html(dokument.get("html", ""))
    pdf_info = data.get("dokumentstatus", {}).get("dokbilaga", {}).get("bilaga", {})

    # Build base metadata that applies to all speeches from this document
    base_meta = {
        "dok_id": dokument.get("dok_id"),
        "hangar_id": dokument.get("hangar_id"),
        "rm": dokument.get("rm"),
        "datum": dokument.get("datum"),
        "titel": dokument.get("titel"),
        "doktyp": dokument.get("doktyp"),
        "typ": dokument.get("typ"),
        "typ_rubrik": dokument.get("typrubrik"),
        "source": {
            "html": dokument.get("dokument_url_html"),
            "pdf": {
                "url": pdf_info.get("fil_url"),
                "filename": pdf_info.get("filnamn"),
                "filesize": pdf_info.get("filstorlek"),
                "filetype": pdf_info.get("filtyp"),
                "title": pdf_info.get("titel"),
            },
        },
    }

    all_speeches = []

    # Parse all clauses and extract any speeches from each
    clauses = extract_clauses(cleaned_text)
    for clause_number, clause_title, clause_content in clauses:
        speeches = extract_speeches(clause_title, clause_content)
        for speech in speeches:
            speech_doc = {
                **base_meta,
                "clause_number": clause_number,
                "clause_title": clause_title,
                **speech,
            }
            collection.insert_one(speech_doc)  # Save to MongoDB
            all_speeches.append(speech_doc)

    # If in debug mode, save a separate .json output with samples
    if debug and os.path.basename(file_path) in DEBUG_FILES:
        os.makedirs(DEBUG_OUTPUT_DIR, exist_ok=True)
        debug_path = os.path.join(
            DEBUG_OUTPUT_DIR, os.path.basename(file_path) + ".speeches.json"
        )
        with open(debug_path, "w", encoding="utf-8") as out:
            for speech in all_speeches:
                speech.pop("_id", None)  # Remove MongoDB metadata
            json.dump(
                {
                    "file": os.path.basename(file_path),
                    "total_clauses": len(clauses),
                    "total_speeches": len(all_speeches),
                    "sample_clauses": clauses,
                    "sample_speeches": all_speeches,
                },
                out,
                ensure_ascii=False,
                indent=2,
            )
    
    # Summary print for every file (even outside debug mode)
    summaries.append({
    "file": os.path.basename(file_path),
    "clauses": len(clauses),
    "speeches": len(all_speeches)
})

# Run parsing across all .json protocol files
def main(debug=False):
    files = [f for f in os.listdir(RAW_DATA_DIR) if f.endswith(".json")]
    for file_name in tqdm(files, desc="Parsing files"):
        full_path = os.path.join(RAW_DATA_DIR, file_name)
        process_file(full_path, debug)
    print("✅ Done. Speeches extracted and stored in MongoDB.")
    print("\nParsing Summary:")
    for summary in summaries:
      print(f"{summary['file']} → {summary['clauses']} clauses, {summary['speeches']} speeches")


# CLI entry point
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract speeches and store into MongoDB."
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode for output inspection."
    )
    args = parser.parse_args()
    main(debug=args.debug)
