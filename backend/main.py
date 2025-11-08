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
import chromadb
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from sentence_transformers import SentenceTransformer

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

@app.on_event("startup")
async def startup_event():
    """
    Initialize models and database pool on startup.
    """
    global pool, embedding_model, generative_model
    pool = await asyncpg.create_pool(DATABASE_URL)
    logging.info("PostgreSQL connection pool created.")
    
    logging.info("Loading Sentence Transformer model...")
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    logging.info("Embedding model loaded.")

    logging.info("Loading Generative model...")
    generative_model = genai.GenerativeModel('gemini-2.5-flash-lite')
    logging.info("Generative model loaded.")


# --- gRPC Service ---
class DataVaultService(datavault_pb2_grpc.DataVaultServiceServicer):
    async def Ingest(self, request, context):
        try:
            data = json.loads(request.data)
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
                    record_id, encrypted_data_b64.encode('utf-8'), request.data_type, data_hash
                )
            
            return datavault_pb2.IngestResponse(id=str(record_id), status="OK")
        except Exception as e:
            logging.error(f"Error ingesting data: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error ingesting data: {e}")
            return datavault_pb2.IngestResponse(id="", status="ERROR")

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

class RAGResponse(BaseModel):
    response: str

@app.post("/rag_query", response_model=RAGResponse)
async def rag_query(query: RAGQuery):
    try:
        chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=8000)
        collection = chroma_client.get_collection(name="datavault_anonymized")
        
        query_embedding = embedding_model.encode(query.query).tolist()
        
        results = collection.query(query_embeddings=[query_embedding], n_results=5)
        documents = results.get('documents', [])
        if not documents or not documents[0]:
            raise HTTPException(status_code=404, detail="No relevant documents found.")
        
        context = "\n".join(documents[0])
        prompt = f"Based on the following context, please answer the user's query.\n\nContext:\n{context}\n\nUser Query:\n{query.query}"
        
        response = await generative_model.generate_content_async(prompt)
        return RAGResponse(response=response.text)
    except Exception as e:
        logging.error(f"Error during RAG query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "DataVault RAG API is running"}

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
    # The startup event will handle initialization
    await asyncio.gather(serve_grpc(), serve_fastapi())

if __name__ == "__main__":
    asyncio.run(main())