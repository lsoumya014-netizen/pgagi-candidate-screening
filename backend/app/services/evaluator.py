import re
from typing import Dict, Any, List, Tuple
from ..models.schemas import AnswerEvaluation, InterviewSessionSummary

EVALUATION_RUBRIC = {
    "high_quality_indicators": [
        "tradeoff", "complexity", "concurrency", "asynchronous", "indexing", "b+ tree", "acid", "wal",
        "gradient", "backpropagation", "regularization", "overfitting", "variance", "bias", "sliding window",
        "cosine similarity", "embeddings", "precision", "recall", "auc", "pipeline", "cache stampede", "token bucket"
    ]
}

def evaluate_candidate_answer(
    question_text: str,
    candidate_answer: str,
    topic: str,
    grounded_context: str
) -> AnswerEvaluation:
    """Evaluates the candidate's answer against grounded knowledge corpus and technical depth."""
    answer_clean = candidate_answer.strip().lower()
    word_count = len(answer_clean.split())
    
    # 1. Base depth score on response completeness and terminology
    if word_count < 15:
        base_score = 3.0
        feedback = "Answer is overly brief and lacks technical explanation or architectural specifics."
    elif word_count < 40:
        base_score = 6.0
        feedback = "Good baseline answer, but could be strengthened with deeper architectural mechanics and concrete examples."
    elif word_count < 80:
        base_score = 8.0
        feedback = "Solid, comprehensive explanation showing good conceptual grasp and technical clarity."
    else:
        base_score = 9.0
        feedback = "Exceptional depth, thorough technical reasoning, and mature articulation of system tradeoffs."

    # 2. Concept extraction & keyword alignment
    context_tokens = set(re.findall(r'\b[a-zA-Z]{4,}\b', grounded_context.lower()))
    answer_tokens = set(re.findall(r'\b[a-zA-Z]{4,}\b', answer_clean))
    
    overlap = context_tokens.intersection(answer_tokens)
    key_concepts_covered = list(overlap)[:6]
    
    missing_candidates = context_tokens - answer_tokens
    # Filter stopwords from missing candidates
    ignore_set = {"this", "that", "from", "with", "based", "their", "where", "which", "system", "using", "order", "document", "module"}
    meaningful_missing = [m for m in missing_candidates if m not in ignore_set and len(m) > 4][:4]
    
    # Adjustment based on technical overlap
    if len(key_concepts_covered) >= 4:
        base_score = min(10.0, base_score + 1.0)
    elif len(key_concepts_covered) <= 1 and word_count >= 30:
        base_score = max(4.0, base_score - 1.0)
        
    final_score = round(max(1.0, min(10.0, base_score)), 1)
    
    return AnswerEvaluation(
        question_id="",
        question_text=question_text,
        candidate_answer=candidate_answer,
        score=final_score,
        feedback=feedback,
        key_concepts_covered=key_concepts_covered,
        missing_concepts=meaningful_missing
    )

def generate_session_summary(
    session: Dict[str, Any],
    answers: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Generates an end-to-end interview scorecard, radar metrics, and hiring recommendation."""
    if not answers:
        return {
            "overall_score": 0.0,
            "percentage": 0.0,
            "strengths": ["Interview not yet started."],
            "areas_for_improvement": ["Complete the interview rounds."],
            "recommendation": "Incomplete",
            "summary_report": "No responses submitted."
        }
        
    scores = [a["score"] for a in answers]
    avg_score = round(sum(scores) / len(scores), 2)
    percentage = round((avg_score / 10.0) * 100, 1)
    
    # Identify strengths from top answers
    all_covered = []
    all_missing = []
    for a in answers:
        all_covered.extend(a.get("concepts_covered", []))
        all_missing.extend(a.get("missing_concepts", []))
        
    strengths = []
    if avg_score >= 7.5:
        strengths.append("Demonstrates strong conceptual grasp of foundational principles and system boundaries.")
    if len(all_covered) >= 6:
        strengths.append(f"Effective domain vocabulary and accurate citation of core concepts ({', '.join(set(all_covered[:4]))}).")
    strengths.append(f"Clear problem formulation aligned with {session['target_role'].replace('_', ' ').title()} standards.")
    
    areas_for_improvement = []
    if avg_score < 7.0:
        areas_for_improvement.append("Deepen explanations of underlying mathematical mechanics and low-level algorithmic tradeoffs.")
    if all_missing:
        unique_missing = list(set(all_missing))[:3]
        areas_for_improvement.append(f"Strengthen coverage of edge-case concepts such as {', '.join(unique_missing)}.")
    areas_for_improvement.append("Incorporate more quantitative metrics (e.g. latency targets, asymptotic time/space bounds) in responses.")
    
    if avg_score >= 8.5:
        recommendation = "Strong Hire (Exceeds Bar)"
    elif avg_score >= 7.0:
        recommendation = "Hire (Meets Technical Bar)"
    elif avg_score >= 5.5:
        recommendation = "Leaning Hire (Good Potential with Targeted Mentorship)"
    else:
        recommendation = "Needs Further Preparation"
        
    summary_report = (
        f"Candidate {session['candidate_name']} completed a structured technical screening for the {session['target_role'].replace('_', ' ').title()} position. "
        f"Across {len(answers)} evaluated interview modules, the candidate achieved an overall rating of {avg_score}/10 ({percentage}%). "
        f"The interview demonstrated {strengths[0].lower()} Overall recommendation: {recommendation}."
    )
    
    return {
        "overall_score": avg_score,
        "percentage": percentage,
        "strengths": strengths,
        "areas_for_improvement": areas_for_improvement,
        "recommendation": recommendation,
        "summary_report": summary_report
    }
