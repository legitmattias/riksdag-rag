# /pipeline/embed_and_seed_chroma.py

import os
import json
import tiktoken
import chromadb
from openai import OpenAI
from typing import List
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables (OpenAI API key)
env_path = Path(__file__).resolve().parents[1] / "backend" / ".env"
load_dotenv(dotenv_path=env_path)

# Settings
DATA_PATH = "./data/speeches.json"
CHROMA_COLLECTION_NAME = "speeches"
TARGET_TOKENS = 300
MAX_TOKENS = 512
MIN_TOKENS = 150

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path="chroma_storage")

# Initialize or get collection
collection = chroma_client.get_or_create_collection(CHROMA_COLLECTION_NAME)

# Tokenizer
tokenizer = tiktoken.encoding_for_model("text-embedding-ada-002")

def count_tokens(text: str) -> int:
    """Count the number of tokens in a string."""
    return len(tokenizer.encode(text))

def split_into_sentences(text: str) -> List[str]:
    """Simple sentence splitter based on punctuation."""
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s for s in sentences if s]

def chunk_text(text: str) -> List[str]:
    """Chunk text into meaningful chunks based on token limits."""
    sentences = split_into_sentences(text)
    chunks = []
    current_chunk = []
    current_token_count = 0

    for sentence in sentences:
        tokens_in_sentence = count_tokens(sentence)

        if current_token_count + tokens_in_sentence > MAX_TOKENS:
            if current_token_count >= MIN_TOKENS:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_token_count = 0

        current_chunk.append(sentence)
        current_token_count += tokens_in_sentence

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def embed_text(text: str) -> List[float]:
    """Get embedding vector for a text using OpenAI."""
    response = openai_client.embeddings.create(
        model="text-embedding-ada-002",
        input=[text]
    )
    return response.data[0].embedding

def seed_chroma():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        speeches = json.load(f)

    print(f"Loaded {len(speeches)} speeches.")

    batch_texts = []
    batch_metadatas = []
    batch_ids = []

    for speech in speeches:

        text = speech.get("text", "")
        if not text:
            continue

        chunks = chunk_text(text)

        for idx, chunk in enumerate(chunks):
            chunk_id = f"{speech['document_id']}_{speech['speech_number']}_{idx}"
            metadata = {
                "speaker": speech.get("speaker"),
                "party": speech.get("party"),
                "date": speech.get("date"),
                "document_id": speech.get("document_id"),
                "speech_number": speech.get("speech_number"),
                "chunk_index": idx
            }

            batch_texts.append(chunk)
            batch_metadatas.append(metadata)
            batch_ids.append(chunk_id)

            if len(batch_ids) % 50 == 0:
                print(f"Prepared {len(batch_ids)} chunks...")

    # Upload to ChromaDB
    print(f"Uploading {len(batch_ids)} chunks to ChromaDB...")
    collection.add(
        documents=batch_texts,
        embeddings=[embed_text(text) for text in batch_texts],
        metadatas=batch_metadatas,
        ids=batch_ids
    )

    print("Finished seeding ChromaDB!")



if __name__ == "__main__":
    seed_chroma()
