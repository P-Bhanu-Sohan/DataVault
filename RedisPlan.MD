# Plan: Integrating Redis for a Hybrid Ingestion Pipeline

This document outlines the plan to evolve the DataVault service by integrating Redis Streams. The goal is to create a more resilient and scalable ingestion pipeline while retaining the efficiency of gRPC for data retrieval.

### 1. The Hybrid Approach: Asynchronous Ingestion, Synchronous Retrieval

We will adopt a hybrid model that uses the best tool for the job:

- **Redis Streams for Ingestion:** Data will be sent to a Redis Stream instead of directly to the backend. This is an *asynchronous* process that decouples the data producer from the consumer, acting as a durable buffer.
- **gRPC for Retrieval:** The existing `Retrieve` gRPC endpoint will be preserved for its high performance in *synchronous* request-response scenarios where a client needs immediate access to data.

### 2. Key Code Changes

**A. Producer (`simulations/ingest.py`)**
- **Role Change:** Will become a Redis Stream producer.
- **Logic:** Instead of making gRPC calls, it will connect to Redis and add data records to a stream (e.g., `datavault:raw_data_stream`). This allows the script to complete its job quickly without waiting for the backend to process the data.

**B. Consumer (`backend/main.py`)**
- **Role Change:** Will become a Redis Stream consumer.
- **Logic:** The gRPC `Ingest` RPC will be removed. In its place, a new process will continuously read data from the Redis Stream. For each message, it will perform the existing anonymization, encryption, and storage logic, acknowledging the message only after successful processing to ensure reliability.

### 3. Benefits of This Approach

- **Resilience:** If the backend service is down, data producers can continue to send data to the Redis Stream. The data will be processed once the backend recovers, preventing data loss.
- **Scalability:** The stream acts as a natural buffer, absorbing spikes in data volume. If processing becomes a bottleneck, we can scale by adding more backend consumers to the same stream without changing the producer.
- **Decoupling:** The data production and data processing services no longer need to know about each other directly, allowing them to be developed, deployed, and scaled independently.
