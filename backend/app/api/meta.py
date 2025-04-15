# backend/app/api/meta.py
from fastapi import APIRouter, Depends
from app.db.mongo import get_db
from app.models.models import Protocol
from typing import List

router = APIRouter()

@router.get("/protocols", response_model=List[Protocol])
def get_protocols(db=Depends(get_db)):
    return list(db.protocols.find({}, {"_id": 0}))

@router.get("/parties", response_model=List[str])
def get_parties(db=Depends(get_db)):
    return sorted(db.speeches.distinct("party"))