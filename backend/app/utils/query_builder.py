# backend/app/utils/query_builder.py
import re

def build_speech_query(filters: dict) -> dict:
    query = {}

    if filters["speaker"]:
        query.setdefault("$and", []).append({
            "$or": [
                {"speaker": {"$regex": re.escape(name), "$options": "i"}}
                for name in filters["speaker"]
            ]
        })

    if filters["party"] is not None:
        query["party"] = {"$in": [p.upper() for p in filters["party"]]}

    if filters["date"]:
        query["date"] = {"$in": filters["date"]}

    if filters["start_date"] or filters["end_date"]:
        query["date"] = {}
        if filters["start_date"]:
            query["date"]["$gte"] = filters["start_date"]
        if filters["end_date"]:
            query["date"]["$lte"] = filters["end_date"]

    if filters["clause_title"]:
        clause_conditions = [
            {"clause_title": {"$regex": re.escape(ct), "$options": "i"}}
            for ct in filters["clause_title"]
        ]
        clause_logic = "$and" if filters["match_all"] else "$or"
        query.setdefault("$and", []).append({clause_logic: clause_conditions})

    return query
