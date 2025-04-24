# backend/app/api/meta.py
from fastapi import APIRouter, Depends, Query
from app.db.mongo import get_db
from app.models.models import Protocol, SpeakerCount
from app.services.meta_service import (
    fetch_protocols,
    fetch_party_labels,
    fetch_top_speakers,
    fetch_date_range
)
from typing import List

router = APIRouter()


@router.get("/protocols", response_model=List[Protocol])
def get_protocols(db=Depends(get_db)):
    """Return a list of all parliamentary protocols."""
    return fetch_protocols(db)


@router.get("/parties", response_model=List[dict])
def get_parties(db=Depends(get_db)):
    """Return a list of all unique party codes with optional labels."""
    return fetch_party_labels(db)


@router.get("/top-speakers", response_model=List[SpeakerCount])
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
    """Return a list of top speakers ranked by speech count, normalized by title."""
    return fetch_top_speakers(db, limit)


@router.get("/date-range")
def get_date_range_endpoint(db=Depends(get_db)):
    """Return earliest and latest speech date."""
    return fetch_date_range(db)

