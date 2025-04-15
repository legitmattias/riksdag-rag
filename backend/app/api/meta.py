# backend/app/api/meta.py
from fastapi import APIRouter, Depends
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
