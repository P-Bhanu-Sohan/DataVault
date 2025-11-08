import os
import json
import asyncpg
import chromadb
from dotenv import load_dotenv
import asyncio
from sentence_transformers import SentenceTransformer

from backend.crypto_utils import decrypt_json

async def embed_data():
    """
    Fetches encrypted data from PostgreSQL, decrypts it, generates embeddings
    using a Sentence Transformer model, and stores them in ChromaDB.
    """
    load_dotenv()

    # --- Configuration ---
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/datavault")
    SECRET_KEY = os.getenv("ENCRYPTION_KEY", "12345678901234567890123456789012").encode('utf-8')
    CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")

    # --- Initialize Clients ---
    db_pool = await asyncpg.create_pool(DATABASE_URL)
    chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=8000)
    collection = chroma_client.get_or_create_collection(name="datavault_anonymized")
    
    # Load the Sentence Transformer model
    print("Loading Sentence Transformer model...")
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Model loaded.")

    print("Fetching encrypted records from PostgreSQL...")
    async with db_pool.acquire() as conn:
        records = await conn.fetch('SELECT id, data FROM encrypted_blobs')
        print(f"Found {len(records)} records to process.")

        for record in records:
            encrypted_data_b64 = record['data'].decode('utf-8')
            
            # 1. Decrypt the data
            decrypted_data = decrypt_json(encrypted_data_b64, SECRET_KEY)
            document = json.dumps(decrypted_data)
            doc_id = str(record['id'])

            # 2. Generate embedding
            print(f"Generating embedding for record {doc_id}...")
            embedding = embedding_model.encode(document).tolist()
            
            # 3. Store in ChromaDB
            collection.add(
                embeddings=[embedding],
                documents=[document],
                ids=[doc_id]
            )
            print(f"Successfully embedded record {doc_id} into ChromaDB.")

    await db_pool.close()
    print("Embedding process complete.")

async def main():
    await embed_data()

if __name__ == '__main__':
    asyncio.run(main())