import asyncio
import psycopg2
import redis
import os
import json
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import logging
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)

def decrypt(encrypted_data_with_nonce):
    key = base64.b64decode(os.environ["ENCRYPTION_KEY"])
    aesgcm = AESGCM(key)
    nonce = encrypted_data_with_nonce[:12]
    ciphertext = encrypted_data_with_nonce[12:]
    decrypted_data = aesgcm.decrypt(nonce, ciphertext, None)
    return decrypted_data.decode('utf-8')

def summarize_data(data_type, data):
    if data_type == "healthcare":
        return f"Healthcare record for patient {data.get('patient_id', 'N/A')}: Diagnosis - {data.get('diagnosis', 'N/A')}, Treatment - {data.get('treatment_plan', 'N/A')}."
    elif data_type == "finance":
        return f"Finance transaction for account {data.get('account_hash', 'N/A')}: Type - {data.get('transaction_type', 'N/A')}, Amount - {data.get('amount', 'N/A')}."
    return "Unknown data type."

async def process_encrypted_blobs():
    conn = None
    try:
        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        cur = conn.cursor()
        
        # Create a Redis client
        r = redis.from_url(os.environ["REDIS_URL"])

        # Use a consumer group to ensure each message is processed only once
        stream_name = "ingestion_stream"
        group_name = "processor_group"
        consumer_name = "data_processor_consumer"

        try:
            r.xgroup_create(stream_name, group_name, id="0", mkstream=True)
        except redis.exceptions.ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise

        logging.info("Data processor started, waiting for messages...")

        while True:
            try:
                # Read messages from the stream
                messages = r.xreadgroup(group_name, consumer_name, {stream_name: ">"}, count=1, block=5000) # Block for 5 seconds
                
                if not messages:
                    continue

                for message in messages:
                    stream, msg_id, data = message
                    try:
                        original_id = data[b"id"].decode()
                        encrypted_data_with_nonce = data[b"data"]
                        data_type = data[b"data_type"].decode()

                        decrypted_json_str = decrypt(encrypted_data_with_nonce)
                        decrypted_data = json.loads(decrypted_json_str)
                        
                        summary = summarize_data(data_type, decrypted_data)
                        
                        summarized_id = str(uuid.uuid4())
                        cur.execute(
                            "INSERT INTO summarized_data (id, original_id, data_type, summary) VALUES (%s, %s, %s, %s)",
                            (summarized_id, original_id, data_type, summary)
                        )
                        conn.commit()
                        logging.info(f"Processed and summarized record {original_id}. Summary: {summary}")
                        
                        # Acknowledge the message
                        r.xack(stream_name, group_name, msg_id)

                    except Exception as e:
                        logging.error(f"Error processing message {msg_id}: {e}")
                        # NACK or retry logic could be added here
            except Exception as e:
                logging.error(f"Error reading from Redis stream: {e}")
            
            await asyncio.sleep(1) # Small delay to prevent busy-waiting
            
    except Exception as e:
        logging.error(f"Failed to connect to database or Redis: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Set dummy environment variables for local testing
    os.environ["DATABASE_URL"] = "postgresql://user:password@postgres/datavault"
    os.environ["REDIS_URL"] = "redis://redis:6379"
    os.environ["ENCRYPTION_KEY"] = base64.b64encode(AESGCM.generate_key(bit_length=256)).decode('utf-8')
    
    asyncio.run(process_encrypted_blobs())
