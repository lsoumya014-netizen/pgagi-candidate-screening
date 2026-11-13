import os
import sys
import uvicorn

if __name__ == "__main__":
    print("=" * 65)
    print("🚀 Starting PG-AGI AI Candidate Screening System")
    print("📡 Local Server: http://localhost:8000")
    print("📖 Interactive API Docs (Swagger): http://localhost:8000/docs")
    print("=" * 65)
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
