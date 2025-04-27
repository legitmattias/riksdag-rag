# /pipeline/chroma_check.py

import chromadb

def main():
    chroma_client = chromadb.PersistentClient(path="chroma_storage")
    collection = chroma_client.get_collection("speeches")

    count = collection.count()
    print(f"Chroma collection contains {count} embedded chunks.")

    sample = collection.peek(3)

    # sample is a dict: {'ids': [...], 'documents': [...], 'metadatas': [...], etc.}
    ids = sample['ids']
    documents = sample['documents']
    metadatas = sample['metadatas']

    for i in range(len(ids)):
        print(f"\nSample {i+1}:")
        print(f"ID: {ids[i]}")
        print(f"Speaker: {metadatas[i].get('speaker')}")
        print(f"Party: {metadatas[i].get('party')}")
        print(f"Date: {metadatas[i].get('date')}")
        print(f"Text snippet:\n{documents[i][:300]}...")
        print("-" * 40)

if __name__ == "__main__":
    main()
