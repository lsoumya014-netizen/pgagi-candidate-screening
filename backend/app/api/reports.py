from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from ..models import database
from ..models.schemas import InterviewSessionSummary, AnswerEvaluation

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/summary/{session_id}", response_model=InterviewSessionSummary)
async def get_session_summary_endpoint(session_id: str):
    session = database.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")
        
    eval_data = database.get_evaluation(session_id)
    answers = database.get_answers_for_session(session_id)
    
    evaluations = [
        AnswerEvaluation(
            question_id=a["question_id"],
            question_text=a["question_text"],
            candidate_answer=a["candidate_answer"],
            score=a["score"],
            feedback=a["feedback"],
            key_concepts_covered=a["concepts_covered"],
            missing_concepts=a["missing_concepts"]
        ) for a in answers
    ]
    
    if not eval_data:
        # In-progress calculation
        scores = [a["score"] for a in answers]
        avg = round(sum(scores) / len(scores), 2) if scores else 0.0
        return InterviewSessionSummary(
            session_id=session_id,
            candidate_name=session["candidate_name"],
            email=session["email"],
            target_role=session["target_role"],
            status=session["status"],
            overall_score=avg,
            percentage=round(avg * 10, 1),
            total_questions_answered=len(answers),
            evaluations=evaluations,
            strengths=["Interview in progress."],
            areas_for_improvement=["Complete all remaining questions."],
            hiring_recommendation="Pending Final Question Submission",
            summary_report="Interview session is currently active.",
            created_at=session["created_at"]
        )
        
    return InterviewSessionSummary(
        session_id=session_id,
        candidate_name=session["candidate_name"],
        email=session["email"],
        target_role=session["target_role"],
        status=session["status"],
        overall_score=eval_data["overall_score"],
        percentage=eval_data["percentage"],
        total_questions_answered=len(answers),
        evaluations=evaluations,
        strengths=eval_data["strengths"],
        areas_for_improvement=eval_data["improvements"],
        hiring_recommendation=eval_data["recommendation"],
        summary_report=eval_data["summary_report"],
        created_at=session["created_at"]
    )

@router.get("/export/{session_id}")
async def export_report_endpoint(session_id: str):
    summary = await get_session_summary_endpoint(session_id)
    return JSONResponse(
        content=summary.dict(),
        headers={"Content-Disposition": f"attachment; filename=screening_report_{session_id}.json"}
    )
