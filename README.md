# 🚀 PG-AGI AI-Powered Role-Based Candidate Screening System

An intelligent, real-world technical screening platform simulating structured role-based technical interviews grounded in candidate resumes and authoritative textbook knowledge bases.

Developed for the **PG-AGI AI/ML & Backend Engineering Intern Assignment**.

---

## 🌟 Key Features

1. **Intelligent Resume Parsing:** Automatically extracts technical skills, tools, programming languages, and experience from PDF or text resumes using `pypdf` and heuristic entity extraction.
2. **Grounded RAG Pipeline (Retrieval-Augmented Generation):**
   - Ingests authoritative textbook knowledge bases (Tom Mitchell's *Machine Learning*, Andriy Burkov's *The Hundred-Page Machine Learning Book*, Andreas Müller, and Distributed Systems standards).
   - Chunks text with sliding-window overlap (500-token chunks with 100-token overlap).
   - Generates vector representations and computes cosine similarity for grounded context retrieval.
3. **Dynamic, Non-Generic Question Generation:**
   - Synthesizes retrieved textbook context with candidate-specific skills.
   - Dynamically adapts across 5 distinct rounds (Foundations, Applied Scenarios, Tradeoffs, Edge Cases, and Adaptive Follow-Up).
4. **Real-Time Evaluation & Scoring:**
   - Scores candidate answers on a 0–10 scale based on technical depth and concept coverage.
   - Automatically detects key concepts covered vs missing technical blind spots.
5. **Session Continuity & Persistence:**
   - Full ACID-compliant SQLite relational database storing interview sessions, questions, answers, and audit logs.
6. **Executive Scorecard & Analytics:**
   - Generates overall percentage rating, hiring recommendations (Strong Hire, Hire, etc.), identified strengths, growth areas, and downloadable JSON reports.
7. **Dual-Architecture Frontend:**
   - Pre-packaged modern SPA served directly by FastAPI for immediate 1-click execution.
   - Clean Next.js / React source code in `frontend/nextjs-app` for modern component structure.

---

## 🛠️ System Architecture

```text
pgagi-candidate-screening/
├── run.py                             # 1-click execution launcher
├── requirements.txt                   # Production dependencies
├── PROJECT_DOCUMENT.md                # Full architectural design document
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI application & lifecycle events
│   │   ├── config.py                  # Environment settings & directory paths
│   │   ├── models/
│   │   │   ├── schemas.py             # Pydantic schemas
│   │   │   └── database.py            # SQLite database models & persistence
│   │   ├── services/
│   │   │   ├── resume_parser.py       # PDF/Text extraction & skill extraction
│   │   │   ├── rag_engine.py          # Vector store, chunking & semantic retrieval
│   │   │   ├── question_generator.py  # Grounded dynamic question generator
│   │   │   └── evaluator.py           # Multi-factor answer evaluation & scoring
│   │   └── api/
│   │       ├── interview.py           # Interview lifecycle REST endpoints
│   │       └── reports.py             # Analytics & JSON report export endpoints
│   └── knowledge_base/                # Authoritative textbook corpora
│       ├── ai_ml_engineer/            # Tom Mitchell & Burkov ML Foundations
│       ├── data_science_ml/           # Müller & Guido Data Science Foundations
│       └── backend_engineer/          # Distributed Systems & High-Scale Architecture
└── frontend/
    ├── static/                        # Production Dark-Theme UI (HTML, CSS, JS)
    └── nextjs-app/                    # Next.js / React standalone components
```

---

## ⚡ Quick Start Guide (Run in 30 Seconds)

### 1. Clone the Repository
```bash
git clone https://github.com/lsoumya014-netizen/pgagi-candidate-screening.git
cd pgagi-candidate-screening
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Application
```bash
python run.py
```

### 4. Access the Application
- **Interactive UI:** Open [http://localhost:8000](http://localhost:8000) in any web browser.
- **Interactive API Swagger Docs:** Open [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 📹 Demo Video Walkthrough Script (For Recording)

When recording your demo video (Loom / OBS), follow this 2-minute flow:

1. **Introduction (15 sec):** Introduce yourself (Soumya L) and state the project goal: an AI-powered role-based technical screening system with grounded RAG architecture.
2. **Resume Upload & Parsing (30 sec):** 
   - Show the candidate entry form.
   - Upload or paste a resume, click **Auto-Extract Skills**, and highlight the extracted technical skills (FastAPI, Python, SQL, Docker).
   - Select the target role (e.g. *Backend Engineering* or *AI/ML Engineer*).
3. **Interactive Grounded Interview (45 sec):**
   - Click **Start Technical Interview**.
   - Point out the **Grounded Knowledge Base Reference** box citing the specific textbook module.
   - Type in an answer explaining system design or ML mechanics, and click **Submit Answer**.
   - Show the instant real-time score (e.g., 8.5/10) and the covered vs missing concepts.
4. **Scorecard & Report Export (30 sec):**
   - Click through to the final summary view.
   - Show the overall score, hiring recommendation, strengths, and click **Export Evaluation JSON** to demonstrate persistence.

---

## 📄 License
MIT License. Built for PG-AGI Engineering Assignment.
