# backend/app/api/data.py
from fastapi import APIRouter, Depends, Query
from app.db.mongo import get_db
from app.models.models import Speech
from typing import List, Optional
import re

router = APIRouter()


@router.get("/speeches", response_model=List[Speech])
def get_speeches(
    speaker: Optional[List[str]] = Query(
        None,
        description="Filter by one or more speaker names",
        example=["Nohrén"],
    ),
    party: Optional[List[str]] = Query(
        None, description="Filter by one or more parties", example=["M", "Mp"]
    ),
    date: Optional[List[str]] = Query(
        None,
        description="Filter by one or more dates (YYYY-MM-DD)",
        example=["2023-12-19", "2024-06-19"],
    ),
    clause_title: Optional[List[str]] = Query(
        None, description="Match clause title(s), partial allowed", example=["klimat", "natur"]
    ),
    match_all: bool = Query(
        False, description="Require all clause_title terms to match", example=False
    ),
    skip: int = Query(
        0, ge=0, description="Number of results to skip (for pagination)", example=0
    ),
    limit: int = Query(
        100,
        le=500,
        description="Maximum number of results to return (max 500)",
        example=50,
    ),
    db=Depends(get_db),
):
    query = {}

    if speaker:
        query.setdefault("$and", []).append(
            {
                "$or": [
                    {"speaker": {"$regex": re.escape(name), "$options": "i"}}
                    for name in speaker
                ]
            }
        )

    if party:
        query["party"] = {"$in": [p.upper() for p in party]}

    if date:
        query["date"] = {"$in": date}

    if clause_title:
        condition_list = [
            {"clause_title": {"$regex": re.escape(ct), "$options": "i"}}
            for ct in clause_title
        ]
        clause_query = (
            {"$and": condition_list} if match_all else {"$or": condition_list}
        )
        query.setdefault("$and", []).append(clause_query)

    speeches = db.speeches.find(query).skip(skip).limit(limit)
    return list(speeches)
