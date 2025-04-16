# backend/app/utils/pagination.py

def apply_pagination(cursor, skip: int, limit: int):
    return cursor.skip(skip).limit(limit)
