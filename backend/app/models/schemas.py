from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class TargetRole(str, Enum):
    AI_ML_ENGINEER = "ai_ml_engineer"
    DATA_SCIENCE_ML = "data_science_ml"
    BACKEND_ENGINEER = "backend_engineer"

class ResumeParsedData(BaseModel):
    name: Optional[str] = "Candidate"
    email: Optional[str] = None
    skills: List[str] = []
    technologies: List[str] = []
    experience_years: Optional[float] = None
    domain_exposure: List[str] = []
    summary: str = ""
    raw_text: str = ""

class StartInterviewRequest(BaseModel):
    candidate_name: str
    email: str
    target_role: TargetRole
    resume_text: Optional[str] = None

class QuestionResponse(BaseModel):
    question_id: str
    session_id: str
    question_number: int
    total_questions: int
    topic: str
    question_text: str
    grounded_context: str
    difficulty: str

class SubmitAnswerRequest(BaseModel):
    session_id: str
    question_id: str
    answer_text: str

class AnswerEvaluation(BaseModel):
    question_id: str
    question_text: str
    candidate_answer: str
    score: float = Field(..., ge=0, le=10)
    feedback: str
    key_concepts_covered: List[str] = []
    missing_concepts: List[str] = []

class InterviewSessionSummary(BaseModel):
    session_id: str
    candidate_name: str
    email: str
    target_role: str
    status: str
    overall_score: float
    percentage: float
    total_questions_answered: int
    evaluations: List[AnswerEvaluation] = []
    strengths: List[str] = []
    areas_for_improvement: List[str] = []
    hiring_recommendation: str
    summary_report: str
    created_at: str
