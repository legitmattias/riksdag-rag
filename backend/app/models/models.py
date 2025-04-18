# backend/app/models/models.py
from pydantic import BaseModel
from typing import List, Optional


class Clause(BaseModel):
    number: int
    title: str


class Protocol(BaseModel):
    document_id: str
    title: str
    parliament_year: str
    date: str
    num_clauses: int
    num_speeches: int
    clauses: List[Clause]


class Speech(BaseModel):
    document_id: str
    hangar_id: str
    parliament_year: str
    date: str
    title: str
    clause_number: int
    clause_title: str
    speech_number: int
    speaker: str
    party: Optional[str]
    text: str
    length: int


class SpeechSummary(BaseModel):
    speaker: Optional[str]
    party: Optional[str]
    date: Optional[str]
    clause_title: Optional[str]
    speech_number: Optional[int]
    length: Optional[int]


class SpeakerCount(BaseModel):
    speaker: str
    count: int


class PartyCount(BaseModel):
    year: str
    month: Optional[str] = None
    party: Optional[str] = None
    count: int
