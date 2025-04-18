# backend/app/services/data_service.py

from app.repositories.data_repository import (
    find_speeches,
    aggregate_speeches_per_party,
    aggregate_speeches_over_time,
    build_speech_length_pipeline,
    aggregate_pipeline,
)
from app.utils.query_builder import build_speech_query
from app.utils.pagination import apply_pagination
from app.utils.speaker_normalizer import regroup_normalized_speakers


def fetch_speeches(db, filters):
    """Fetch paginated full speeches based on filters."""
    query = build_speech_query(filters)
    cursor = find_speeches(db, query)
    return list(apply_pagination(cursor, filters["skip"], filters["limit"]))


def fetch_speech_summaries(db, filters):
    """Fetch paginated speech summaries with metadata only."""
    query = build_speech_query(filters)
    projection = {
        "_id": 0,
        "speaker": 1,
        "party": 1,
        "date": 1,
        "clause_title": 1,
        "speech_number": 1,
        "length": 1,
    }
    cursor = find_speeches(db, query, projection)
    return list(apply_pagination(cursor, filters["skip"], filters["limit"]))


def fetch_speeches_per_party(db, filters):
    """Return count of speeches grouped by party."""
    query = build_speech_query(filters)
    return aggregate_speeches_per_party(db, query)


def fetch_speeches_over_time(db, filters, options):
    """Return count of speeches over time, optionally grouped by party and resolution."""
    query = build_speech_query(filters)
    return aggregate_speeches_over_time(db, query, options)


def fetch_speech_lengths(db, filters, options):
    """Return average speech length grouped by speaker and/or party."""
    query = build_speech_query(filters)
    pipeline = build_speech_length_pipeline(query, options)
    results = aggregate_pipeline(db, pipeline)
    return regroup_normalized_speakers(
        results,
        normalize=options["group_by_speaker"],
        group_by_party=options["group_by_party"],
    )
