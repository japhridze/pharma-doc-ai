# pharma-doc-ai
PharmaDocAI – AI/LLM-Powered GMP Document &amp; Batch Record Analyzer using Python + FastAPI + embeddings + (future) LLM + Azure + Terraform + Azure DevOps.


# PharmaDocAI – AI/LLM-Powered GMP Document & Batch Record Analyzer

PharmaDocAI is an experimental backend service that uses AI to analyze
pharmaceutical GMP documents and batch records.  
It is built with **Python, FastAPI, and modern MLOps practices** and
is intended as a learning / portfolio project aligned with the tech stack
used at **MIGx (healthcare & life science consulting)**.

## Tech Stack

- Python 3.11
- FastAPI + Uvicorn
- SQLAlchemy (async) + SQLite (local, later Azure SQL / Postgres)
- Basic rule-based + ML analysis (later: LLM, embeddings, vector DB)
- Docker
- Terraform (Azure)
- Azure DevOps Pipelines (YAML)

## Features (current)

- `POST /api/v1/batches/` – submit a GMP batch record text for analysis
- `GET /api/v1/batches/` – list analyzed batch records
- `GET /health` – health check

The analysis is currently heuristic and rule-based:
it looks for missing fields like temperature, signatures, and deviation justifications,
and computes a simple GMP risk score (0–100).

Roadmap:
- Integrate sentence embeddings + FAISS for semantic search across SOPs.
- Add LLM-based document review for deeper compliance checks.
- Containerize and deploy to Azure App Service using Terraform + Azure DevOps.
