import os
import re
import math
from pathlib import Path
from typing import List, Dict, Any, Tuple
from ..config import settings

class KnowledgeChunk:
    def __init__(self, chunk_id: str, role: str, document_name: str, module_title: str, content: str):
        self.chunk_id = chunk_id
        self.role = role
        self.document_name = document_name
        self.module_title = module_title
        self.content = content
        self.term_frequencies: Dict[str, float] = {}

class RAGEngine:
    def __init__(self):
        self.chunks: List[KnowledgeChunk] = []
        self.vocabulary: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.is_indexed: bool = False

    def tokenize(self, text: str) -> List[str]:
        cleaned = re.sub(r'[^a-zA-Z0-9_\-\s]', ' ', text.lower())
        tokens = [t.strip() for t in cleaned.split() if len(t.strip()) > 2]
        stopwords = {
            "the", "and", "for", "with", "that", "this", "from", "are", "which",
            "have", "has", "can", "using", "used", "into", "their", "such", "than",
            "been", "each", "were", "when", "will", "more", "also", "some", "only"
        }
        return [t for t in tokens if t not in stopwords]

    def chunk_text(self, text: str, chunk_size: int = 400, overlap: int = 80) -> List[Tuple[str, str]]:
        """Splits document text into logical module chunks with sliding window overlap."""
        sections = text.split("## ")
        chunks = []
        
        for section in sections:
            if not section.strip():
                continue
            lines = section.splitlines()
            title = lines[0].strip() if lines else "Core Concept"
            body = "\n".join(lines[1:]).strip()
            
            words = body.split()
            if len(words) <= chunk_size:
                chunks.append((title, body))
            else:
                start = 0
                while start < len(words):
                    end = min(start + chunk_size, len(words))
                    chunk_body = " ".join(words[start:end])
                    chunks.append((title, chunk_body))
                    if end == len(words):
                        break
                    start += (chunk_size - overlap)
        return chunks

    def ingest_knowledge_base(self) -> None:
        """Ingests all role-specific textbook and documentation corpora."""
        self.chunks.clear()
        kb_dir = settings.KNOWLEDGE_BASE_DIR
        
        if not kb_dir.exists():
            return
            
        doc_count = 0
        for role_dir in kb_dir.iterdir():
            if role_dir.is_dir():
                role_name = role_dir.name
                for file_path in role_dir.glob("*.md"):
                    try:
                        content = file_path.read_text(encoding="utf-8")
                        raw_chunks = self.chunk_text(content, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
                        for idx, (title, chunk_body) in enumerate(raw_chunks):
                            chunk_id = f"{role_name}_{file_path.stem}_{idx}"
                            chunk = KnowledgeChunk(
                                chunk_id=chunk_id,
                                role=role_name,
                                document_name=file_path.name,
                                module_title=title,
                                content=chunk_body
                            )
                            tokens = self.tokenize(chunk_body + " " + title)
                            tf: Dict[str, int] = {}
                            for t in tokens:
                                tf[t] = tf.get(t, 0) + 1
                            total = len(tokens) or 1
                            chunk.term_frequencies = {k: v / total for k, v in tf.items()}
                            self.chunks.append(chunk)
                        doc_count += 1
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
                        
        # Compute IDF
        total_chunks = len(self.chunks)
        doc_freq: Dict[str, int] = {}
        for chunk in self.chunks:
            for term in chunk.term_frequencies.keys():
                doc_freq[term] = doc_freq.get(term, 0) + 1
                
        self.idf = {
            term: math.log((1 + total_chunks) / (1 + count)) + 1.0
            for term, count in doc_freq.items()
        }
        self.is_indexed = True
        print(f"RAG Engine successfully ingested {len(self.chunks)} chunks across {doc_count} knowledge corpora.")

    def retrieve_context(self, role: str, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        """Vector retrieval matching query against role-specific knowledge base chunks."""
        if not self.is_indexed:
            self.ingest_knowledge_base()
            
        query_tokens = self.tokenize(query)
        if not query_tokens:
            query_tokens = self.tokenize(role)
            
        q_tf: Dict[str, int] = {}
        for t in query_tokens:
            q_tf[t] = q_tf.get(t, 0) + 1
            
        scored_chunks = []
        for chunk in self.chunks:
            if chunk.role != role and role != "all":
                continue
                
            score = 0.0
            for term, q_count in q_tf.items():
                if term in chunk.term_frequencies:
                    tf = chunk.term_frequencies[term]
                    idf = self.idf.get(term, 1.0)
                    score += (tf * idf * q_count)
                    
            # Boost score if title matches query
            title_tokens = self.tokenize(chunk.module_title)
            title_overlap = sum(1 for t in query_tokens if t in title_tokens)
            score += (title_overlap * 0.5)
            
            scored_chunks.append((score, chunk))
            
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        top_results = []
        for score, chunk in scored_chunks[:top_k]:
            top_results.append({
                "chunk_id": chunk.chunk_id,
                "role": chunk.role,
                "title": chunk.module_title,
                "content": chunk.content,
                "relevance_score": round(score, 4),
                "source_document": chunk.document_name
            })
        return top_results

rag_engine = RAGEngine()
