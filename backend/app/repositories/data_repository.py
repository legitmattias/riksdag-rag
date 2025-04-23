# backend/app/repositories/data_repository.py

def count_speeches(db, query) -> int:
    """Return number of speeches matching the query."""
    return db.speeches.count_documents(query)


def find_speeches(db, query, projection=None):
    """Find speeches with optional projection."""
    return db.speeches.find(query, projection)


def aggregate_speeches_per_party(db, query):
    """Aggregate number of speeches grouped by party."""
    pipeline = [
        {"$match": query},
        {"$group": {"_id": "$party", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$project": {"_id": 0, "party": "$_id", "count": 1}},
    ]
    return db.speeches.aggregate(pipeline)


def aggregate_speeches_over_time(db, query, options):
    """Aggregate speech counts over time, grouped by year/month and party."""
    resolution = options["resolution"]
    group_by_party = options["group_by_party"]

    projection = {"year": {"$substr": ["$date", 0, 4]}, "party": 1}
    if resolution == "month":
        projection["month"] = {"$substr": ["$date", 5, 2]}

    group_id = {"year": "$year"}
    if resolution == "month":
        group_id["month"] = "$month"
    if group_by_party:
        group_id["party"] = "$party"

    sort_keys = list(group_id.keys())

    pipeline = [
        {"$match": query},
        {"$project": projection},
        {"$group": {"_id": group_id, "count": {"$sum": 1}}},
        {"$sort": {f"_id.{k}": 1 for k in sort_keys}},
        {
            "$project": {
                "year": "$_id.year",
                "month": "$_id.month" if resolution == "month" else None,
                "party": "$_id.party" if group_by_party else None,
                "count": 1,
                "_id": 0,
            }
        },
    ]
    return db.speeches.aggregate(pipeline)


def build_speech_length_pipeline(query, options):
    """Construct aggregation pipeline for speech length summaries."""
    group_by_party = options["group_by_party"]
    group_by_speaker = options["group_by_speaker"]

    projection = {"length": 1}
    if group_by_party:
        projection["party"] = 1
    if group_by_speaker:
        projection["speaker"] = 1

    group_id = {}
    if group_by_party:
        group_id["party"] = "$party"
    if group_by_speaker:
        group_id["speaker"] = "$speaker"

    return [
        {"$match": query},
        {"$project": projection},
        {
            "$group": {
                "_id": group_id if group_id else None,
                "avg_length": {"$avg": "$length"},
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"avg_length": -1}},
        {
            "$project": {
                "party": "$_id.party" if group_by_party else None,
                "speaker": "$_id.speaker" if group_by_speaker else None,
                "avg_length": {"$round": ["$avg_length", 1]},
                "count": 1,
                "_id": 0,
            }
        },
    ]


def aggregate_pipeline(db, pipeline):
    """Execute a generic aggregation pipeline."""
    return db.speeches.aggregate(pipeline)
