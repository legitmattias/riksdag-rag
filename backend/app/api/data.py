# backend/app/api/data.py
from fastapi import APIRouter, Depends
from app.db.mongo import get_db
from app.models.models import Speech
from typing import List

router = APIRouter()

@router.get("/speeches", response_model=List[Speech])
def get_speeches(db=Depends(get_db)):
    return list(db.speeches.find({}, {"_id": 0}))
