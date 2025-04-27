# /repositories/chroma_repository.py

import chromadb
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Connect to ChromaDB
chroma_client = chromadb.PersistentClient(path="../pipeline/chroma_storage_test")
collection = chroma_client.get_collection("speeches")

# OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def embed_query(query: str) -> list:
    """Embed the user's query into a vector."""
    print("[OpenAI] Embedding user query...")
    response = openai_client.embeddings.create(
        model="text-embedding-ada-002",
        input=[query]
    )
    return response.data[0].embedding

def query_chroma(query_vector: list, top_k: int = 5) -> list:
    """Query ChromaDB with embedded query vector."""
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas"]
    )

    documents = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        documents.append({
            "text": doc,
            "speaker": meta.get("speaker"),
            "party": meta.get("party"),
            "date": meta.get("date"),
            "document_id": meta.get("document_id"),
            "speech_number": meta.get("speech_number")
        })

    return documents
