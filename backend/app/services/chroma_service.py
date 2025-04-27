# /services/chroma_service.py

from repositories import chroma_repository

def search_documents(query: str, top_k: int = 5) -> list:
    """High-level semantic search: embed query + find documents."""
    query_vector = chroma_repository.embed_query(query)
    documents = chroma_repository.query_chroma(query_vector, top_k)
    return documents
