import json
import time
import asyncio
import os
import sys
from dotenv import load_dotenv
import asyncpg
import chromadb
from sentence_transformers import SentenceTransformer

# Ensure the simulations directory is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulations.ingest import run as run_ingestion
from backend.crypto_utils import decrypt_json

async def setup_test_data():
    """
    Triggers the Redis ingestion and then verifies and embeds the processed data.
    """
    load_dotenv()
    print("--- Starting Test Data Setup ---")

    # --- Configuration ---
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgres:5432/datavault")
    SECRET_KEY = os.getenv("ENCRYPTION_KEY", "12345678901234567890123456789012").encode('utf-8')
    CHROMA_HOST = os.getenv("CHROMA_HOST", "chroma")
    
    # Wait for services to be ready
    print("Waiting for services to start... (10s)")
    time.sleep(10)

    # 1. Run the ingestion script to push data to the Redis Stream
    print("\n--- Step 1: Running ingestion script to publish to Redis ---")
    run_ingestion()
    print("Ingestion script finished. Data is now in the Redis Stream.")

    # 2. Verify data has been processed from the stream into PostgreSQL
    print("\n--- Step 2: Verifying data processing in PostgreSQL ---")
    db_pool = await asyncpg.create_pool(DATABASE_URL)
    
    expected_records = 10 # 5 healthcare + 5 finance

    max_wait_time = 45  # seconds
    start_time = time.time()
    
    record_count = 0
    while time.time() - start_time < max_wait_time:
        try:
            async with db_pool.acquire() as conn:
                # Clear table for a clean test run
                if time.time() - start_time < 2: # Run only once at the beginning
                    await conn.execute('TRUNCATE TABLE encrypted_blobs;')
                    print("Cleared encrypted_blobs table for a clean test run.")

                record_count = await conn.fetchval('SELECT COUNT(*) FROM encrypted_blobs')
            
            if record_count >= expected_records:
                print(f"Success! Found {record_count} records in the database.")
                break
            
            print(f"Waiting for data to be processed... Found {record_count}/{expected_records} records.")
            await asyncio.sleep(3)
        except Exception as e:
            print(f"An error occurred while polling the database: {e}")
            await asyncio.sleep(3)

    if record_count < expected_records:
        print(f"Error: Timed out waiting for records. Found only {record_count}.")
        await db_pool.close()
        return

    # 3. Embed data from PostgreSQL into ChromaDB
    print("\n--- Step 3: Embedding data into ChromaDB ---")
    chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=8000)
    collection = chroma_client.get_or_create_collection(name="datavault_anonymized")
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    async with db_pool.acquire() as conn:
        rows = await conn.fetch('SELECT id, data FROM encrypted_blobs')
        print(f"Embedding {len(rows)} records into ChromaDB...")
        for row in rows:
            record_id = str(row['id'])
            encrypted_data_b64 = row['data'].decode('utf-8')
            decrypted_data = decrypt_json(encrypted_data_b64, SECRET_KEY)
            document = json.dumps(decrypted_data)
            embedding = embedding_model.encode(document).tolist()
            
            collection.upsert(embeddings=[embedding], documents=[document], ids=[record_id])
            print(f"  - Successfully embedded record {record_id}")
            
    await db_pool.close()
    print("Embedding complete.")
    print("\n--- Test Data Setup Complete ---")

if __name__ == "__main__":
    asyncio.run(setup_test_data())