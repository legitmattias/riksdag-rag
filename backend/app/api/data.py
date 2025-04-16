# backend/app/api/data.py
from fastapi import APIRouter, Depends
from app.db.mongo import get_db
from app.models.models import Speech, SpeechSummary, PartyCount
from app.utils.filters import common_speech_filters
from app.utils.query_builder import build_speech_query
from app.utils.pagination import apply_pagination

from typing import List

router = APIRouter()


@router.get("/speeches", response_model=List[Speech])
def get_speeches(filters: dict = Depends(common_speech_filters), db=Depends(get_db)):
    query = build_speech_query(filters)
    cursor = db.speeches.find(query)
    paginated = apply_pagination(cursor, filters["skip"], filters["limit"])
    return list(paginated)


@router.get("/speeches/summary", response_model=List[SpeechSummary])
def get_speech_summaries(
    filters: dict = Depends(common_speech_filters), db=Depends(get_db)
):
    query = build_speech_query(filters)
    projection = {
        "_id": 0,
        "speaker": 1,
        "party": 1,
        "date": 1,
        "clause_title": 1,
        "speech_number": 1,
    }
    cursor = db.speeches.find(query, projection)
    paginated = apply_pagination(cursor, filters["skip"], filters["limit"])
    return list(paginated)


@router.get("/summary/speeches-per-party", response_model=List[PartyCount])
def get_speeches_per_party(
    filters: dict = Depends(common_speech_filters), db=Depends(get_db)
):
    query = build_speech_query(filters)

    pipeline = [
        {"$match": query},
        {"$group": {"_id": "$party", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$project": {"_id": 0, "party": "$_id", "count": 1}},
    ]

    results = db.speeches.aggregate(pipeline)
    return list(results)
