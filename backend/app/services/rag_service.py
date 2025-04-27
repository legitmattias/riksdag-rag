# /services/rag_service.py

from . import chroma_service
from . import llm_service

def generate_answer(query: str, top_k: int = 5) -> dict:
    """Retrieve documents and generate final answer."""
    documents = chroma_service.query_chroma(query, top_k)

    # Build the context
    context = "\n\n".join(
        f"{doc['speaker']} ({doc['party']}, {doc['date']}):\n{doc['text']}"
        for doc in documents
    )

    prompt = f"""Svara på frågan baserat på följande utdrag från svenska riksdagsdebatter.
Använd endast information från dessa utdrag. Om du inte vet, skriv att du inte är säker.

Utdrag:
{context}

Fråga: {query}
Svar:"""

    answer = llm_service.call_openai_chat(prompt)

    return {
        "answer": answer,
        "sources": documents
    }