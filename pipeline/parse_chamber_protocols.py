# /pipeline/parse_chamber_protocols.py

"""
This script processes chamber protocol JSON files to extract structured data.

It parses raw HTML content to identify and mark structural elements such as clauses and speeches. The script then extracts metadata, clause titles, and speech content, normalizing and cleaning the data.

Outputs:
1. protocols.json - Contains metadata and clause information for each protocol.
2. speeches.json - Contains detailed speech data, including speaker, party, and speech text.
"""

import os
import json
import re
from bs4 import BeautifulSoup, NavigableString
from tqdm import tqdm

# Neutral speakers without party affiliation
NEUTRAL_SPEAKERS = [
    "TALMANNEN",
    "FÖRSTE VICE TALMANNEN",
    "ANDRE VICE TALMANNEN",
    "TREDJE VICE TALMANNEN",
    "TJÄNSTGÖRANDE ÅLDERSPRESIDENTEN",
    "HANS MAJESTÄT KONUNGEN",
]

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.join(BASE_DIR, "./raw")
PARSED_DATA_DIR = os.path.join(BASE_DIR, "./data")
os.makedirs(PARSED_DATA_DIR, exist_ok=True)

# ------------------------------------------------------------------------
# HTML Preprocessing
# ------------------------------------------------------------------------


def mark_structural_boundaries(raw_html):
    """
    Insert custom markers into <h1> and <h2> tags to support clause/speech parsing.
    Ensures space between clause number and title span to avoid merging.
    """
    soup = BeautifulSoup(raw_html, "html.parser")

    # Add markers around <h1> tags containing clauses to structure clause parsing.
    for h1 in soup.find_all("h1"):
        text = h1.get_text().strip()
        if "§" in text:
            spans = h1.find_all("span")
            if len(spans) >= 3:
                if spans[0].text.strip() == "§":
                    for i, span in enumerate(spans):
                        if span.text.strip().isdigit():
                            marker = soup.new_tag("span")
                            marker.string = "<<CLAUSE_NUMBER_END>>"
                            span.insert_after(marker)
                            break

            h1.insert_before(NavigableString("<<CLAUSE_TITLE_BLOCK_START>>\n"))
            h1.insert_after(NavigableString("\n<<CLAUSE_TITLE_BLOCK_END>>"))

    # Insert a marker before <h2> tags containing speeches to identify speech blocks.
    for h2 in soup.find_all("h2"):
        if "Anf." in h2.get_text():
            h2.insert_before(NavigableString("<<SPEECH_START>>\n"))

    return soup.get_text(separator="\n")


def normalize_text(text):
    """
    Normalize whitespace, unicode dashes, quotation marks, and inject fallback markers.
    """
    # Cut footer section
    text = re.split(r"Sammanträdet leddes(?:.|\n)*?(?=Vid protokollet|Tryck:)", text)[0]

    # Add fallback break between clause title and body
    text = re.sub(
        r"(§\s*\d+\s+(?:\(forts\.\)\s*)?[^\n]+)(\n{2,})",
        r"\1 <<CLAUSE_TITLE_FALLBACK_BREAK>>\2",
        text,
    )

    # Insert end-of-speech marker
    text = re.sub(
        r"\n\s*Ajournering\s*\n", "\n<<END_OF_SPEECH>>\n", text, flags=re.IGNORECASE
    )

    # Clean and normalize characters
    text = re.sub(r"\n+", "\n", text)
    text = text.replace("\xa0", " ").replace("\u2011", "-")
    text = re.sub(r"\u00AD", "", text)
    text = re.sub(r"[\u2013\u2014\u2012\u2015\u002D]", "-", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"(\d+)(?=\s+(\d+))+(\s|$)", r"\1", text)
    text = text.replace("\u2212", "-").replace("\u200b", "").replace("\uf0b7", " ")
    text = text.replace("\u2018", "'").replace("\u2019", "'")

    # Ensure "Anf." starts on new line
    text = re.sub(r"(?<!\n)(Anf\.\s*\d+\s+)", r"\n\1", text)

    return text


def clean_html(raw_html):
    """
    Full cleaning pipeline.
    """
    marked = mark_structural_boundaries(raw_html)
    return normalize_text(marked)


# ------------------------------------------------------------------------
# Clause and Speech Extraction
# ------------------------------------------------------------------------


def extract_clause_blocks(cleaned_text):
    """
    Slice up the cleaned text into clause segments.
    """
    header_pattern = r"\u00a7\s*(\d+)\s+"
    return list(re.finditer(header_pattern, cleaned_text))


def parse_clause_title_and_content(block):
    """
    Parse clause title and content from a text block.
    Handles both cleanly marked blocks and fallback structure.
    """
    # Priority: cleanly marked with HTML
    html_match = re.search(
        r"<<CLAUSE_TITLE_BLOCK_START>>(.*?)<<CLAUSE_TITLE_BLOCK_END>>", block, re.DOTALL
    )

    if html_match:
        raw_block = html_match.group(1).strip()

        # Use custom injected marker if present
        if "<<CLAUSE_NUMBER_END>>" in raw_block:
            title = raw_block.split("<<CLAUSE_NUMBER_END>>", 1)[-1].strip()
        else:
            title = re.sub(r"^§\s*\d{1,3}", "", raw_block).lstrip(" \u00a0")

        title = re.sub(r"<<.*?>>", "", title).strip()

        content = re.sub(
            r"<<CLAUSE_TITLE_BLOCK_START>>.*?<<CLAUSE_TITLE_BLOCK_END>>",
            "",
            block,
            flags=re.DOTALL,
        ).strip()

    else:
        # Fallback on paragraph pattern
        if "<<CLAUSE_TITLE_FALLBACK_BREAK>>" not in block:
            block = re.sub(
                r"(Anf\.\s*\d+\s+)",
                r"<<CLAUSE_TITLE_FALLBACK_BREAK>>\1",
                block,
                count=1,
            )

        if "<<CLAUSE_TITLE_FALLBACK_BREAK>>" in block:
            title, content = block.split("<<CLAUSE_TITLE_FALLBACK_BREAK>>", 1)
            title = re.sub(r"^§\s*\d+\s*", "", title.strip())
            content = content.strip()
        else:
            title = "(Unknown title)"
            content = block.strip()

    # Final marker cleanup
    title = re.sub(r"<<.*?>>", "", title).strip()
    content = re.sub(r"<<.*?>>", "", content).strip()

    return title, content


def extract_clauses(cleaned_text):
    """
    Use header markers to split up the text and extract clauses.
    """
    matches = extract_clause_blocks(cleaned_text)
    clauses = []
    seen_clause_numbers = set()

    for i, match in enumerate(matches):
        clause_number = int(match.group(1))
        if clause_number in seen_clause_numbers:
            continue
        seen_clause_numbers.add(clause_number)

        # Pull block between current and next clause header
        preamble = cleaned_text[: match.start()]
        clause_start = preamble.rfind("<<CLAUSE_TITLE_BLOCK_START>>")
        start = clause_start if clause_start != -1 else match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(cleaned_text)
        full_block = cleaned_text[start:end].strip()

        title, content = parse_clause_title_and_content(full_block)
        clauses.append((clause_number, title, content))

    return clauses


# ------------------------------------------------------------------------
# Speech Extraction
# ------------------------------------------------------------------------


def extract_speeches(clause_title, clause_content):
    """
    Use regex to find all speeches (Anf.) inside a clause block.
    """
    speech_pattern = (
        r"(?i)Anf\.\s*(\d+)\s+"
        r"([A-ZÅÄÖÉÜ][^:(\n]+?)"
        r"(?:\s+\((\w+)\))?"
        r"(?:\s+\w+)*:"
    )

    # Merge title + content for speech detection
    full_text = f"{clause_title}\n{clause_content}"
    full_text = re.sub(r"<<.*?>>", "", full_text).strip()

    matches = list(re.finditer(speech_pattern, full_text))
    speeches = []

    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)
        speech_text = full_text[start:end].strip()

        # Clean embedded markers
        speech_text = re.sub(r"<<.*?>>", "", speech_text).strip()
        speech_number = int(match.group(1))
        speaker = match.group(2).strip().upper()

        # Attempt to rehydrate cut-off neutral titles
        for neutral in NEUTRAL_SPEAKERS:
            if neutral.startswith(speaker):
                speaker = neutral
                party = ""
                break

        party = match.group(3) or ""
        if speaker in NEUTRAL_SPEAKERS:
            party = ""

        length = len(speech_text.split())

        speeches.append(
            {
                "speech_number": speech_number,
                "speaker": speaker,
                "party": party,
                "text": speech_text,
                "length": length,
            }
        )

    return speeches


# ------------------------------------------------------------------------
# Main File Processor
# ------------------------------------------------------------------------


def extract_meta(data):
    dokument = data.get("dokumentstatus", {}).get("dokument", {})
    pdf_info = data.get("dokumentstatus", {}).get("dokbilaga", {}).get("bilaga", {})
    raw_date = dokument.get("datum")
    parsed_date = raw_date.split(" ")[0] if raw_date else None

    return {
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


def process_files():
    speeches = []
    protocols = []

    files = [f for f in os.listdir(RAW_DATA_DIR) if f.endswith(".json")]
    for file_name in tqdm(files, desc="Parsing files"):
        with open(os.path.join(RAW_DATA_DIR, file_name), encoding="utf-8") as f:
            data = json.load(f)
        dokument = data.get("dokumentstatus", {}).get("dokument", {})
        if not dokument:
            continue

        base_meta = extract_meta(data)
        cleaned = clean_html(dokument.get("html", ""))
        clauses = extract_clauses(cleaned)

        clause_info = [{"number": num, "title": title} for num, title, _ in clauses]
        clause_speeches = []

        for number, title, content in clauses:
            for speech in extract_speeches(title, content):
                clause_speeches.append(
                    {
                        **base_meta,
                        "clause_number": number,
                        "clause_title": title,
                        **speech,
                    }
                )

        speeches.extend(clause_speeches)

        protocols.append(
            {
                "document_id": base_meta["document_id"],
                "title": base_meta["title"],
                "parliament_year": base_meta["parliament_year"],
                "date": base_meta["date"],
                "num_clauses": len(clauses),
                "num_speeches": len(clause_speeches),
                "clauses": clause_info,
            }
        )

    return protocols, speeches


# ------------------------------------------------------------------------
# Entry Point
# ------------------------------------------------------------------------

if __name__ == "__main__":
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
