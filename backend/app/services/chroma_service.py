# /services/chroma_service.py

import chromadb
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Connect to ChromaDB
chroma_client = chromadb.PersistentClient(path="pipeline/chroma_storage")
collection = chroma_client.get_collection("speeches")

# OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def embed_query(query: str) -> list:
    """Embed the user's query."""
    response = openai_client.embeddings.create(
        model="text-embedding-ada-002",
        input=[query]
    )
    return response.data[0].embedding

def query_chroma(query: str, top_k: int = 5) -> list:
    """Semantic search ChromaDB for top-k relevant documents."""
    query_embedding = embed_query(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas"]
    )

    documents = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        documents.append({
            "text": doc,
            "speaker": meta.get("speaker"),
            "party": meta.get("party"),
            "date": meta.get("date")
        })

    return documents