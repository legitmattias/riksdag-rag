# backend/app/repositories/meta_repository.py


def find_all_protocols(db):
    """Return all protocol records without _id field."""
    return db.protocols.find({}, {"_id": 0})


def get_distinct_party_codes(db):
    """Return a list of all unique party codes in the speeches collection."""
    return db.speeches.distinct("party")


def aggregate_speaker_counts(db):
    """Aggregate the number of speeches per raw speaker name."""
    pipeline = [
        {"$group": {"_id": "$speaker", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 200},  # Allows space for title-variant duplicates
    ]
    return db.speeches.aggregate(pipeline)
