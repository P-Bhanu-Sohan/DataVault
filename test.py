import json
import requests
import time
import asyncio
import grpc
import os
from dotenv import load_dotenv
import asyncpg
import chromadb
from sentence_transformers import SentenceTransformer

from backend.generated import datavault_pb2, datavault_pb2_grpc
from backend.crypto_utils import decrypt_json

async def setup_test_data():
    """
    Ingests and embeds the first 5 records of each data category.
    """
    load_dotenv()
    print("--- Starting Test Data Setup ---")

    # --- Configuration ---
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/datavault")
    SECRET_KEY = os.getenv("ENCRYPTION_KEY", "12345678901234567890123456789012").encode('utf-8')
    CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
    
    # Wait for services to be ready
    print("Waiting for services to start... (15s)")
    time.sleep(15)

    # 1. Load test data
    print("\n--- Step 1: Loading test data ---")
    with open('simulations/datasets/healthcare.json', 'r') as f:
        healthcare_samples = json.load(f)[:5]
    with open('simulations/datasets/finance.json', 'r') as f:
        finance_samples = json.load(f)[:5]
    print("Loaded 5 healthcare and 5 finance records.")

    # 2. Ingest data via gRPC
    print("\n--- Step 2: Ingesting data via gRPC ---")
    ingested_ids = []
    with grpc.insecure_channel('backend:50051') as channel:
        stub = datavault_pb2_grpc.DataVaultServiceStub(channel)
        for record in healthcare_samples:
            response = stub.Ingest(datavault_pb2.DataRecord(data_type='healthcare', data=json.dumps(record).encode()))
            print(f"Healthcare record ingested with ID: {response.id}, Status: {response.status}")
            if response.status == "OK":
                ingested_ids.append(response.id)
        for record in finance_samples:
            response = stub.Ingest(datavault_pb2.DataRecord(data_type='finance', data=json.dumps(record).encode()))
            print(f"Finance record ingested with ID: {response.id}, Status: {response.status}")
            if response.status == "OK":
                ingested_ids.append(response.id)
    print("Ingestion complete.")

    # 3. Embed data from PostgreSQL into ChromaDB
    print("\n--- Step 3: Embedding data into ChromaDB ---")
    db_pool = await asyncpg.create_pool(DATABASE_URL)
    chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=8000)
    collection_name = "datavault_anonymized_new"
    collection = chroma_client.get_or_create_collection(name=collection_name)
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    async with db_pool.acquire() as conn:
        for record_id in ingested_ids:
            row = await conn.fetchrow('SELECT data FROM encrypted_blobs WHERE id = $1', record_id)
            if row:
                encrypted_data_b64 = row['data'].decode('utf-8')
                decrypted_data = decrypt_json(encrypted_data_b64, SECRET_KEY)
                document = json.dumps(decrypted_data)
                embedding = embedding_model.encode(document).tolist()
                collection.add(embeddings=[embedding], documents=[document], ids=[record_id])
                print(f"Successfully embedded record {record_id} into ChromaDB.")
    
    print(f"Total items in '{collection_name}': {collection.count()}")
    await db_pool.close()
    print("Embedding complete.")
    print("\n--- Test Data Setup Complete ---")

if __name__ == "__main__":
    asyncio.run(setup_test_data())