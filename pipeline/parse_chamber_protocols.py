import os
import json
import re
from bs4 import BeautifulSoup, NavigableString
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
PARSED_DATA_DIR = os.path.join(BASE_DIR, "./data")
os.makedirs(PARSED_DATA_DIR, exist_ok=True)


def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")

    # Insert markers around <h1> elements that contain clause headers
    for h1 in soup.find_all("h1"):
        if "§" in h1.text:
            h1.insert_before(NavigableString("<<CLAUSE_TITLE_BLOCK_START>>\n"))
            h1.insert_after(NavigableString("\n<<CLAUSE_TITLE_BLOCK_END>>"))

    # Insert markers before <h2> elements containing speeches
    for h2 in soup.find_all("h2"):
        if "Anf." in h2.text:
            h2.insert_before(NavigableString("<<SPEECH_START>>\n"))

    # Convert full HTML content to plain text
    text = soup.get_text(separator="\n")

    # Remove text after protocol footer
    text = re.split(r"Sammanträdet leddes(?:.|\n)*?(?=Vid protokollet|Tryck:)", text)[0]

    # Add fallback marker between clause title and body based on § header followed by double newlines
    text = re.sub(
        r"(§\s*\d+\s+(?:\(forts\.\)\s*)?[^\n]+)(\n{2,})",
        r"\1 <<CLAUSE_TITLE_FALLBACK_BREAK>>\2",
        text,
    )

    # Insert marker to denote end of speech block
    text = re.sub(
        r"\n\s*Ajournering\s*\n", "\n<<END_OF_SPEECH>>\n", text, flags=re.IGNORECASE
    )

    # Normalize excessive newlines to single newlines
    text = re.sub(r"\n+", "\n", text)

    # Replace special characters and dashes with standard ones
    text = text.replace("\xa0", " ").replace("\u2011", "-")
    text = re.sub(r"\u00AD", "", text)  # Soft hyphen
    text = re.sub(r"[\u2013\u2014\u2012\u2015\u002D]", "-", text)

    # Collapse whitespace into single spaces
    text = re.sub(r"\s+", " ", text).strip()

    # Fix formatting of adjacent digits split by whitespace
    text = re.sub(r"(\d+)(?=\s+(\d+))+(\s|$)", r"\1", text)

    # Replace minus and zero-width characters
    text = text.replace("\u2212", "-").replace("\u200b", "").replace("\uf0b7", " ")

    # Normalize single quotation marks
    text = text.replace("\u2018", "'").replace("\u2019", "'")

    # Ensure 'Anf.' starts on its own line
    text = re.sub(r"(?<!\n)(Anf\.\s*\d+\s+)", r"\n\1", text)

    return text


def extract_clauses(cleaned_text):
    # Match clause headers by § + number
    header_pattern = r"\u00a7\s*(\d+)\s+"
    matches = list(re.finditer(header_pattern, cleaned_text))

    clauses = []
    seen_clause_numbers = set()

    for i, match in enumerate(matches):
        clause_number = int(match.group(1))

        if clause_number in seen_clause_numbers:
            continue  # Skip duplicates
        seen_clause_numbers.add(clause_number)

        # Extend start to before <<CLAUSE_TITLE_BLOCK_START>> if possible
        preamble = cleaned_text[: match.start()]
        clause_start = preamble.rfind("<<CLAUSE_TITLE_BLOCK_START>>")
        start = clause_start if clause_start != -1 else match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(cleaned_text)
        full_block = cleaned_text[start:end].strip()

        # --- PRIORITY: Try to extract title using HTML markers
        title_match = re.search(
            r"<<CLAUSE_TITLE_BLOCK_START>>(.*?)<<CLAUSE_TITLE_BLOCK_END>>",
            full_block,
            re.DOTALL,
        )
        if title_match:
            clause_title = title_match.group(1).strip()
            clause_title = re.sub(
                r"^§\s*\d+\s*", "", clause_title
            ).strip()  # Clean "§ X"
            clause_content = re.sub(
                r"<<CLAUSE_TITLE_BLOCK_START>>.*?<<CLAUSE_TITLE_BLOCK_END>>",
                "",
                full_block,
                flags=re.DOTALL,
            ).strip()
        else:
            # --- FALLBACK: Use <<CLAUSE_TITLE_FALLBACK_BREAK>> if no HTML markers found
            clause_content = full_block
            if "<<CLAUSE_TITLE_FALLBACK_BREAK>>" not in clause_content:
                clause_content = re.sub(
                    r"(Anf\.\s*\d+\s+)",
                    r"<<CLAUSE_TITLE_FALLBACK_BREAK>>\1",
                    clause_content,
                    count=1,
                )

            if "<<CLAUSE_TITLE_FALLBACK_BREAK>>" in clause_content:
                clause_title, clause_content = clause_content.split(
                    "<<CLAUSE_TITLE_FALLBACK_BREAK>>", 1
                )
                clause_title = clause_title.strip()
                clause_content = clause_content.strip()
                clause_title = re.sub(r"^§\s*\d+\s*", "", clause_title).strip()
            else:
                clause_title = "(Unknown title)"
                clause_content = clause_content.strip()

        # Clean any remaining markers from clause title/content
        clause_title = re.sub(r"<<.*?>>", "", clause_title).strip()
        clause_content = re.sub(r"<<.*?>>", "", clause_content).strip()

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
        (clause_title + "\n" + clause_content)
        .replace("<<CLAUSE_TITLE_FALLBACK_BREAK>>", "")
        .strip()
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
        speech_text = speech_text.replace("<<SPEECH_START>>", "").strip()
        speech_text = speech_text.replace("<<END_OF_SPEECH>>", "").strip()
        speech_number = int(match.group(1))
        speaker = match.group(2).strip().upper()
        party = match.group(3) or ""
        if speaker in NEUTRAL_SPEAKERS:
            party = ""

        speech_text = re.sub(r"<<.*?>>", "", speech_text).strip()

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
        # Store protocol metadata
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
