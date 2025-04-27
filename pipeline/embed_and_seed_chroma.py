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
UPLOAD_CHECKPOINT_PATH = "./upload_checkpoint.txt"
BATCH_SIZE = 30
MAX_SPEECHES = None  # None = full, or e.g., 100 for test

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

def load_upload_checkpoint():
    """Load upload checkpoint if exists."""
    if os.path.exists(UPLOAD_CHECKPOINT_PATH):
        with open(UPLOAD_CHECKPOINT_PATH, "r") as f:
            return int(f.read().strip())
    return 0

def save_upload_checkpoint(batch_index):
    """Save upload checkpoint."""
    with open(UPLOAD_CHECKPOINT_PATH, "w") as f:
        f.write(str(batch_index))

def seed_chroma():
    """Main seeding process."""
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        speeches = json.load(f)

    print(f"Loaded {len(speeches)} speeches.")

    batch_texts = []
    batch_metadatas = []
    batch_ids = []

    speech_counter = 0
    for idx, speech in enumerate(tqdm(speeches, desc="Preparing chunks")):
        if MAX_SPEECHES and speech_counter >= MAX_SPEECHES:
            break

        text = speech.get("text", "")
        if not text:
            continue

        chunks = chunk_text(text)

        for chunk_idx, chunk in enumerate(chunks):
            chunk_id = f"{speech['document_id']}_{speech['speech_number']}_{chunk_idx}"
            metadata = {
                "speaker": speech.get("speaker"),
                "party": speech.get("party"),
                "date": speech.get("date"),
                "document_id": speech.get("document_id"),
                "speech_number": speech.get("speech_number"),
                "chunk_index": chunk_idx
            }

            batch_texts.append(chunk)
            batch_metadatas.append(metadata)
            batch_ids.append(chunk_id)

        speech_counter += 1

    print(f"Prepared {len(batch_texts)} chunks. Starting upload to ChromaDB...")

    # Load upload checkpoint
    last_uploaded_batch = load_upload_checkpoint()

    # Embed and store in batches
    total_batches = (len(batch_texts) + BATCH_SIZE - 1) // BATCH_SIZE

    for batch_index in tqdm(range(total_batches), desc="Uploading to Chroma"):
        if batch_index < last_uploaded_batch:
            continue  # Skip batches already uploaded

        batch_slice = slice(batch_index * BATCH_SIZE, (batch_index + 1) * BATCH_SIZE)
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

        # Save upload checkpoint after each batch
        save_upload_checkpoint(batch_index + 1)

    print("Finished seeding ChromaDB!")
    # Clear checkpoint after full success
    if os.path.exists(UPLOAD_CHECKPOINT_PATH):
        os.remove(UPLOAD_CHECKPOINT_PATH)

if __name__ == "__main__":
    seed_chroma()
