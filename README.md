# AtlasDx - Rare Disease Diagnostic System

AtlasDx is an **AI-based diagnostic system** for early detection of rare diseases.  
It uses **RAG, semantic embeddings, and multi-agent reasoning** to generate **ranked disease predictions with explanations**.

---

## Features
- Step-based diagnosis workflow
- AI-powered symptom extraction
- Semantic similarity search
- Multi-agent reasoning system
- Explainable results with recommendations
- Clean and responsive UI

---

## Tech Stack

| Category            | Technology Used |
|--------------------|----------------|
| Frontend           | ![React](https://img.shields.io/badge/React-20232A?logo=react&logoColor=61DAFB) |
| Backend            | ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) |
| AI Framework       | ![LangGraph](https://img.shields.io/badge/LangGraph-000000?logo=data&logoColor=white) |
| Embeddings         | ![SentenceTransformers](https://img.shields.io/badge/SentenceTransformers-FF6F00?logo=ai&logoColor=white) |
| Vector Database    | ![ChromaDB](https://img.shields.io/badge/ChromaDB-5A67D8?logo=database&logoColor=white) |

---

## Setup

```bash
git clone https://github.com/kundana-kolanuvada/Rare_Disease_System
cd Rare_Disease_System

# Backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
