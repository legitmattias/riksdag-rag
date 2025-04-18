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
        flags=re.IGNORECASE,
    )

    if match:
        cleaned = match.group(4).strip()
    else:
        cleaned = name

    return cleaned.upper()


def regroup_normalized_speakers(
    aggregation_result: list, normalize: bool = False, group_by_party: bool = False
) -> list:
    """
    Post-process aggregation results:
    - Optionally normalize speaker names
    - Regroup by (normalized_speaker, party)
    - Recalculate avg_length
    """
    grouped = {}

    for doc in aggregation_result:
        speaker = doc.get("speaker")
        party = doc.get("party")
        avg_length = doc["avg_length"]
        count = doc["count"]

        # Normalize if enabled
        if normalize and speaker:
            speaker = normalize_speaker_name(speaker)

        key = (speaker, party) if group_by_party else speaker

        if key not in grouped:
            grouped[key] = {"speaker": speaker, "party": party, "count": 0, "total": 0}

        grouped[key]["count"] += count
        grouped[key]["total"] += avg_length * count  # un-avg, re-sum

    # Recompute avg_length
    final = []
    for entry in grouped.values():
        entry["avg_length"] = round(entry["total"] / entry["count"], 1)
        del entry["total"]
        final.append(entry)

    # Sort by avg_length descending
    return sorted(final, key=lambda x: x["avg_length"], reverse=True)
