# backend/app/utils/speaker_normalizer.py

import re

def normalize_speaker_name(name: str) -> str:
    """
    Removes official titles like 'statsminister', 'rådet', 'konungen', etc.
    Preserves formal speaker variants like 'i NORRHULT' if present.
    Returns the cleaned name in uppercase.
    """
    name = name.strip()

    # Remove titles like "statsrådet", "tillträdande statsminister", "presidenten"
    match = re.search(
        r"(?:(tillträdande|ålders)?\s*)?"
        r"(statsrådet|.*ministern?|rådet|president(en)?|konungen)\s+(.+)$",
        name,
        flags=re.IGNORECASE
    )

    if match:
        cleaned = match.group(4).strip()
    else:
        cleaned = name

    return cleaned.upper()
