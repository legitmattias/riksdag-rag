# /models/search_models.py

from pydantic import BaseModel
from typing import List, Optional

class RAGQueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5  # How many documents to retrieve

class SourceDocument(BaseModel):
    text: str
    speaker: Optional[str]
    party: Optional[str]
    date: Optional[str]

class RAGQueryResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]