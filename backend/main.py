import importlib.metadata
import sys

# Patch for importlib.metadata.packages_distributions
if sys.version_info < (3, 10):
    def packages_distributions():
        return {
            dist.metadata["name"]: [dist]
            for dist in importlib.metadata.distributions()
        }
    importlib.metadata.packages_distributions = packages_distributions

import asyncio
import grpc
from concurrent import futures
import logging
import os
from dotenv import load_dotenv
import json
import uuid
import hashlib
import asyncpg
import redis.asyncio as redis
import chromadb
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from sentence_transformers import SentenceTransformer
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from anonymizer import redact_names, anonymize_age
from crypto_utils import encrypt_json, decrypt_json

from backend.generated import datavault_pb2, datavault_pb2_grpc

# Load environment variables
load_dotenv()

# --- Configuration ---
SECRET_KEY = os.getenv("ENCRYPTION_KEY", "12345678901234567890123456789012").encode('utf-8')
if len(SECRET_KEY) != 32:
    raise ValueError("ENCRYPTION_KEY must be 32 bytes long")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/datavault")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file or environment variables")
genai.configure(api_key=GEMINI_API_KEY)

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")

# --- Globals ---
pool = None
embedding_model = None
generative_model = None

# --- FastAPI Application ---
app = FastAPI()

# Mount static files
app.mount("/resources", StaticFiles(directory="/app/UI/Resources"), name="resources")

@app.on_event("startup")
async def startup_event():
    global pool, embedding_model, generative_model
    pool = await asyncpg.create_pool(DATABASE_URL)
    logging.info("PostgreSQL connection pool created.")
    
    logging.info("Loading Sentence Transformer model...")
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    logging.info("Embedding model loaded.")

    logging.info("Loading Generative model...")
    generative_model = genai.GenerativeModel('gemini-1.5-flash')
    logging.info("Generative model loaded.")

# --- Data Processing Logic ---
async def process_and_store_data(data_payload, data_type):
    """
    Anonymizes, encrypts, and stores a single data record.
    """
    try:
        data = json.loads(data_payload)
        record_id = uuid.uuid4()
        anonymized_data = {**data}
        
        if 'first_name' in anonymized_data and 'last_name' in anonymized_data:
            anonymized_names = redact_names([{'first_name': anonymized_data['first_name'], 'last_name': anonymized_data['last_name']}])
            anonymized_data['first_name'] = anonymized_names[0]['first_name']
            anonymized_data['last_name'] = anonymized_names[0]['last_name']

        if 'age' in anonymized_data:
            anonymized_data['age'] = anonymize_age(anonymized_data['age'])
        
        encrypted_data_b64 = encrypt_json(anonymized_data, SECRET_KEY)
        data_hash = hashlib.sha256(encrypted_data_b64.encode('utf-8')).hexdigest()

        async with pool.acquire() as conn:
            await conn.execute(
                'INSERT INTO encrypted_blobs (id, data, data_type, data_hash) VALUES ($1, $2, $3, $4)',
                record_id, encrypted_data_b64.encode('utf-8'), data_type, data_hash
            )
        
        logging.info(f"Successfully processed and stored record {record_id} of type {data_type}")
        return record_id
    except Exception as e:
        logging.error(f"Error processing data: {e}")
        return None

# --- Redis Stream Consumer ---
async def redis_stream_consumer():
    stream_name = "datavault:raw_data_stream"
    group_name = "datavault_group"
    consumer_name = f"consumer-{uuid.uuid4()}"

    logging.info(f"Starting Redis consumer {consumer_name} for group {group_name} on stream {stream_name}")
    
    try:
        r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
        await r.ping()
        logging.info("Redis connection successful for consumer.")
    except Exception as e:
        logging.error(f"Redis connection failed for consumer: {e}")
        return

    try:
        await r.xgroup_create(stream_name, group_name, id='0', mkstream=True)
        logging.info(f"Consumer group '{group_name}' created for stream '{stream_name}'.")
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" in str(e):
            logging.info(f"Consumer group '{group_name}' already exists.")
        else:
            logging.error(f"Error creating consumer group: {e}")
            return

    while True:
        try:
            response = await r.xreadgroup(group_name, consumer_name, {stream_name: '>'}, count=10, block=5000)
            
            if not response:
                continue

            for stream, messages in response:
                for message_id, message_data in messages:
                    logging.info(f"Received message {message_id}: processing...")
                    await process_and_store_data(message_data['data'], message_data['data_type'])
                    await r.xack(stream_name, group_name, message_id)
                    logging.info(f"Acknowledged message {message_id}.")

        except Exception as e:
            logging.error(f"Error in Redis consumer loop: {e}")
            await asyncio.sleep(5) # Wait before retrying

# --- gRPC Service (Retrieve Only) ---
class DataVaultService(datavault_pb2_grpc.DataVaultServiceServicer):
    async def Retrieve(self, request, context):
        try:
            record_id = uuid.UUID(request.id)
            async with pool.acquire() as conn:
                row = await conn.fetchrow('SELECT data, data_type FROM encrypted_blobs WHERE id = $1', record_id)
                if not row:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details("Record not found")
                    return datavault_pb2.DataRecord(data_type="", data=b"")
                
                encrypted_data_b64 = row['data'].decode('utf-8')
                decrypted_data = decrypt_json(encrypted_data_b64, SECRET_KEY)
                
                return datavault_pb2.DataRecord(data_type=row['data_type'], data=json.dumps(decrypted_data).encode('utf-8'))
        except Exception as e:
            logging.error(f"Error retrieving data: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error retrieving data: {e}")
            return datavault_pb2.DataRecord(data_type="", data=b"")

# --- RAG Endpoint ---
class RAGQuery(BaseModel):
    query: str

@app.post("/rag_query", response_model=RAGResponse)
async def rag_query(query: RAGQuery):
    # ... (RAG implementation remains the same)
    pass

@app.get("/")
async def read_root():
    return FileResponse('/app/UI/index.html')

# --- Server Startup ---
async def serve_grpc():
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    datavault_pb2_grpc.add_DataVaultServiceServicer_to_server(DataVaultService(), server)
    server.add_insecure_port('[::]:50051')
    logging.info("Starting gRPC server on port 50051")
    await server.start()
    await server.wait_for_termination()

async def serve_fastapi():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    logging.info("Starting FastAPI server on port 8000")
    await server.serve()

async def main():
    logging.basicConfig(level=logging.INFO)
    await asyncio.gather(
        serve_grpc(), 
        serve_fastapi(),
        redis_stream_consumer()
    )

if __name__ == "__main__":
    asyncio.run(main())
