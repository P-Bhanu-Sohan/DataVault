import asyncio
import grpc
from concurrent import futures
import logging
import os
from dotenv import load_dotenv
import json
import uuid
import hashlib
import base64
import asyncpg # For PostgreSQL async operations

from anonymizer import redact_names, anonymize_age
from crypto_utils import encrypt_json, decrypt_json

import datavault_pb2
import datavault_pb2_grpc

# Load environment variables
load_dotenv()

# --- Configuration ---
SECRET_KEY = os.getenv("ENCRYPTION_KEY", "12345678901234567890123456789012").encode('utf-8') # 32-byte key
if len(SECRET_KEY) != 32:
    raise ValueError("ENCRYPTION_KEY must be 32 bytes long")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/datavault")

# PostgreSQL connection pool
pool = None

async def init_db_pool():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)
    logging.info("PostgreSQL connection pool created.")

# --- gRPC Service ---
class DataVaultService(datavault_pb2_grpc.DataVaultServiceServicer):
    def __init__(self):
        pass # No redis_client needed here anymore

    async def Ingest(self, request, context):
        try:
            data = json.loads(request.data)
            record_id = uuid.uuid4()

            # Prepare data for anonymization and encryption
            anonymized_data_for_encryption = {**data} # Start with a copy of the original data

            # Apply PII removal and anonymization to the data that will be encrypted
            original_first_name = anonymized_data_for_encryption.get('first_name', 'AnonF')
            original_last_name = anonymized_data_for_encryption.get('last_name', 'AnonL')
            original_age = anonymized_data_for_encryption.get('age')

            # Anonymize names
            anonymized_names = redact_names([{'first_name': original_first_name, 'last_name': original_last_name}])
            anonymized_data_for_encryption['first_name'] = anonymized_names[0]['first_name']
            anonymized_data_for_encryption['last_name'] = anonymized_names[0]['last_name']

            # Anonymize age
            if original_age is not None:
                anonymized_data_for_encryption['age'] = anonymize_age(original_age)
            
            # Encrypt the anonymized data
            encrypted_data_b64 = encrypt_json(anonymized_data_for_encryption, SECRET_KEY)
            data_hash = hashlib.sha256(encrypted_data_b64.encode('utf-8')).hexdigest()

            async with pool.acquire() as conn:
                # Insert only the encrypted blob into encrypted_blobs
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

async def serve_grpc():
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    datavault_pb2_grpc.add_DataVaultServiceServicer_to_server(DataVaultService(), server)
    server.add_insecure_port('[::]:50051')
    logging.info("Starting gRPC server on port 50051")
    await server.start()
    logging.info("gRPC server started.")
    await server.wait_for_termination()
    logging.info("gRPC server terminated.")

async def main():
    logging.basicConfig(level=logging.INFO)
    await init_db_pool() # Initialize the database pool
    
    # Start gRPC server
    await serve_grpc()

if __name__ == "__main__":
    asyncio.run(main())


