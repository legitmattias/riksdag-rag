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
speech_collection = db.speeches
protocols_collection = db.protocols

# Specify files to include in debug output
""" DEBUG_FILES = {'ha091.json', 'ha0926.json', 'ha0939.json', 'ha0944.json', 'ha0973.json', 'ha0986.json', 'ha09121.json', 'hb0950.json', 'hb0994.json', 'hb0962.json', "hb0939.json"} """
DEBUG_FILES = {"ha09100.json"}
# DEBUG_FILES = {"hb0939.json"}

# Summaries for debug print
summaries = []

# Neutral speakers without party affiliation
NEUTRAL_SPEAKERS = [
    "TALMANNEN",
    "ANDRE VICE TALMANNEN",
    "TREDJE VICE TALMANNEN",
    "HANS MAJESTÄT KONUNGEN",
]


# Clean and normalize raw HTML content and inject parsing markers
def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator="\n")

    # Remove all text after the known footer (prevents duplicated clause junk)
    text = re.split(r"Sammanträdet leddes(?:.|\n)*?(?=Vid protokollet|Tryck:)", text)[0]

    # DEBUG: Print last 5000 characters for manual inspection
    # print("\n[DEBUG] Raw text with escape characters:\n", repr(text[:15000]), "\n...\n")

    # Insert a marker after clause title if followed by multiple newlines
    text = re.sub(
        r"(§\s*\d+\s+(?:\(forts\.\)\s*)?[^\n]+)(\n{2,})", r"\1 <<END_OF_TITLE>>\2", text
    )

    # Insert marker for speeches that should stop at 'Ajournering'
    text = re.sub(
        r"\n\s*Ajournering\s*\n", "\n<<END_OF_SPEECH>>\n", text, flags=re.IGNORECASE
    )

    # Normalize newlines and whitespace characters
    text = re.sub(r"\n+", "\n", text)
    text = text.replace("\xa0", " ").replace("\u2011", "-")
    text = re.sub(r"\u00AD", "", text)
    text = re.sub(r"\u2013|\u2014|\u2012|\u2015|\u002D", "-", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"(\d+)(?=\s+(\d+))+(\s|$)", r"\1", text)
    text = text.replace("\u2212", "-").replace("\u200b", "").replace("\uf0b7", " ")

    # Normalize left and right single quotation marks to straight apostrophes
    text = text.replace("\u2018", "'").replace("\u2019", "'")

    # Ensure that 'Anf.' always starts on a new line to break clause title greediness
    text = re.sub(r"(?<!\n)(Anf\.\s*\d+\s+)", r"\n\1", text)

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

        # Get the content between this clause and the next one
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(cleaned_text)
        clause_content = cleaned_text[start:end].strip()

        # Fallback: If there's no <<END_OF_TITLE>> marker, try to insert it before the first Anf.
        if "<<END_OF_TITLE>>" not in clause_content:
            clause_content = re.sub(
                r"(Anf\.\s*\d+\s+)",  # Before first speech marker
                r"<<END_OF_TITLE>>\1",
                clause_content,
                count=1,
            )

        # Now combine clause title and content for final split
        full_clause_text = clause_title_candidate + "\n" + clause_content

        if "<<END_OF_TITLE>>" in full_clause_text:
            clause_title, clause_content = full_clause_text.split("<<END_OF_TITLE>>", 1)
            clause_title = clause_title.strip()
            clause_content = clause_content.strip()
        else:
            clause_title = clause_title_candidate
            clause_content = clause_content.strip()

        clauses.append((clause_number, clause_title, clause_content))

    return clauses


# Extract individual speeches (Anf.) within each clause
def extract_speeches(clause_title, clause_content):
    # Regex to match either a standard speaker (with party) or special roles (without party)
    # Examples:
    #   Anf. 55 JESSICA ROSENCRANTZ (M):
    #   Anf. 56 ANDRE VICE TALMANNEN:
    speech_pattern = (
        r"(?i)"  # Case-insensitive for entire pattern
        r"Anf\.\s*(\d+)\s+"  # Group 1: speech number
        r"([A-ZÅÄÖÉÜ][^:(\n]+?)"  # Group 2: speaker name or role
        r"(?:\s+\((\w+)\))?"  # Group 3 (optional): party in parentheses
        r"(?:\s+\w+)*:"  # Optional trailing tags like "replik:"
    )

    # Combine clause title and content, then clean markers
    full_text = (
        (clause_title + "\n" + clause_content).replace("<<END_OF_TITLE>>", "").strip()
    )

    speeches = []
    matches = list(re.finditer(speech_pattern, full_text))

    for i, match in enumerate(matches):
        # Get start and end bounds for this speech's content
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)
        speech_text = full_text[start:end].strip()

        # Stop at end marker if present
        if "<<END_OF_SPEECH>>" in speech_text:
            speech_text = speech_text.split("<<END_OF_SPEECH>>")[0].strip()

        # Clean any leftover marker
        speech_text = speech_text.replace("<<END_OF_SPEECH>>", "").strip()

        # Extract parsed values from the match
        speech_number = int(match.group(1))
        speaker = match.group(2).strip().upper()  # Normalize all speaker names
        party = match.group(3) or ""  # Empty string if no party present

        # Remove party if the speaker is a neutral role
        if speaker in NEUTRAL_SPEAKERS:
            party = ""

        # Add to speech list
        speeches.append(
            {
                "speech_number": speech_number,
                "speaker": speaker,
                "party": party,
                "text": speech_text,
            }
        )

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
    raw_date = dokument.get("datum")
    parsed_date = (
        raw_date.split(" ")[0] if raw_date else None
    )  # Only date - no timestamp

    base_meta = {
        "document_id": dokument.get("dok_id"),
        "hangar_id": dokument.get("hangar_id"),
        "parliament_year": dokument.get("rm"),
        "date": parsed_date,
        "title": dokument.get("titel"),
        "document_type": dokument.get("doktyp"),
        "type": dokument.get("typ"),
        "type_label": dokument.get("typrubrik"),
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

    # Remove old entries for this protocol
    protocols_collection.delete_one({"document_id": dokument.get("dok_id")})

    # Delete all previous speeches for this document once
    speech_collection.delete_many({"document_id": dokument.get("dok_id")})

    for clause_number, clause_title, clause_content in clauses:
        speeches = extract_speeches(clause_title, clause_content)
        for speech in speeches:
            speech_doc = {
                **base_meta,
                "clause_number": clause_number,
                "clause_title": clause_title,
                **speech,
            }
            speech_collection.insert_one(speech_doc)  # Save to MongoDB
            all_speeches.append(speech_doc)

    clause_info = [{"number": num, "title": title} for num, title, _ in clauses]

    protocol_doc = {
        "document_id": dokument.get("dok_id"),
        "title": dokument.get("titel"),
        "parliament_year": dokument.get("rm"),
        "date": parsed_date,
        "num_clauses": len(clauses),
        "num_speeches": len(all_speeches),
        "clauses": clause_info,
    }

    # Store protocol metadata
    protocols_collection.insert_one(protocol_doc)

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
                    # "sample_clauses": clauses,
                    "sample_speeches": all_speeches,
                },
                out,
                ensure_ascii=False,
                indent=2,
            )

    # Summary print for every file (even outside debug mode)
    summaries.append(
        {
            "file": os.path.basename(file_path),
            "clauses": len(clauses),
            "speeches": len(all_speeches),
        }
    )


# Run parsing across all .json protocol files
def main(debug=False):
    files = [f for f in os.listdir(RAW_DATA_DIR) if f.endswith(".json")]
    for file_name in tqdm(files, desc="Parsing files"):
        full_path = os.path.join(RAW_DATA_DIR, file_name)
        process_file(full_path, debug)
    print("✅ Done. Speeches extracted and stored in MongoDB.")
    print("\nParsing Summary:")
    for summary in summaries:
        print(
            f"{summary['file']} → {summary['clauses']} clauses, {summary['speeches']} speeches"
        )


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
