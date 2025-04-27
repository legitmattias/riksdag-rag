# /pipeline/embed_and_seed_chroma.py

import os
import json
import chromadb
import tiktoken
from openai import OpenAI
from tqdm import tqdm
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables (OpenAI API key)
env_path = Path(__file__).resolve().parents[1] / "backend" / ".env"
load_dotenv(dotenv_path=env_path)

# Settings
DATA_PATH = "./data/speeches.json"
CHROMA_STORAGE_PATH = "./chroma_storage"
BATCH_SIZE = 30  # Number of chunks to embed per OpenAI request
MAX_SPEECHES = 100  # Set to None for full, or e.g., 100 for test runs

# Initialize clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
chroma_client = chromadb.PersistentClient(path=CHROMA_STORAGE_PATH)
collection = chroma_client.get_or_create_collection("speeches")

# Tokenizer
tokenizer = tiktoken.encoding_for_model("text-embedding-ada-002")

def count_tokens(text: str) -> int:
    return len(tokenizer.encode(text))

def split_into_sentences(text: str):
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s for s in sentences if s]

def chunk_text(text: str):
    """Chunk speech text into chunks based on token limits."""
    max_tokens = 512
    min_tokens = 150

    sentences = split_into_sentences(text)
    chunks = []
    current_chunk = []
    current_token_count = 0

    for sentence in sentences:
        tokens_in_sentence = count_tokens(sentence)

        if current_token_count + tokens_in_sentence > max_tokens:
            if current_token_count >= min_tokens:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_token_count = 0

        current_chunk.append(sentence)
        current_token_count += tokens_in_sentence

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def embed_texts(texts: list) -> list:
    """Batch embed a list of texts."""
    response = openai_client.embeddings.create(
        model="text-embedding-ada-002",
        input=texts
    )
    return [item.embedding for item in response.data]

def seed_chroma():
    """Main seeding process."""
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        speeches = json.load(f)

    print(f"Loaded {len(speeches)} speeches.")

    batch_texts = []
    batch_metadatas = []
    batch_ids = []
    speech_counter = 0
    total_speeches = min(len(speeches), MAX_SPEECHES) if MAX_SPEECHES else len(speeches)
    
    # Prepare all chunks
    for speech in tqdm(speeches, total=total_speeches, desc="Preparing chunks"):
        if MAX_SPEECHES and speech_counter >= MAX_SPEECHES:
            break

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

        speech_counter += 1

    print(f"Prepared {len(batch_texts)} chunks. Starting upload to ChromaDB...")

    # Embed and store in batches
    for i in tqdm(range(0, len(batch_texts), BATCH_SIZE), desc="Uploading to Chroma"):
        batch_slice = slice(i, i + BATCH_SIZE)
        texts_batch = batch_texts[batch_slice]
        metadatas_batch = batch_metadatas[batch_slice]
        ids_batch = batch_ids[batch_slice]

        embeddings = embed_texts(texts_batch)

        collection.add(
            documents=texts_batch,
            embeddings=embeddings,
            metadatas=metadatas_batch,
            ids=ids_batch
        )

    print("Finished seeding ChromaDB")

if __name__ == "__main__":
    seed_chroma()
