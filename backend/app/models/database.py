import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from ..config import settings

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Sessions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        candidate_name TEXT NOT NULL,
        email TEXT NOT NULL,
        target_role TEXT NOT NULL,
        resume_text TEXT,
        skills_json TEXT,
        status TEXT DEFAULT 'in_progress',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Questions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        question_number INTEGER NOT NULL,
        question_text TEXT NOT NULL,
        topic TEXT NOT NULL,
        grounded_context TEXT NOT NULL,
        difficulty TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions (session_id)
    )
    """)
    
    # Answers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS answers (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        question_id TEXT NOT NULL,
        candidate_answer TEXT NOT NULL,
        score REAL NOT NULL,
        feedback TEXT NOT NULL,
        concepts_covered_json TEXT,
        missing_concepts_json TEXT,
        answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions (session_id),
        FOREIGN KEY (question_id) REFERENCES questions (id)
    )
    """)
    
    # Evaluations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evaluations (
        session_id TEXT PRIMARY KEY,
        overall_score REAL NOT NULL,
        percentage REAL NOT NULL,
        strengths_json TEXT,
        improvements_json TEXT,
        recommendation TEXT NOT NULL,
        summary_report TEXT NOT NULL,
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions (session_id)
    )
    """)
    
    conn.commit()
    conn.close()

def create_session(session_id: str, candidate_name: str, email: str, target_role: str, resume_text: str, skills: List[str]) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO sessions (session_id, candidate_name, email, target_role, resume_text, skills_json)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (session_id, candidate_name, email, target_role, resume_text, json.dumps(skills)))
    conn.commit()
    conn.close()

def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    data = dict(row)
    data["skills"] = json.loads(data["skills_json"]) if data["skills_json"] else []
    return data

def save_question(question_id: str, session_id: str, question_number: int, question_text: str, topic: str, grounded_context: str, difficulty: str) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO questions (id, session_id, question_number, question_text, topic, grounded_context, difficulty)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (question_id, session_id, question_number, question_text, topic, grounded_context, difficulty))
    conn.commit()
    conn.close()

def get_questions_for_session(session_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions WHERE session_id = ? ORDER BY question_number ASC", (session_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_answer(answer_id: str, session_id: str, question_id: str, answer_text: str, score: float, feedback: str, concepts_covered: List[str], missing_concepts: List[str]) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO answers (id, session_id, question_id, candidate_answer, score, feedback, concepts_covered_json, missing_concepts_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (answer_id, session_id, question_id, answer_text, score, feedback, json.dumps(concepts_covered), json.dumps(missing_concepts)))
    conn.commit()
    conn.close()

def get_answers_for_session(session_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT a.*, q.question_text, q.topic, q.grounded_context, q.difficulty, q.question_number
    FROM answers a
    JOIN questions q ON a.question_id = q.id
    WHERE a.session_id = ?
    ORDER BY q.question_number ASC
    """, (session_id,))
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["concepts_covered"] = json.loads(d["concepts_covered_json"]) if d["concepts_covered_json"] else []
        d["missing_concepts"] = json.loads(d["missing_concepts_json"]) if d["missing_concepts_json"] else []
        result.append(d)
    return result

def save_evaluation(session_id: str, overall_score: float, percentage: float, strengths: List[str], improvements: List[str], recommendation: str, summary_report: str) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO evaluations (session_id, overall_score, percentage, strengths_json, improvements_json, recommendation, summary_report)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (session_id, overall_score, percentage, json.dumps(strengths), json.dumps(improvements), recommendation, summary_report))
    cursor.execute("UPDATE sessions SET status = 'completed', updated_at = CURRENT_TIMESTAMP WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()

def get_evaluation(session_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM evaluations WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["strengths"] = json.loads(d["strengths_json"]) if d["strengths_json"] else []
    d["improvements"] = json.loads(d["improvements_json"]) if d["improvements_json"] else []
    return d
