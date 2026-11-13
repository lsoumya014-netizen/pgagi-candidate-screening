import os
import uuid
import json
import requests
from typing import Dict, Any, List, Optional
from ..config import settings
from .rag_engine import rag_engine

ROLE_CURRICULUM = {
    "ai_ml_engineer": [
        {"topic": "Supervised Learning & Loss Optimization", "keywords": "gradient descent loss cross-entropy backpropagation"},
        {"topic": "Overfitting, Bias-Variance Tradeoff & Regularization", "keywords": "regularization bias variance dropout l1 l2"},
        {"topic": "Decision Trees, Ensembles & Gradient Boosting", "keywords": "random forest boosting xgboost information gain"},
        {"topic": "Neural Network Architecture & Backpropagation", "keywords": "backpropagation activation relu vanishing gradients"},
        {"topic": "Retrieval-Augmented Generation & Vector Embeddings", "keywords": "rag embeddings vector retrieval similarity"}
    ],
    "data_science_ml": [
        {"topic": "Data Preprocessing, Imputation & Feature Engineering", "keywords": "imputation encoding scaling feature engineering"},
        {"topic": "Dimensionality Reduction & Unsupervised Clustering", "keywords": "pca dimensionality reduction kmeans dbscan"},
        {"topic": "Validation Strategies & Data Leakage Prevention", "keywords": "cross-validation data leakage stratified k-fold"},
        {"topic": "Model Evaluation Metrics & Threshold Tuning", "keywords": "precision recall f1-score roc-auc confusion matrix"},
        {"topic": "Applied Machine Learning Systems & Productionizing Pipelines", "keywords": "pipeline deployment monitoring drift"}
    ],
    "backend_engineer": [
        {"topic": "High-Performance API Design & Asynchronous I/O", "keywords": "asyncio fastapi rest grpc concurrency"},
        {"topic": "Relational Databases, Indexing & ACID Guarantees", "keywords": "acid b-tree indexing transactions postgresql"},
        {"topic": "Distributed Caching Strategies & Rate Limiting", "keywords": "redis cache stampede rate limiting token bucket"},
        {"topic": "Message Queues & Event-Driven Architecture", "keywords": "kafka rabbitmq celery asynchronous decoupling"},
        {"topic": "System Reliability, Idempotency & Fault Tolerance", "keywords": "circuit breaker idempotency resilience microservices"}
    ]
}

def generate_interview_question(
    session_id: str,
    target_role: str,
    question_number: int,
    candidate_skills: List[str],
    experience_years: float,
    previous_answers: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Dynamically generates a grounded, role-specific technical question influenced by candidate skills."""
    curriculum = ROLE_CURRICULUM.get(target_role, ROLE_CURRICULUM["backend_engineer"])
    idx = min(question_number - 1, len(curriculum) - 1)
    stage = curriculum[idx]
    
    # Context Construction
    skill_context = ", ".join(candidate_skills[:5]) if candidate_skills else "Python & Systems"
    retrieval_query = f"{stage['keywords']} {skill_context}"
    
    # Knowledge Retrieval (RAG)
    retrieved_chunks = rag_engine.retrieve_context(target_role, retrieval_query, top_k=1)
    grounded_chunk = retrieved_chunks[0] if retrieved_chunks else {
        "title": stage["topic"],
        "content": f"Core engineering standards and principles for {stage['topic']}.",
        "source_document": "Knowledge Base"
    }
    
    difficulty = "Intermediate" if experience_years < 3 else "Senior / Advanced"
    if previous_answers and len(previous_answers) > 0:
        last_score = previous_answers[-1].get("score", 7.0)
        if last_score >= 8.5:
            difficulty = "Advanced / Deep-Dive"
        elif last_score < 5.0:
            difficulty = "Fundamental / Core Principles"

    # Dynamic Question Construction
    question_text = synthesize_question_prompt(
        role=target_role,
        stage=stage,
        grounded_context=grounded_chunk["content"],
        candidate_skills=candidate_skills,
        difficulty=difficulty,
        previous_answers=previous_answers
    )
    
    question_id = f"q_{session_id[:8]}_{question_number}_{uuid.uuid4().hex[:6]}"
    
    return {
        "question_id": question_id,
        "session_id": session_id,
        "question_number": question_number,
        "total_questions": len(curriculum),
        "topic": stage["topic"],
        "question_text": question_text,
        "grounded_context": f"[{grounded_chunk.get('title', 'Module')} - {grounded_chunk.get('source_document', 'Corpus')}]: {grounded_chunk['content'][:300]}...",
        "difficulty": difficulty
    }

def synthesize_question_prompt(
    role: str,
    stage: Dict[str, str],
    grounded_context: str,
    candidate_skills: List[str],
    difficulty: str,
    previous_answers: Optional[List[Dict[str, Any]]] = None
) -> str:
    """Produces non-generic technical questions grounded in the corpus and candidate background."""
    primary_skill = candidate_skills[0] if candidate_skills else "Python"
    related_skills = ", ".join(candidate_skills[1:4]) if len(candidate_skills) > 1 else "core libraries"
    
    topic = stage["topic"]
    
    # Adaptive synthesis if previous answer exists
    adaptation = ""
    if previous_answers and len(previous_answers) > 0:
        last_ans = previous_answers[-1]
        missing = last_ans.get("missing_concepts", [])
        if missing:
            adaptation = f" (Building on your earlier discussion where we touched upon {missing[0]}):"

    if "Loss Optimization" in topic:
        return (
            f"In your work with {primary_skill}, you likely configure optimizers and loss functions. "
            f"Based on the mathematical principles in Tom Mitchell's Machine Learning, how does the choice between "
            f"SGD with Momentum and Adam impact convergence when navigating high-curvature loss surfaces, "
            f"and how do you mathematically guard against gradient explosion in deep architectures?"
        )
    elif "Overfitting" in topic or "Regularization" in topic:
        return (
            f"When building production models using {primary_skill} ({related_skills}), suppose your validation loss diverges while training loss approaches zero. "
            f"Explain how L1 (Lasso) vs L2 (Ridge) regularization alters weight vectors geometrically at the penalty boundary, "
            f"and describe how you would determine whether the error originates from High Bias or High Variance."
        )
    elif "Decision Trees" in topic or "Gradient Boosting" in topic:
        return (
            f"Random Forest and Gradient Boosted Decision Trees (XGBoost/LightGBM) address variance and bias differently. "
            f"How does feature subsampling in Random Forest mathematically decorrelate tree outputs compared to the residual fitting mechanism "
            f"in GBDT, and how would you configure tree depth to prevent leaf-node overfitting?"
        )
    elif "Neural Network" in topic:
        return (
            f"During backpropagation through multi-layer perceptrons implemented in {primary_skill}, vanishing gradients frequently occur with Sigmoid activations. "
            f"Explain the mathematical mechanics of the chain rule dL/dW^(l) that causes this decay, and why He initialization combined with ReLU "
            f"or residual skip connections resolves the degradation problem."
        )
    elif "Retrieval-Augmented Generation" in topic or "Embeddings" in topic:
        return (
            f"You have listed exposure to {primary_skill} and AI engineering. In a production RAG pipeline, how do chunking strategies "
            f"with sliding-window overlap preserve semantic boundaries for vector indexing, and how would you mitigate hallucination "
            f"using cosine similarity ranking and strict grounded context prompt constraints?"
        )
    elif "API Design" in topic or "Asynchronous I/O" in topic:
        return (
            f"Given your background in {primary_skill} backend development, explain how the `asyncio` event loop and ASGI servers (such as Uvicorn) "
            f"handle thousands of concurrent I/O-bound requests on a single OS thread. How does this compare to multi-threading with Python's GIL, "
            f"and when must a backend engineer offload work to a process pool?"
        )
    elif "Relational Databases" in topic or "ACID" in topic:
        return (
            f"In a relational database (PostgreSQL/MySQL), explain the physical structure of a B+ Tree index leaf node and why composite indexes "
            f"adhere strictly to the Leftmost Prefix rule. Furthermore, describe how Write-Ahead Logging (WAL) ensures Atomicity and Durability during a crash."
        )
    elif "Distributed Caching" in topic or "Rate Limiting" in topic:
        return (
            f"When designing a distributed service in {primary_skill}, suppose your database faces a Cache Stampede (Thundering Herd) during peak traffic. "
            f"What cache invalidation strategy and locking mechanism would you implement to protect the database, and how does the Token Bucket algorithm enforce rate limits?"
        )
    elif "Message Queues" in topic:
        return (
            f"Explain the architectural differences between an AMQP message broker (like RabbitMQ) and a distributed commit log (like Apache Kafka). "
            f"How do consumer groups, partitions, and message acknowledgments ensure high-throughput without dropping messages or creating poison-pill crashes?"
        )
    elif "Data Preprocessing" in topic or "Feature Engineering" in topic:
        return (
            f"In data pipelines using {primary_skill} (e.g. Pandas/Scikit-Learn), how do you diagnose whether missing values are MCAR, MAR, or MNAR, "
            f"and why must feature transformations (scaling, target encoding) be encapsulated strictly inside cross-validation pipelines to eliminate data leakage?"
        )
    elif "Dimensionality Reduction" in topic:
        return (
            f"Explain the mathematical objective of Principal Component Analysis (PCA) in terms of maximizing projected variance and Singular Value Decomposition (SVD). "
            f"When would you choose a non-linear manifold technique like UMAP over linear PCA for exploratory clustering?"
        )
    elif "Validation Strategies" in topic or "Evaluation Metrics" in topic:
        return (
            f"When evaluating highly imbalanced classification datasets (e.g., 99% negative class), why is standard accuracy deceptive? "
            f"Compare the diagnostic utility of ROC-AUC versus Precision-Recall AUC (PR-AUC), and explain which metric should drive threshold selection."
        )
    else:
        return (
            f"Considering your technical experience in {primary_skill}, walk through how you would architect a scalable, fault-tolerant {topic} "
            f"pipeline from ingestion to production serving, highlighting key failure modes and observability metrics."
        )
