# backend/app/repositories/meta_repository.py


def find_all_protocols(db):
    """Return all protocol records without _id field."""
    return db.protocols.find({}, {"_id": 0})


def get_distinct_party_codes(db):
    """Return a list of all unique party codes in the speeches collection."""
    return db.speeches.distinct("party")

def find_speakers_with_party(db):
    """Return all speakers with associated party information."""
    return db.speeches.find({}, {"speaker": 1, "party": 1})

def get_date_range(db):
    """Return the earliest and latest dates from the speeches collection."""
    pipeline = [
        {
            "$group": {
                "_id": None,
                "min_date": {"$min": "$date"},
                "max_date": {"$max": "$date"}
            }
        },
        {"$project": {"_id": 0, "min_date": 1, "max_date": 1}}
    ]
    result = list(db.speeches.aggregate(pipeline))
    return result[0] if result else {"min_date": None, "max_date": None}
