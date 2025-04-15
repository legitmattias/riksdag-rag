# backend/app/api/data.py
from fastapi import APIRouter, Depends, Query
from app.db.mongo import get_db
from app.models.models import Speech
from typing import List, Optional
import re

router = APIRouter()

@router.get("/speeches", response_model=List[Speech])
def get_speeches(
    speaker: Optional[List[str]] = Query(None, description="Filter by one or more speaker names"),
    party: Optional[List[str]] = Query(None, description="Filter by one or more parties"),
    date: Optional[List[str]] = Query(None, description="Filter by one or more dates (YYYY-MM-DD)"),
    clause_title: Optional[List[str]] = Query(None, description="Match clause title(s), partial allowed"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    db=Depends(get_db)
):
    query = {}

    if speaker:
        query.setdefault("$and", []).append({
            "$or": [
                {"speaker": {"$regex": re.escape(name), "$options": "i"}}
                for name in speaker
            ]
        })

    if party:
        query["party"] = {"$in": [p.upper() for p in party]}

    if date:
        query["date"] = {"$in": date}

    if clause_title:
        query.setdefault("$and", []).append({
            "$or": [
                {"clause_title": {"$regex": re.escape(ct), "$options": "i"}}
                for ct in clause_title
            ]
        })

    speeches = db.speeches.find(query).skip(skip).limit(limit)
    return list(speeches)
