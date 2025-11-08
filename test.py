import asyncio
import grpc
import json
import os
import asyncpg
import uuid
from dotenv import load_dotenv

import datavault_pb2
import datavault_pb2_grpc

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/datavault")

async def run_test():
    # Setup gRPC channel
    channel = grpc.aio.insecure_channel('localhost:50051')
    stub = datavault_pb2_grpc.DataVaultServiceStub(channel)

    # Setup direct DB connection
    conn = await asyncpg.connect(DATABASE_URL)

    try:
        print("--- Starting Mini Test ---")

        # --- Test Healthcare Data ---
        print("\n--- Testing Healthcare Data ---")
        healthcare_file_path = '/app/simulations/datasets/healthcare.json'
        with open(healthcare_file_path, 'r') as f:
            healthcare_data_samples = json.load(f)[:3] # Take 3 samples

        for i, record in enumerate(healthcare_data_samples):
            print(f"\n--- Healthcare Record {i+1} ---")
            print(f"Original Data: {record}")

            # 1. Ingest data via gRPC
            response = await stub.Ingest(datavault_pb2.DataRecord(data_type='healthcare', data=json.dumps(record).encode()))
            print(f"Ingestion Response: ID={response.id}, Status={response.status}")

            if response.status == "OK":
                record_id = uuid.UUID(response.id)

                # 2. Verify direct DB access (should be encrypted)
                db_row = await conn.fetchrow('SELECT data FROM encrypted_blobs WHERE id = $1', record_id)
                if db_row:
                    encrypted_blob_from_db = db_row['data']
                    print(f"Direct DB Access (Encrypted Blob): {encrypted_blob_from_db[:50]}... (truncated for brevity)")
                    print(f"  (This blob should be unreadable without decryption key)")
                else:
                    print("Error: Encrypted blob not found in DB.")

                # 3. Verify decryption via gRPC (should be anonymized)
                retrieve_response = await stub.Retrieve(datavault_pb2.IngestResponse(id=response.id))
                decrypted_data = json.loads(retrieve_response.data.decode('utf-8'))
                print(f"Decrypted Data (via gRPC Retrieve): {decrypted_data}")
                print(f"  (Verify names and age are anonymized compared to original data)")
            else:
                print(f"Ingestion failed for record {i+1}.")

        # --- Test Finance Data ---
        print("\n--- Testing Finance Data ---")
        finance_file_path = '/app/simulations/datasets/finance.json'
        with open(finance_file_path, 'r') as f:
            finance_data_samples = json.load(f)[:3] # Take 3 samples

        for i, record in enumerate(finance_data_samples):
            print(f"\n--- Finance Record {i+1} ---")
            print(f"Original Data: {record}")

            # 1. Ingest data via gRPC
            response = await stub.Ingest(datavault_pb2.DataRecord(data_type='finance', data=json.dumps(record).encode()))
            print(f"Ingestion Response: ID={response.id}, Status={response.status}")

            if response.status == "OK":
                record_id = uuid.UUID(response.id)

                # 2. Verify direct DB access (should be encrypted)
                db_row = await conn.fetchrow('SELECT data FROM encrypted_blobs WHERE id = $1', record_id)
                if db_row:
                    encrypted_blob_from_db = db_row['data']
                    print(f"Direct DB Access (Encrypted Blob): {encrypted_blob_from_db[:50]}... (truncated for brevity)")
                    print(f"  (This blob should be unreadable without decryption key)")
                else:
                    print("Error: Encrypted blob not found in DB.")

                # 3. Verify decryption via gRPC (should be anonymized)
                retrieve_response = await stub.Retrieve(datavault_pb2.IngestResponse(id=response.id))
                decrypted_data = json.loads(retrieve_response.data.decode('utf-8'))
                print(f"Decrypted Data (via gRPC Retrieve): {decrypted_data}")
                print(f"  (Verify names and age are anonymized compared to original data)")
            else:
                print(f"Ingestion failed for record {i+1}.")

        print("\n--- Mini Test Complete ---")

    finally:
        await channel.close()
        await conn.close()

if __name__ == "__main__":
    asyncio.run(run_test())
