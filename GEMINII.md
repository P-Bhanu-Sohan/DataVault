You are a Staff Engineer at FAANG and have won 25 hackathons, you are to design this PRD step by step ensuring checks on the way.

Notes: We would first build a MVP locally using Docker and a data pipelines locally, then we would switch to Vultr and Snowflake.


Current State:
Building a MVP Ingestion layer which support the encryption for now and we are able to access the encrypted DB blobs.


Future Post MVP: 

Next ideas to showcase our prowess and systems thinking will be going to be:


We will focus on Vultr and Snowflake later once our initial MVP is ready.



# 🛡️ DataVault.AI — Privacy-Preserving AI Framework for Regulated Data  

## 🏆 Target Hackathon Tracks
- 🥇 Outright Winner  
- 🔒 Best Data Protection Hack  
- 🤖 Most Impactful AI Hack  
- 💡 Most Novel Use of AI  
- ❄️ MLH – Best Use of Snowflake  
- ☁️ MLH – Best Use of Vultr  
- 🧠 MLH – Best Use of Gemini API  

---

## 🚀 Overview
**DataVault.AI** is a secure, privacy-first AI framework that enables organizations to train and query **LLMs on anonymized healthcare and finance data**.  
It ensures sensitive information never leaves the system unprotected, while enabling **real-time insights** and **explainable reasoning** through **Gemini API** in Snowflake.

---

## 🏗️ Architecture Overview

### **Core Components**
1. **Simulated Data Generation**  

2. **Anonymization & Encryption Service (Vultr)**  

3. **Encrypted Blob Storage (PostgreSQL)**  

4. **Snowflake Analytical Layer**  

5. **Gemini API RAG & Insight Layer**  

6. **Frontend Dashboard**   
---

## 🔁 Data Flow Diagram

[Simulated Healthcare/Finance Data]
│
▼
[Anonymization + AES-256 Encryption Service - Vultr]
│
▼
[Redis Streams (Buffering)]
│
▼
[PostgreSQL - Encrypted Blob Storage]
│
▼
[Snowflake Analytical Layer]
│
▼
[Gemini API - RAG & Insight Generation]
│
▼
[Frontend Dashboard (React/Tailwind)]

## ⚙️ Technical Stack

| Component | Technology |
|-----------|------------|
| Backend | Python FastAPI / gRPC, Docker |
| Messaging | Redis Streams (Vultr) |
| Storage | PostgreSQL (encrypted blobs) |
| Compute | Vultr Cloud Instances (GPU for LLM inference) |
| Analytics | Snowflake (summaries & embeddings) |
| LLM Reasoning | Gemini API (via Snowflake Cortex) |
| Frontend | React + Tailwind |
| Security | AES-256 + anonymization masking + JWT Auth |

---
## 🧪 Simulation Scenarios

### Healthcare
- Input anonymized patient data (symptoms, vitals, treatment outcomes).  
- LLM generates **frequent condition summaries**.  
- Snowflake + Gemini produces **top emerging conditions** insights.  

### Finance
- Input anonymized transaction records.  
- LLM summarizes **irregular spending patterns**.  
- Gemini RAG explains anomalies and generates **explanations for unusual transactions**.

---

## 🏆 Why This Wins Each Track

| Track | Advantage |
|-------|-----------|
| Outright Winner | End-to-end AI + privacy + analytics system with working demo |
| Best Data Protection Hack | Data never leaves encrypted/anonymized; PostgreSQL + AES-256 storage |
| Most Impactful AI Hack | Secure insights for real-world healthcare and finance scenarios |
| Most Novel Use of AI | RAG + LLM on structured anonymized data for actionable insights |
| MLH – Best Use of Snowflake | Summaries, embeddings, RAG source directly within Snowflake |
| MLH – Best Use of Vultr | Hosts all microservices, Redis Streams, PostgreSQL, and LLM inference |
| MLH – Best Use of Gemini | Direct reasoning on anonymized summaries; explainable AI outputs |

---

## 🔜 Implementation Phases

| Phase | Task |
|-------|------|
| 1 | Setup Vultr Compute, Redis Streams, PostgreSQL |
| 2 | Build gRPC ingestion + anonymization + AES-256 encryption |
| 3 | Implement Redis buffering + PostgreSQL blob storage |
| 4 | Stream decrypted summaries into Snowflake |
| 5 | Integrate Gemini API for RAG insights |
| 6 | Build frontend dashboard with React + Tailwind |
| 7 | Test simulated scenarios for Healthcare & Finance |
