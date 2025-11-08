import json
import requests
import time
import asyncio

from simulations.ingest import ingest_data
from simulations.embed import embed_data

def query_rag_api(query: str):
    """
    Sends a query to the RAG API and prints the response.
    """
    print(f"\n--- Querying RAG API with: '{query}' ---")
    api_url = "http://localhost:8000/rag_query"
    payload = {"query": query}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(api_url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        print("RAG API Response:")
        print(response.json().get("response"))
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while querying the RAG API: {e}")

async def run_e2e_test():
    """
    Runs an end-to-end test of the DataVault pipeline.
    """
    print("--- Starting End-to-End Test ---")
    
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
    ingest_data(healthcare_samples, 'healthcare')
    ingest_data(finance_samples, 'finance')
    print("Ingestion complete.")

    # 3. Embed data from PostgreSQL into ChromaDB
    print("\n--- Step 3: Embedding data into ChromaDB ---")
    await embed_data()
    print("Embedding complete.")

    # 4. Query the RAG API
    print("\n--- Step 4: Querying the RAG API ---")
    query_rag_api("What are the risks of high-risk investments?")
    query_rag_api("What are common treatments for hypertension?")

    print("\n--- End-to-End Test Complete ---")

if __name__ == "__main__":
    asyncio.run(run_e2e_test())