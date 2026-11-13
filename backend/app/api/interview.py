import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from ..models.schemas import (
    StartInterviewRequest,
    QuestionResponse,
    SubmitAnswerRequest,
    AnswerEvaluation,
    ResumeParsedData,
    TargetRole
)
from ..models import database
from ..services.resume_parser import extract_text_from_pdf, parse_resume_content
from ..services.question_generator import generate_interview_question
from ..services.evaluator import evaluate_candidate_answer, generate_session_summary

router = APIRouter(prefix="/interview", tags=["Interview"])

@router.post("/parse-resume", response_model=ResumeParsedData)
async def parse_resume_endpoint(
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None)
):
    text_content = ""
    if file:
        content = await file.read()
        if file.filename.lower().endswith(".pdf"):
            text_content = extract_text_from_pdf(content)
        else:
            text_content = content.decode("utf-8", errors="ignore")
    elif raw_text:
        text_content = raw_text
    else:
        raise HTTPException(status_code=400, detail="Either a resume file or raw_text must be provided.")
        
    if not text_content.strip():
        raise HTTPException(status_code=400, detail="Could not extract readable text from the provided resume.")
        
    parsed_data = parse_resume_content(text_content)
    return parsed_data

@router.post("/start", response_model=QuestionResponse)
async def start_interview_endpoint(request: StartInterviewRequest):
    session_id = f"sess_{uuid.uuid4().hex[:12]}"
    
    resume_text = request.resume_text or ""
    parsed = parse_resume_content(resume_text) if resume_text else None
    skills = parsed.skills if parsed else ["Software Engineering", "Python"]
    
    # Create persistent session
    database.create_session(
        session_id=session_id,
        candidate_name=request.candidate_name,
        email=request.email,
        target_role=request.target_role.value,
        resume_text=resume_text,
        skills=skills
    )
    
    # Generate Question 1
    q1 = generate_interview_question(
        session_id=session_id,
        target_role=request.target_role.value,
        question_number=1,
        candidate_skills=skills,
        experience_years=parsed.experience_years if parsed else 1.0,
        previous_answers=None
    )
    
    # Save Question 1 to DB
    database.save_question(
        question_id=q1["question_id"],
        session_id=session_id,
        question_number=1,
        question_text=q1["question_text"],
        topic=q1["topic"],
        grounded_context=q1["grounded_context"],
        difficulty=q1["difficulty"]
    )
    
    return QuestionResponse(**q1)

@router.get("/question/{session_id}", response_model=QuestionResponse)
async def get_current_question_endpoint(session_id: str):
    session = database.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")
        
    questions = database.get_questions_for_session(session_id)
    answers = database.get_answers_for_session(session_id)
    
    if len(questions) > len(answers):
        # Current unanswered question
        q = questions[-1]
        return QuestionResponse(
            question_id=q["id"],
            session_id=session_id,
            question_number=q["question_number"],
            total_questions=5,
            topic=q["topic"],
            question_text=q["question_text"],
            grounded_context=q["grounded_context"],
            difficulty=q["difficulty"]
        )
        
    if len(answers) >= 5:
        raise HTTPException(status_code=400, detail="All interview questions have been answered. View the summary report.")
        
    # Generate next question
    next_num = len(answers) + 1
    next_q = generate_interview_question(
        session_id=session_id,
        target_role=session["target_role"],
        question_number=next_num,
        candidate_skills=session["skills"],
        experience_years=1.5,
        previous_answers=answers
    )
    
    database.save_question(
        question_id=next_q["question_id"],
        session_id=session_id,
        question_number=next_num,
        question_text=next_q["question_text"],
        topic=next_q["topic"],
        grounded_context=next_q["grounded_context"],
        difficulty=next_q["difficulty"]
    )
    return QuestionResponse(**next_q)

@router.post("/answer")
async def submit_answer_endpoint(request: SubmitAnswerRequest):
    session = database.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
        
    questions = database.get_questions_for_session(request.session_id)
    current_q = next((q for q in questions if q["id"] == request.question_id), None)
    if not current_q:
        raise HTTPException(status_code=404, detail="Question not found in this session.")
        
    # Evaluate answer
    eval_result = evaluate_candidate_answer(
        question_text=current_q["question_text"],
        candidate_answer=request.answer_text,
        topic=current_q["topic"],
        grounded_context=current_q["grounded_context"]
    )
    eval_result.question_id = request.question_id
    
    # Save Answer to DB
    answer_id = f"ans_{uuid.uuid4().hex[:10]}"
    database.save_answer(
        answer_id=answer_id,
        session_id=request.session_id,
        question_id=request.question_id,
        answer_text=request.answer_text,
        score=eval_result.score,
        feedback=eval_result.feedback,
        concepts_covered=eval_result.key_concepts_covered,
        missing_concepts=eval_result.missing_concepts
    )
    
    answers = database.get_answers_for_session(request.session_id)
    is_completed = len(answers) >= 5
    
    if is_completed:
        # Generate and save final evaluation
        summary = generate_session_summary(session, answers)
        database.save_evaluation(
            session_id=request.session_id,
            overall_score=summary["overall_score"],
            percentage=summary["percentage"],
            strengths=summary["strengths"],
            improvements=summary["areas_for_improvement"],
            recommendation=summary["recommendation"],
            summary_report=summary["summary_report"]
        )
        
    return {
        "evaluation": eval_result.dict(),
        "is_completed": is_completed,
        "questions_answered": len(answers),
        "total_questions": 5
    }
