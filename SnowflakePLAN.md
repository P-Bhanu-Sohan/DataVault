# Snowflake Integration Plan for Analytics

This document outlines a strategy for integrating Snowflake as a cloud data warehouse for the DataVault project. The goal is to enable powerful, large-scale analytics without impacting the primary ingestion and retrieval pipeline.

### 1. Architectural Approach: A Separate Analytics Pipeline

We will not replace the existing PostgreSQL database. PostgreSQL is well-suited for its current role as a transactional database (handling single-record lookups for the `Retrieve` gRPC call).

Instead, we will establish a separate, parallel pipeline to load data into Snowflake for analytics (OLAP).

- **Transactional Flow (Unchanged):**
  `ingest.py` → `Redis Stream` → `backend/main.py` → `PostgreSQL`
  This remains the "hot path" for fast ingestion and retrieval of individual records.

- **Analytical Flow (New):**
  `PostgreSQL` → `ETL Script` → `Snowflake`
  This will be a batch process that periodically moves data from the transactional database to the analytical warehouse.

### 2. Implementation Plan

1.  **Create an ETL (Extract, Transform, Load) Script:**
    - A new Python script (e.g., `etl_postgres_to_snowflake.py`) will be created.
    - This script will run on a schedule (e.g., once a day).

2.  **Extract:**
    - The script will connect to the PostgreSQL database and query for new data added since the last run.

3.  **Transform & Stage:**
    - The data remains encrypted. The main transformation is formatting it for bulk loading (e.g., as Parquet or CSV files).
    - These files will be uploaded to a cloud storage stage (like AWS S3), which is the most efficient way to load data into Snowflake.

4.  **Load:**
    - The script will then execute Snowflake's `COPY INTO` command to load the data from the S3 stage into a target table in Snowflake.

### 3. Benefits of This Approach

- **Separation of Concerns:** Keeps the fast, transactional application database separate from resource-intensive analytical queries. This ensures the `Retrieve` API remains fast.
- **Performance:** Leverages Snowflake's massively parallel processing engine, allowing you to run complex queries over huge datasets far more efficiently than you could in PostgreSQL.
- **Scalability:** Snowflake's architecture is built to scale compute and storage independently, providing a cost-effective and powerful platform for growing datasets.

---
