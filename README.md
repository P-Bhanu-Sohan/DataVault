# DataVault

> A secure data pipeline that protects sensitive information while unlocking its value for AI-powered insights through Retrieval-Augmented Generation (RAG).

DataVault is a comprehensive framework designed to solve two of the biggest challenges in modern data management: **protection and utility**. It provides a secure-by-design pipeline to ingest and encrypt sensitive data, and a powerful, privacy-preserving mechanism to query that data using Large Language Models (LLMs).

## Table of Contents

- [The Vision: Protection and Utility](#the-vision-protection-and-utility)
- [Core Principles: Security and Privacy](#core-principles-security-and-privacy)
- [Real-World Applications](#real-world-applications)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Core Components](#core-components)

## The Vision: Protection and Utility

### The Motivation

How can organizations leverage the power of AI on their most sensitive data without compromising user privacy or security? Raw, sensitive data (like financial records or health information) is incredibly valuable for generating insights, but using it is fraught with risk. Exposing this data to third-party AI models or even internal analytics platforms can create significant security vulnerabilities.

### The Idea: A Dual-Purpose Pipeline

DataVault is designed as a two-part solution to this problem:

1.  **The Vault (Protection):** First, it acts as a digital fortress. It ingests sensitive data, immediately anonymizes it to remove personal identifiers, encrypts it into an indecipherable format, and stores it securely. This ensures the "data at rest" is fundamentally safe.

2.  **The RAG Engine (Utility):** Second, it provides a secure bridge to unlock the *meaning* of that data without exposing the raw contents. It allows users to ask natural language questions about their encrypted data and receive intelligent answers from an LLM (like Google's Gemini). This is achieved through a Retrieval-Augmented Generation (RAG) process that maintains privacy at every step.

The ultimate goal is to enable users to have a conversation with their data, asking questions like, *"What are the spending trends in the last quarter for our high-value customers?"* and get a useful, AI-generated answer, all while the underlying sensitive data remains securely encrypted and anonymized.

## Core Principles: Security and Privacy

DataVault's security model is built on key pillars that protect data throughout its lifecycle, both during storage and during AI-powered analysis.

### 1. Anonymization at the Edge

Before data is ever stored, it is stripped of its most sensitive identifiers.
- **PII Redaction (`anonymizer.py`):** Personally Identifiable Information is replaced with synthetic but structurally similar data.
- **Privacy Preservation:** This ensures that even if data is decrypted for analysis, it is difficult to trace back to a specific individual.

### 2. "Zero Memory" Encrypted Storage

The database is never a single point of failure for data security.
- **Strong Encryption (`crypto_utils.py`):** After anonymization, the data object is encrypted using **AES-256-CBC**.
- **Opaque Storage (`db/init.sql`):** The encrypted output is stored as a binary blob (`BYTEA`) in PostgreSQL. The database has "zero memory" of the cleartext information.

### 3. Privacy-Preserving RAG

The process of querying the data with an LLM is designed to protect the source information.
- **In-Memory Decryption:** For the RAG process, data is only decrypted in-memory, just-in-time.
- **Vectorization of Anonymized Data:** The system creates vector embeddings from the *anonymized* data, not the original PII. These embeddings, which represent the semantic meaning of the data, are stored in a **ChromaDB** vector store.
- **Contextual Augmentation:** When a user asks a question, the system searches the vector store for relevant information and provides this anonymized context to the LLM. The LLM answers the question based on this context, without ever having access to the original, sensitive source data.

## Real-World Applications

-   **AI-Powered Healthcare Analytics:** A hospital can ask, *"What is the correlation between medication adherence and readmission rates for patients with chronic conditions?"* The RAG engine can provide a detailed analysis by querying anonymized patient records, without exposing any individual's health information.
-   **Intelligent Financial Fraud Detection:** A bank can query, *"Are there any unusual transaction patterns across our new accounts in the last month?"* The system can identify and summarize anomalies from a vast dataset of encrypted transactions.
-   **Conversational SaaS BI:** A multi-tenant SaaS platform can offer a feature where customers can "talk" to their own data, asking about user engagement, sales trends, or operational metrics, all while their data remains securely isolated and encrypted.

## Architecture

The DataVault architecture is divided into two main flows: the Ingestion Flow and the RAG Query Flow.

```
                               +----------------------+
                               |   Data Producers     |
                               +-----------+----------+
                                           | (gRPC Ingest)
                                           v
+------------------------------------------------------------------------+
|                               Backend Service                          |
|                            [ Ingestion Flow ]                          |
|                  1. Anonymize PII -> 2. Encrypt with AES-256             |
+------------------------------------+-----------------------------------+
                                     | (Encrypted Blob)
                                     v
                           +------------------+
                           |   PostgreSQL DB  |
                           +------------------+
                                     ^
                                     | (Read for RAG/Retrieve)
                                     |
+------------------------------------+-----------------------------------+
|                               Backend Service                          |
|                         [ RAG & Retrieval Flow ]                       |
|      1. Fetch & Decrypt Blob -> 2. Generate Embeddings or Return Data    |
+------------------+-----------------+-----------------------------------+
                   | (Embeddings)      | (Anonymized Data via gRPC)
                   v                   v
         +------------------+      +------------------+
         |   ChromaDB       |      |   Client App     |
         | (Vector Store)   |      +------------------+
         +--------+---------+
                  ^
                  | (Similarity Search)
                  |
+-----------------+------------------------------------------------------+
|                               Backend Service                          |
|                             [ LLM Query Flow ]                           |
|   1. User Query -> Embed -> Search ChromaDB -> 2. Augment LLM Prompt     |
+------------------------------------+-----------------------------------+
                                     | (Answer from Gemini)
                                     v
                             +------------------+
                             |   UI / Client    |
                             +------------------+
```

## Getting Started

### Prerequisites

-   Docker & Docker Compose
-   An environment file `.env` in the root directory with your `GEMINI_API_KEY`.

### Running the Application

1.  **Build and start all services:** `docker-compose up --build`
2.  **Run the Ingestion Script:** `docker-compose exec backend python simulations/ingest.py`
3.  **Run the Test Script (includes embedding):** `docker-compose exec backend python test.py`

### Accessing the UI

The RAG query interface is available at: [http://localhost:8000](http://localhost:8000)

## Core Components

-   **/backend**: The main Python service running gRPC (for data handling) and FastAPI (for the RAG API).
-   **/proto**: gRPC service definitions.
-   **/simulations**: Scripts for generating and ingesting sample data.
-   **/UI**: A web interface for visualizing the pipeline and interacting with the RAG engine.
-   `docker-compose.yml`: Orchestrates all services (`backend`, `postgres`, `redis`, `chroma`).
-   `test.py`: An end-to-end test script that ingests data and prepares the ChromaDB vector store.
