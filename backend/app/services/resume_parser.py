import re
import io
from typing import Dict, Any, List, Optional
import pypdf
from ..models.schemas import ResumeParsedData

KNOWN_SKILLS = {
    # Programming & Languages
    "python": "Python", "javascript": "JavaScript", "typescript": "TypeScript", "sql": "SQL", "c++": "C++", "java": "Java", "bash": "Bash/Shell",
    # Frameworks & Libraries
    "fastapi": "FastAPI", "flask": "Flask", "django": "Django", "pydantic": "Pydantic", "sqlalchemy": "SQLAlchemy",
    "pytorch": "PyTorch", "tensorflow": "TensorFlow", "keras": "Keras", "scikit-learn": "Scikit-Learn", "sklearn": "Scikit-Learn",
    "pandas": "Pandas", "numpy": "NumPy", "scipy": "SciPy", "matplotlib": "Matplotlib", "seaborn": "Seaborn",
    "huggingface": "Hugging Face", "transformers": "Transformers", "langchain": "LangChain", "llamaindex": "LlamaIndex",
    # Data & Storage
    "postgresql": "PostgreSQL", "mysql": "MySQL", "sqlite": "SQLite", "mongodb": "MongoDB", "redis": "Redis", "chromadb": "ChromaDB", "faiss": "FAISS", "pinecone": "Pinecone",
    # Engineering & DevOps
    "docker": "Docker", "kubernetes": "Kubernetes", "git": "Git", "github actions": "GitHub Actions", "pytest": "PyTest", "postman": "Postman", "celery": "Celery", "rabbitmq": "RabbitMQ", "kafka": "Apache Kafka", "rest api": "RESTful APIs", "rest": "REST APIs", "graphql": "GraphQL", "grpc": "gRPC", "rag": "Retrieval-Augmented Generation (RAG)"
}

DOMAIN_KEYWORDS = {
    "nlp": "Natural Language Processing (NLP)",
    "computer vision": "Computer Vision",
    "llm": "Large Language Models (LLMs)",
    "recommendation system": "Recommendation Systems",
    "distributed systems": "Distributed Systems",
    "microservices": "Microservices Architecture",
    "cloud": "Cloud Computing",
    "fintech": "FinTech / Financial Systems",
    "healthtech": "Healthcare AI",
    "eda": "Exploratory Data Analysis"
}

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    try:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return ""

def parse_resume_content(raw_text: str) -> ResumeParsedData:
    lower_text = raw_text.lower()
    
    # 1. Extract email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', raw_text)
    email = email_match.group(0) if email_match else None
    
    # 2. Extract name (first non-empty line or heuristic)
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    name = "Candidate"
    if lines:
        for l in lines[:3]:
            if not any(char in l for char in ['@', 'http', '+', 'linkedin', 'github']):
                if len(l.split()) <= 4:
                    name = l
                    break
    
    # 3. Extract skills
    extracted_skills = []
    for key, display_name in KNOWN_SKILLS.items():
        pattern = r'\b' + re.escape(key) + r'\b'
        if re.search(pattern, lower_text):
            if display_name not in extracted_skills:
                extracted_skills.append(display_name)
                
    # 4. Extract domain exposure
    extracted_domains = []
    for key, domain in DOMAIN_KEYWORDS.items():
        pattern = r'\b' + re.escape(key) + r'\b'
        if re.search(pattern, lower_text):
            if domain not in extracted_domains:
                extracted_domains.append(domain)
                
    # 5. Extract experience estimation
    exp_matches = re.findall(r'(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience', lower_text)
    experience_years = float(exp_matches[0]) if exp_matches else None
    if not experience_years:
        grad_match = re.search(r'20(1\d|2[0-6])\s*[-–]\s*20(2[0-6])', raw_text)
        if grad_match:
            end_year = int("20" + grad_match.group(2))
            experience_years = max(0.5, 2026 - end_year)

    # 6. Concise technical summary
    skills_summary = ", ".join(extracted_skills[:8]) if extracted_skills else "General software development"
    domains_summary = ", ".join(extracted_domains) if extracted_domains else "Software Engineering"
    summary = f"Candidate proficient in {skills_summary} with applied exposure in {domains_summary}."
    
    return ResumeParsedData(
        name=name,
        email=email,
        skills=extracted_skills,
        technologies=extracted_skills,
        experience_years=experience_years or 1.0,
        domain_exposure=extracted_domains,
        summary=summary,
        raw_text=raw_text
    )
