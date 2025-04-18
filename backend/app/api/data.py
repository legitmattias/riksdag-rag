# backend/app/api/data.py
from fastapi import APIRouter, Depends
from app.db.mongo import get_db
from app.models.models import Speech, SpeechSummary, PartyCount, SpeechLengthStats
from app.utils.filters import common_speech_filters, common_summary_options
from app.utils.query_builder import build_speech_query
from app.utils.pagination import apply_pagination
from app.utils.speaker_normalizer import normalize_speaker_name

from typing import List

router = APIRouter()


@router.get("/speeches", response_model=List[Speech])
def get_speeches(
    base_filters: dict = Depends(common_speech_filters), db=Depends(get_db)
):
    query = build_speech_query(base_filters)
    cursor = db.speeches.find(query)
    paginated = apply_pagination(cursor, base_filters["skip"], base_filters["limit"])
    return list(paginated)


@router.get("/speeches/summary", response_model=List[SpeechSummary])
def get_speech_summaries(
    base_filters: dict = Depends(common_speech_filters), db=Depends(get_db)
):
    query = build_speech_query(base_filters)
    projection = {
        "_id": 0,
        "speaker": 1,
        "party": 1,
        "date": 1,
        "clause_title": 1,
        "speech_number": 1,
        "length": 1,
    }
    cursor = db.speeches.find(query, projection)
    paginated = apply_pagination(cursor, base_filters["skip"], base_filters["limit"])
    return list(paginated)


@router.get("/summary/speeches-per-party", response_model=List[PartyCount])
def get_speeches_per_party(
    base_filters: dict = Depends(common_speech_filters), db=Depends(get_db)
):
    query = build_speech_query(base_filters)

    pipeline = [
        {"$match": query},
        {"$group": {"_id": "$party", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$project": {"_id": 0, "party": "$_id", "count": 1}},
    ]

    results = db.speeches.aggregate(pipeline)
    return list(results)


@router.get("/summary/speeches-over-time", response_model=List[PartyCount])
def get_speeches_over_time(
    base_filters: dict = Depends(common_speech_filters),
    summary_options: dict = Depends(common_summary_options),
    db=Depends(get_db),
):
    group_by_party = summary_options["group_by_party"]
    resolution = summary_options["resolution"]

    query = build_speech_query(base_filters)

    # Determine projection
    projection = {"year": {"$substr": ["$date", 0, 4]}, "party": 1}

    if resolution == "month":
        projection["month"] = {"$substr": ["$date", 5, 2]}

    group_id = {"year": "$year"}
    if resolution == "month":
        group_id["month"] = "$month"
    if group_by_party:
        group_id["party"] = "$party"

    sort_keys = list(group_id.keys())

    pipeline = [
        {"$match": query},
        {"$project": projection},
        {"$group": {"_id": group_id, "count": {"$sum": 1}}},
        {"$sort": {f"_id.{k}": 1 for k in sort_keys}},
        {
            "$project": {
                "year": "$_id.year",
                "month": "$_id.month" if resolution == "month" else None,
                "party": "$_id.party" if group_by_party else None,
                "count": 1,
                "_id": 0,
            }
        },
    ]

    results = db.speeches.aggregate(pipeline)
    return list(results)


@router.get("/summary/speech-lengths", response_model=List[SpeechLengthStats])
def get_speech_lengths(
    base_filters: dict = Depends(common_speech_filters),
    summary_options: dict = Depends(common_summary_options),
    db=Depends(get_db),
):
    group_by_party = summary_options["group_by_party"]
    group_by_speaker = summary_options["group_by_speaker"]

    query = build_speech_query(base_filters)

    projection = {"length": 1}
    if group_by_party:
        projection["party"] = 1
    if group_by_speaker:
        projection["speaker"] = 1

    # Build _id group object
    group_id = {}
    if group_by_party:
        group_id["party"] = "$party"
    if group_by_speaker:
        group_id["speaker"] = "$speaker"

    pipeline = [
        {"$match": query},
        {"$project": projection},
        {
            "$group": {
                "_id": group_id if group_id else None,
                "avg_length": {"$avg": "$length"},
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"avg_length": -1}},
        {
            "$project": {
                "party": "$_id.party" if group_by_party else None,
                "speaker": "$_id.speaker" if group_by_speaker else None,
                "avg_length": {"$round": ["$avg_length", 1]},
                "count": 1,
                "_id": 0,
            }
        },
    ]

    results = db.speeches.aggregate(pipeline)
    grouped = {}

    for doc in results:
        speaker = doc.get("speaker")
        party = doc.get("party")
        avg_length = doc["avg_length"]
        count = doc["count"]

        # Normalize only if grouping by speaker
        if group_by_speaker and speaker:
            normalized = normalize_speaker_name(speaker)
        else:
            normalized = speaker

        key = (normalized, party) if group_by_party else normalized

        if key not in grouped:
            grouped[key] = {
                "speaker": normalized,
                "party": party,
                "count": 0,
                "total": 0,
            }

        grouped[key]["count"] += count
        grouped[key]["total"] += avg_length * count  # reverse average to total

    # Recompute actual avg
    final = []
    for entry in grouped.values():
        entry["avg_length"] = round(entry["total"] / entry["count"], 1)
        del entry["total"]
        final.append(entry)

    final = sorted(
        final,
        key=lambda entry: entry["avg_length"],
        reverse=True,  # descending, highest first
    )

    return final
