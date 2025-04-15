# backend/app/api/meta.py
from fastapi import APIRouter, Depends, Query
from app.db.mongo import get_db
from app.models.models import Protocol
from typing import List

router = APIRouter()


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


@router.get("/speakers", response_model=List[str])
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
        {"$limit": limit},
    ]
    result = db.speeches.aggregate(pipeline)
    return [doc["_id"] for doc in result]
