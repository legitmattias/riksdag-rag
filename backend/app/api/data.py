# backend/app/api/data.py
from fastapi import APIRouter, Depends, Query
from app.db.mongo import get_db
from app.models.models import Speech
from typing import List, Optional
import re

router = APIRouter()

@router.get("/speeches", response_model=List[Speech])
def get_speeches(
    speaker: Optional[str] = Query(None, description="Filter by speaker name (case-insensitive)"),
    party: Optional[str] = Query(None, description="Filter by party"),
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    clause_title: Optional[str] = Query(None, description="Match clause title (partial allowed)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    db=Depends(get_db)
):
    query = {}

    if speaker:
        query["speaker"] = {"$regex": re.escape(speaker), "$options": "i"}

    if party:
        query["party"] = party.upper()

    if date:
        query["date"] = date

    if clause_title:
        query["clause_title"] = {"$regex": clause_title, "$options": "i"}

    speeches = db.speeches.find(query).skip(skip).limit(limit)
    return list(speeches)
