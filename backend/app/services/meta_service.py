# backend/app/services/meta_service.py
from app.repositories.meta_repository import (
    find_all_protocols,
    get_distinct_party_codes,
    find_speakers_with_party,
    get_date_range
)
from app.utils.speaker_normalizer import normalize_speaker_name
from collections import defaultdict, Counter


def fetch_protocols(db):
    """Fetch all protocols with no internal MongoDB _id."""
    return list(find_all_protocols(db))


def fetch_party_labels(db):
    """Fetch unique party codes and return them with user-friendly labels."""
    codes = get_distinct_party_codes(db)
    unique = sorted(set(code.strip() for code in codes if code is not None))

    party_labels = {
        "": "Neutral",
        "S": "Socialdemokraterna",
        "M": "Moderaterna",
        "V": "Vänsterpartiet",
        "C": "Centerpartiet",
        "L": "Liberalerna",
        "KD": "Kristdemokraterna",
        "MP": "Miljöpartiet",
        "SD": "Sverigedemokraterna",
    }

    return [{"code": code, "label": party_labels.get(code, code)} for code in unique]


def fetch_top_speakers(db, limit=50):
    """Aggregate top speakers and normalize names, resolving their most common party."""
    raw = find_speakers_with_party(db)
    speaker_counts = defaultdict(int)
    speaker_parties = defaultdict(list)

    for doc in raw:
        name = doc.get("speaker")
        party = doc.get("party") or ""

        if not name:
            continue

        normalized = normalize_speaker_name(name)
        speaker_counts[normalized] += 1
        speaker_parties[normalized].append(party)

    # Sort and pick most common party for each speaker
    sorted_speakers = sorted(speaker_counts.items(), key=lambda x: x[1], reverse=True)

    result = []
    for name, count in sorted_speakers[:limit]:
        most_common_party = Counter(speaker_parties[name]).most_common(1)[0][0]
        result.append({
            "speaker": name,
            "party": most_common_party,
            "count": count
        })

    return result

def fetch_date_range(db):
    """Fetch min and max date of speeches."""
    return get_date_range(db)

