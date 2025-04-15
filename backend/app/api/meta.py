# backend/app/api/meta.py
from fastapi import APIRouter, Depends, Query
from app.db.mongo import get_db
from app.models.models import Protocol
from typing import List
from collections import defaultdict
import re
from app.models.models import SpeakerCount

router = APIRouter()


def normalize_speaker_name(name: str) -> str:
    """
    Removes titles ending in 'minister', 'rådet', or 'konungen'.
    Returns the remaining speaker name, uppercased.
    """
    name = name.strip()

    # Match title prefixes ending with specified words
    match = re.search(r"(minister|rådet|konungen)\s+(.*)$", name, flags=re.IGNORECASE)

    if match:
        cleaned = match.group(2).strip()
    else:
        cleaned = name

    return cleaned.upper()


@router.get("/protocols", response_model=List[Protocol])
def get_protocols(db=Depends(get_db)):
    return list(db.protocols.find({}, {"_id": 0}))


@router.get("/parties", response_model=List[dict])
def get_parties(db=Depends(get_db)):
    party_codes = db.speeches.distinct("party")
    unique_codes = sorted(set(code.strip() for code in party_codes if code is not None))

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

    return [
        {"code": code, "label": party_labels.get(code, code)} for code in unique_codes
    ]


@router.get("/speakers", response_model=List[SpeakerCount])
def get_top_speakers(
    db=Depends(get_db),
    limit: int = Query(
        50,
        ge=1,
        le=100,
        description="Number of top speakers to return (based on number of speeches)",
        example=10,
    ),
):
    pipeline = [
        {"$group": {"_id": "$speaker", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 200},  # allows space for duplicate names with titles
    ]
    raw_results = db.speeches.aggregate(pipeline)

    speaker_counts = defaultdict(int)

    for doc in raw_results:
        raw_name = doc["_id"]
        count = doc["count"]

        if not raw_name:
            continue

        normalized = normalize_speaker_name(raw_name)
        speaker_counts[normalized] += count

    top_speakers = sorted(
        [{"speaker": name, "count": count} for name, count in speaker_counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )[:limit]

    return top_speakers
