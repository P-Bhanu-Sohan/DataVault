import redis
import json
import time
import os

def ingest_data_to_stream(redis_client, records, data_type, stream_name):
    """
    Ingests a list of records into a Redis Stream.
    """
    print(f"--- Ingesting {data_type} data into stream '{stream_name}' ---")
    for record in records:
        # The message for XADD must be a dictionary of bytes or strings
        message = {
            "data_type": data_type,
            "data": json.dumps(record)
        }
        record_id = redis_client.xadd(stream_name, message)
        print(f"  - Ingested {data_type} record with Stream ID: {record_id}")
    print(f"--- Finished ingesting {data_type} data ---\n")

def run():
    """
    Reads data from JSON files and pushes it to a Redis Stream.
    """
    redis_host = os.getenv("REDIS_HOST", "redis")
    stream_name = "datavault:raw_data_stream"

    print("--- Starting Redis Ingestion Simulation ---")
    print(f"Connecting to Redis at {redis_host}...")
    
    # Wait for Redis to be ready
    time.sleep(5)
    
    try:
        # decode_responses=True decodes responses from bytes to UTF-8
        r = redis.Redis(host=redis_host, port=6379, decode_responses=True)
        r.ping()
        print("Successfully connected to Redis.")
    except redis.exceptions.ConnectionError as e:
        print(f"Error connecting to Redis: {e}")
        return

    # Ingest healthcare data
    with open('/app/simulations/datasets/healthcare.json', 'r') as f:
        healthcare_data = json.load(f)[:5]
        ingest_data_to_stream(r, healthcare_data, 'healthcare', stream_name)

    # Ingest finance data
    with open('/app/simulations/datasets/finance.json', 'r') as f:
        finance_data = json.load(f)[:5]
        ingest_data_to_stream(r, finance_data, 'finance', stream_name)
    
    print("--- Ingestion Simulation Complete ---")

if __name__ == '__main__':
    run()