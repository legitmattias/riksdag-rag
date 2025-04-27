# /api/search.py

from fastapi import APIRouter
from app.models.search_models import RAGQueryRequest, RAGQueryResponse, SourceDocument
from app.services.rag_service import generate_answer

router = APIRouter()

@router.post("/rag/query", response_model=RAGQueryResponse)
async def rag_query(request: RAGQueryRequest):
    result = generate_answer(request.query, request.top_k)
    return RAGQueryResponse(
        answer=result["answer"],
        sources=[SourceDocument(**src) for src in result["sources"]]
    )