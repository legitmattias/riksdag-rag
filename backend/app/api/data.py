# backend/app/api/data.py
from fastapi import APIRouter, Depends
from app.db.mongo import get_db
from app.models.models import Speech, SummaryResponse, PartyCount, SpeechLengthStats
from app.utils.filters import common_speech_filters, common_summary_options
from app.services.data_service import (
    fetch_speeches,
    fetch_single_speech,
    fetch_speech_summaries,
    fetch_speeches_per_party,
    fetch_speeches_over_time,
    fetch_speech_lengths,
)
from typing import List
from fastapi import HTTPException

router = APIRouter()


@router.get("/speeches", response_model=List[Speech])
def get_speeches(
    base_filters: dict = Depends(common_speech_filters),
    db=Depends(get_db),
):
    """Get full speeches with filters and pagination."""
    return fetch_speeches(db, base_filters)


@router.get("/speeches/{speech_id}", response_model=Speech)
def get_single_speech(
    speech_id: str,
    db=Depends(get_db),
):
    """Get a single speech by ID."""
    try:
        speech = fetch_single_speech(db, speech_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid speech ID format.")

    if not speech:
        raise HTTPException(status_code=404, detail="Speech not found.")

    return speech


@router.get("/speeches/summary", response_model=SummaryResponse)
def get_speech_summaries(
    base_filters: dict = Depends(common_speech_filters),
    db=Depends(get_db),
):
    """Get summarized speeches (metadata only)."""
    return fetch_speech_summaries(db, base_filters)


@router.get("/summary/speeches-per-party", response_model=List[PartyCount])
def get_speeches_per_party(
    base_filters: dict = Depends(common_speech_filters),
    db=Depends(get_db),
):
    """Return number of speeches grouped by party."""
    return fetch_speeches_per_party(db, base_filters)


@router.get("/summary/speeches-over-time", response_model=List[PartyCount])
def get_speeches_over_time(
    base_filters: dict = Depends(common_speech_filters),
    summary_options: dict = Depends(common_summary_options),
    db=Depends(get_db),
):
    """Return number of speeches over time (grouped by year/month and party if requested)."""
    return fetch_speeches_over_time(db, base_filters, summary_options)


@router.get("/summary/speech-lengths", response_model=List[SpeechLengthStats])
def get_speech_lengths(
    base_filters: dict = Depends(common_speech_filters),
    summary_options: dict = Depends(common_summary_options),
    db=Depends(get_db),
):
    """Return average speech length grouped by party and/or speaker."""
    return fetch_speech_lengths(db, base_filters, summary_options)
