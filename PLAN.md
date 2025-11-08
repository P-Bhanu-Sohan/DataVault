# PLAN.md: Transforming DataVault into a Robust, Privacy-Preserving LLM Data Pipeline

## 1. Introduction

This document outlines a comprehensive plan to evolve the current DataVault prototype into a robust, production-ready application. The primary goal is to establish a secure, privacy-preserving data pipeline capable of feeding anonymized and encrypted data into a Retrieval-Augmented Generation (RAG) system, leveraging Redis Streams for efficient data ingestion and a Vector Database for semantic search.

The current setup demonstrates the core principles of PII removal, anonymization, and encryption before storage in a PostgreSQL database. The `test.py` script has proven the fundamental integrity of this process. This plan builds upon that foundation to introduce scalability, real-time processing capabilities, and advanced data utilization for LLMs.

## 2. Current State Review

The existing DataVault architecture consists of:

*   **Data Generators:** Python scripts (`simulations/generators/*.py`) that produce synthetic healthcare and finance datasets (`simulations/datasets/*.json`).
*   **gRPC Backend (Python):** `backend/main.py` acts as the central service.
    *   It receives raw data via a gRPC `Ingest` RPC.
    *   Performs PII removal (name anonymization, age anonymization) on the incoming data.
    *   Encrypts the *anonymized* data using AES-256-CBC.
    *   Stores the encrypted blob in a PostgreSQL table (`encrypted_blobs`).
    *   Provides a gRPC `Retrieve` RPC to fetch and decrypt these blobs.
*   **PostgreSQL Database:** Stores encrypted data blobs.
*   **Testing Script:** `test.py` verifies the end-to-end process of ingestion, encrypted storage, and successful decryption of anonymized data.
*   **Dockerized Environment:** Services are containerized using `docker-compose`.

## 3. Target Architecture

The target architecture introduces several new components and modifies existing ones to achieve the desired robustness, streaming capabilities, and RAG integration.

```
+-------------------+       +-------------------+       +-------------------+
| Data Generators   | ----> | Redis Stream      | ----> | Data Processor    |
| (simulations)     |       | (Encrypted Data)  |       | (Encrypt & Store) |
+-------------------+       +-------------------+       +-------------------+
                                                                  |
                                                                  v
                                                          +-------------------+
                                                          | PostgreSQL DB     |
                                                          | (Encrypted Blobs) |
                                                          +-------------------+
                                                                  |
                                                                  v
+-------------------+       +-------------------+       +-------------------+
| RAG Application   | <---- | Vector DB Query   | <---- | Decryption &      |
| (LLM Integration) |       | (Semantic Search) |       | Embedding Service |
+-------------------+       +-------------------+       +-------------------+
```

**Key Architectural Changes:**

*   **Redis Streams for Ingestion:** Data from generators will first be pushed to Redis Streams, acting as a message broker for real-time ingestion.
*   **Dedicated Data Processor Service:** A new service will consume from the Redis Stream, perform anonymization and encryption, and then store the encrypted data in PostgreSQL. This decouples ingestion from processing.
*   **PostgreSQL as Encrypted Data Store:** Remains the primary store for encrypted, anonymized data.
*   **Decryption & Embedding Service:** A new service responsible for:
    *   Retrieving encrypted data from PostgreSQL.
    *   Decrypting the data.
    *   Generating vector embeddings from the decrypted (anonymized) data.
    *   Storing these embeddings in a Vector Database.
*   **Vector Database:** Stores high-dimensional vector representations of the anonymized data, enabling semantic search.
*   **RAG Application:** A separate application that queries the Vector DB for relevant context based on user prompts, then uses an LLM to generate informed responses.

## 4. Phased Implementation Plan

### Phase 1: Redis Stream Integration (Producer Side)

**Goal:** Modify data generators to stream anonymized data to Redis Streams.

**Steps:**

1.  **Redis Setup:**
    *   Ensure Redis is properly configured in `docker-compose.yml` (already present).
    *   Verify Redis client libraries are available in the generator environment (e.g., `redis-py` for Python).
2.  **Modify Data Generators (`simulations/generators/*.py`):**
    *   Instead of writing to local JSON files, each generator will:
        *   Generate a single data record.
        *   Perform PII removal and anonymization (as currently done in the backend, but now shifted to the producer for immediate anonymization before streaming).
        *   Push the *anonymized* data record (as a JSON string) to a designated Redis Stream (e.g., `healthcare_stream`, `finance_stream`).
    *   **Decision Point:** Should anonymization happen *before* Redis Stream, or *after* by a dedicated processor? For "Zero Memory" and privacy-by-design, anonymizing *before* streaming is safer if the stream itself is not fully encrypted. Given the current backend handles anonymization, we will keep anonymization in the backend for now, and generators will push *raw* data to Redis Streams, which will then be consumed by the backend for anonymization and encryption. This simplifies the generators.
3.  **Update `simulations/ingest.py`:**
    *   Modify `ingest.py` to act as a Redis Stream producer.
    *   It will read from the JSON files, and for each record, push the *raw* data to the appropriate Redis Stream.
    *   Remove gRPC `Ingest` calls from `ingest.py`.

### Phase 2: Encrypted Data to PostgreSQL (Consumer Side)

**Goal:** Modify the `backend` service to consume raw data from Redis Streams, perform anonymization and encryption, and store the encrypted blobs in PostgreSQL.

**Steps:**

1.  **Redis Stream Consumer in `backend/main.py`:**
    *   Implement a Redis Stream consumer within `backend/main.py` (or a new dedicated Python service).
    *   The consumer will continuously read new messages from the Redis Streams (e.g., `healthcare_stream`, `finance_stream`).
    *   For each message:
        *   Parse the raw data.
        *   Perform PII removal and anonymization (using `anonymizer.py`).
        *   Encrypt the *anonymized* data (using `crypto_utils.py`).
        *   Store the encrypted blob in the `encrypted_blobs` table in PostgreSQL.
    *   Remove the gRPC `Ingest` RPC from `backend/main.py` as ingestion will now be stream-based.
2.  **Error Handling & Idempotency:**
    *   Implement robust error handling for Redis Stream consumption and PostgreSQL writes.
    *   Ensure message processing is idempotent to prevent duplicate entries in case of retries.
3.  **Monitoring:** Add metrics for stream lag, processing rate, and error rates.

### Phase 3: Vector Database Integration

**Goal:** Introduce a new service to decrypt data from PostgreSQL, generate embeddings, and store them in a Vector DB.

**Steps:**

1.  **Choose a Vector Database:**
    *   **Recommendation:** `pgvector` (if PostgreSQL is sufficient for vector search) or a dedicated service like Pinecone, Weaviate, Qdrant for more advanced features and scalability. For initial implementation, `pgvector` is simpler to integrate.
2.  **New Decryption & Embedding Service (Python):**
    *   Create a new Python service (e.g., `embedding_service.py`) with its own Dockerfile and `docker-compose.yml` entry.
    *   This service will:
        *   Periodically (or event-driven, e.g., via a new Redis Stream for "new encrypted data IDs") query `encrypted_blobs` in PostgreSQL for new or unprocessed records.
        *   Retrieve encrypted blobs.
        *   Decrypt the blobs (using `crypto_utils.py`).
        *   Generate vector embeddings from the *decrypted, anonymized* data.
            *   **Recommendation:** Use a pre-trained sentence transformer model (e.g., from Hugging Face `sentence-transformers` library) to convert text data into dense vectors.
        *   Store the generated vectors (along with the `original_id` from `encrypted_blobs` and potentially some anonymized metadata) in the chosen Vector Database.
3.  **Vector DB Schema:** Define the schema for the Vector DB to store vectors and associated metadata.
4.  **Update `encrypted_blobs` schema (optional):** Add a flag or timestamp to `encrypted_blobs` to track which records have been processed by the embedding service.

### Phase 4: Retrieval-Augmented Generation (RAG)

**Goal:** Implement an application that uses the Vector DB for retrieval and an LLM for generation.

**Steps:**

1.  **RAG Application Service (Python/FastAPI):**
    *   Create a new Python service (e.g., `rag_service.py`) with its own Dockerfile and `docker-compose.yml` entry.
    *   This service will expose an API endpoint (e.g., `/query`).
2.  **User Query Processing:**
    *   When a user submits a query:
        *   Generate an embedding for the user's query using the *same embedding model* used in Phase 3.
        *   Perform a similarity search in the Vector DB to retrieve the top-k most relevant anonymized data chunks/vectors.
3.  **Context Augmentation:**
    *   Retrieve the full anonymized data corresponding to the top-k vectors from the Vector DB (or by using the `original_id` to retrieve from PostgreSQL and decrypt).
    *   Construct a prompt for the LLM that includes the user's query and the retrieved anonymized context.
4.  **LLM Integration:**
    *   **Recommendation:** Integrate with a suitable LLM API (e.g., OpenAI GPT, Google Gemini, Hugging Face models).
    *   Send the augmented prompt to the LLM.
    *   Receive and return the LLM's generated response.
5.  **Privacy Considerations:** Ensure that the RAG application *never* exposes original PII and only operates on anonymized data.

### Phase 5: Robustness, Monitoring, and Scalability

**Goal:** Enhance the entire system for production readiness.

**Steps:**

1.  **Comprehensive Error Handling:** Implement try-except blocks, retry mechanisms (e.g., for DB writes, Redis operations), and circuit breakers across all services.
2.  **Centralized Logging:** Integrate a logging framework (e.g., ELK stack, Grafana Loki) for all services.
3.  **Metrics & Monitoring:**
    *   Expose Prometheus-compatible metrics from each service (e.g., processing rates, error counts, latency, stream lag).
    *   Set up Grafana dashboards for visualization.
    *   Configure alerts for critical issues.
4.  **Scalability:**
    *   **Container Orchestration:** Migrate from `docker-compose` to Kubernetes for horizontal scaling, self-healing, and deployment management of all services.
    *   **Database Scaling:** Consider PostgreSQL replication, connection pooling optimization.
    *   **Redis Scaling:** Implement Redis Cluster for high availability and scalability.
5.  **Security Enhancements:**
    *   Secure API endpoints (authentication/authorization).
    *   Key management for `ENCRYPTION_KEY` (e.g., HashiCorp Vault, AWS KMS).
    *   Network policies between services.
6.  **Configuration Management:** Externalize configurations using environment variables, config maps (Kubernetes), or a dedicated configuration service.
7.  **CI/CD Pipeline:** Automate testing, building, and deployment of services.

## 5. Technology Choices (Recommendations)

*   **Redis Streams:** For message queuing and real-time data ingestion.
*   **PostgreSQL:** For structured storage of encrypted blobs.
*   **Vector Database:**
    *   **`pgvector`:** Excellent for initial integration if vector search needs are moderate and already using PostgreSQL.
    *   **Dedicated Vector DB (e.g., Pinecone, Weaviate, Qdrant):** For high-scale, high-performance semantic search.
*   **Embedding Models:** Hugging Face `sentence-transformers` library (e.g., `all-MiniLM-L6-v2`) for generating embeddings.
*   **LLM Integration:** OpenAI API, Google Gemini API, or self-hosted open-source LLMs (e.g., Llama 2 via Hugging Face `transformers`).
*   **Container Orchestration:** Kubernetes.
*   **Monitoring:** Prometheus + Grafana.
*   **Logging:** ELK Stack (Elasticsearch, Logstash, Kibana) or Grafana Loki.

## 6. Testing Strategy

*   **Unit Tests:** For individual functions (anonymization, encryption, embedding generation).
*   **Integration Tests:**
    *   Generator -> Redis Stream.
    *   Redis Stream -> Data Processor -> PostgreSQL.
    *   PostgreSQL -> Decryption & Embedding Service -> Vector DB.
    *   RAG Application (Vector DB query + LLM).
*   **End-to-End Tests:** Simulate the entire pipeline from data generation to RAG response.
*   **Performance Tests:** Measure throughput, latency, and resource utilization under load.
*   **Security Audits:** Regularly review for vulnerabilities, especially around data handling and key management.

## 7. Risks and Mitigation

*   **Data Leakage:**
    *   **Mitigation:** Strict adherence to anonymization and encryption protocols. Regular security audits. Ensure all intermediate data (e.g., in Redis Streams) is handled with appropriate security measures (e.g., TLS, access control).
*   **Anonymization Effectiveness:**
    *   **Mitigation:** Continuous evaluation of anonymization techniques. Regular review by privacy experts.
*   **Performance Bottlenecks:**
    *   **Mitigation:** Scalable architecture (Redis Streams, Kubernetes). Performance testing and profiling.
*   **LLM Hallucinations/Bias:**
    *   **Mitigation:** Careful prompt engineering. Human-in-the-loop review of RAG responses. Fine-tuning LLMs on domain-specific, anonymized data.
*   **Complexity of Distributed System:**
    *   **Mitigation:** Phased implementation. Robust monitoring and logging. Clear service boundaries.

This plan provides a roadmap for building a sophisticated, privacy-aware data pipeline for LLM applications. Each phase can be developed and tested incrementally.
