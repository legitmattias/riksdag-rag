import os
import json
import re
from bs4 import BeautifulSoup
from tqdm import tqdm

# Neutral speakers without party affiliation
NEUTRAL_SPEAKERS = [
    "TALMANNEN",
    "ANDRE VICE TALMANNEN",
    "TREDJE VICE TALMANNEN",
    "HANS MAJESTÄT KONUNGEN",
]

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.join(BASE_DIR, "./raw")
PARSED_DATA_DIR = os.path.join(BASE_DIR, "./data/test")
os.makedirs(PARSED_DATA_DIR, exist_ok=True)


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


def extract_clauses(cleaned_text):
    # Extract numbered clauses based on "§" marker
    header_pattern = r"\u00a7\s*(\d+)\s+([^\n\u00a7]{4,})"
    matches = list(re.finditer(header_pattern, cleaned_text))
    clauses = []
    seen_clause_numbers = set()

    for i, match in enumerate(matches):
        clause_number = int(match.group(1))
        clause_title_candidate = match.group(2).strip()
        if clause_number in seen_clause_numbers:
            continue
        seen_clause_numbers.add(clause_number)
        # Extract clause body between this and next match
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(cleaned_text)
        clause_content = cleaned_text[start:end].strip()
        # Ensure clause body gets a marker if not present
        if "<<END_OF_TITLE>>" not in clause_content:
            clause_content = re.sub(
                r"(Anf\.\s*\d+\s+)", r"<<END_OF_TITLE>>\1", clause_content, count=1
            )
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


def extract_speeches(clause_title, clause_content):
    # Extract speeches (Anf.) using regex matching
    speech_pattern = (
        r"(?i)Anf\.\s*(\d+)\s+"  # speech number
        r"([A-ZÅÄÖÉÜ][^:(\n]+?)"  # speaker name or role
        r"(?:\s+\((\w+)\))?"  # optional party
        r"(?:\s+\w+)*:"  # optional trailing tag
    )
    full_text = (
        (clause_title + "\n" + clause_content).replace("<<END_OF_TITLE>>", "").strip()
    )
    speeches = []
    matches = list(re.finditer(speech_pattern, full_text))
    for i, match in enumerate(matches):
        # Get speech boundaries from match positions
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)
        speech_text = full_text[start:end].strip()
        if "<<END_OF_SPEECH>>" in speech_text:
            speech_text = speech_text.split("<<END_OF_SPEECH>>")[0].strip()
        speech_text = speech_text.replace("<<END_OF_SPEECH>>", "").strip()
        speech_number = int(match.group(1))
        speaker = match.group(2).strip().upper()
        party = match.group(3) or ""
        if speaker in NEUTRAL_SPEAKERS:
            party = ""
        speeches.append(
            {
                "speech_number": speech_number,
                "speaker": speaker,
                "party": party,
                "text": speech_text,
            }
        )
    return speeches


def process_files():
    # Main processing loop for all JSON files
    speeches = []
    protocols = []
    files = [f for f in os.listdir(RAW_DATA_DIR) if f.endswith(".json")]
    for file_name in tqdm(files, desc="Parsing files"):
        with open(os.path.join(RAW_DATA_DIR, file_name), encoding="utf-8") as f:
            data = json.load(f)
        dokument = data.get("dokumentstatus", {}).get("dokument", {})
        if not dokument:
            continue
        pdf_info = data.get("dokumentstatus", {}).get("dokbilaga", {}).get("bilaga", {})
        raw_date = dokument.get("datum")
        parsed_date = raw_date.split(" ")[0] if raw_date else None
        # Extract general metadata for each protocol
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
        cleaned_text = clean_html(dokument.get("html", ""))
        clauses = extract_clauses(cleaned_text)
        clause_info = [{"number": n, "title": t} for n, t, _ in clauses]
        all_clause_speeches = []
        # Collect all speeches per clause
        for clause_number, clause_title, clause_content in clauses:
            for speech in extract_speeches(clause_title, clause_content):
                all_clause_speeches.append(
                    {
                        **base_meta,
                        "clause_number": clause_number,
                        "clause_title": clause_title,
                        **speech,
                    }
                )
        speeches.extend(all_clause_speeches)
        # Store protocol metadata separately
        protocols.append(
            {
                "document_id": base_meta["document_id"],
                "title": base_meta["title"],
                "parliament_year": base_meta["parliament_year"],
                "date": base_meta["date"],
                "num_clauses": len(clauses),
                "num_speeches": len(all_clause_speeches),
                "clauses": clause_info,
            }
        )
    return protocols, speeches


if __name__ == "__main__":
    # Entry point: save parsed protocols and speeches as JSON
    protocols, speeches = process_files()
    with open(
        os.path.join(PARSED_DATA_DIR, "protocols.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(protocols, f, ensure_ascii=False, indent=2)
    with open(
        os.path.join(PARSED_DATA_DIR, "speeches.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(speeches, f, ensure_ascii=False, indent=2)
    print("Parsing complete. Files saved in /data.")
