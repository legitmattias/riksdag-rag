from fastapi import Query
from typing import Optional, List


def common_speech_filters(
    speaker: Optional[List[str]] = Query(
        None,
        description="Filter by one or more speaker names (partial name allowed)",
        example=["Nohrén"],
    ),
    party: Optional[List[str]] = Query(
        None, description="Filter by one or more parties", example=["M", "Mp"]
    ),
    date: Optional[List[str]] = Query(
        None,
        description="Filter by one or more specific dates (format YYYY-MM-DD)",
        example=["2023-12-19", "2024-06-19"],
    ),
    start_date: Optional[str] = Query(
        None,
        description="Filter speeches from this date (inclusive)",
        example="2023-01-01",
    ),
    end_date: Optional[str] = Query(
        None,
        description="Filter speeches up to this date (inclusive)",
        example="2023-12-31",
    ),
    clause_title: Optional[List[str]] = Query(
        None,
        description="Match clause title(s), partial match allowed",
        example=["klimat", "natur"],
    ),
    match_all: bool = Query(
        False,
        description="Require all clause_title terms to match (default is OR)",
        example=False,
    ),
    skip: int = Query(
        0, ge=0, description="Number of results to skip (for pagination)", example=0
    ),
    limit: int = Query(
        100, le=500, description="Maximum number of results to return", example=50
    ),
):
    return {
        "speaker": speaker,
        "party": party,
        "date": date,
        "start_date": start_date,
        "end_date": end_date,
        "clause_title": clause_title,
        "match_all": match_all,
        "skip": skip,
        "limit": limit,
    }


def common_summary_options(
    group_by_party: bool = Query(False, description="Group results by year and party"),
    resolution: str = Query(
        "year", pattern="^(year|month)$", description="Time resolution (year or month)"
    ),
):
    return {"group_by_party": group_by_party, "resolution": resolution}
