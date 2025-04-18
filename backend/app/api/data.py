# backend/app/api/data.py
from fastapi import APIRouter, Depends
from app.db.mongo import get_db
from app.models.models import Speech, SpeechSummary, PartyCount
from app.utils.filters import common_speech_filters, common_summary_options
from app.utils.query_builder import build_speech_query
from app.utils.pagination import apply_pagination

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
