# backend/app/services/meta_service.py
from app.repositories.meta_repository import (
    find_all_protocols,
    get_distinct_party_codes,
    aggregate_speaker_counts,
)
from app.utils.speaker_normalizer import normalize_speaker_name
from collections import defaultdict


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
    """Aggregate top speakers and normalize names by removing titles."""
    raw = aggregate_speaker_counts(db)
    counts = defaultdict(int)

    for doc in raw:
        raw_name = doc["_id"]
        count = doc["count"]
        if not raw_name:
            continue
        normalized = normalize_speaker_name(raw_name)
        counts[normalized] += count

    sorted_speakers = sorted(counts.items(), key=lambda x: x[1], reverse=True)

    sorted_speakers.sort(key=lambda x: x[1], reverse=True)

    return [
        {"speaker": name, "count": count} for name, count in sorted_speakers[:limit]
    ]
