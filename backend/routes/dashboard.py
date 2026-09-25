from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
from database import get_db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
def dashboard(user_name: str = "Guest", db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.name == user_name).first()
    if not user or not user.interviews:
        return {
            "interviews_completed": 0, "average_performance": 0, "technical_score": 0,
            "communication_score": 0, "strongest_domains": [], "weakest_domains": [],
            "recent_interviews": [], "learning_progress": 0, "recommended_next_practice": None,
        }

    completed = [iv for iv in user.interviews if iv.status == "completed"]
    domain_scores = Counter()
    domain_counts = Counter()
    tech_scores, comm_scores = [], []

    for iv in completed:
        for q in iv.questions:
            if q.evaluation:
                domain_scores[iv.domain] += q.evaluation.overall_score
                domain_counts[iv.domain] += 1
                tech_scores.append(q.evaluation.technical_correctness)
                comm_scores.append(q.evaluation.communication)

    domain_avgs = {d: round(domain_scores[d] / domain_counts[d], 1) for d in domain_scores if domain_counts[d]}
    ranked = sorted(domain_avgs.items(), key=lambda x: x[1], reverse=True)

    progress_rows = db.query(models.LearningProgress).filter(models.LearningProgress.user_id == user.id).all()
    learning_progress = 0
    if progress_rows:
        learning_progress = round(100 * sum(1 for p in progress_rows if p.completed) / len(progress_rows))

    recent = sorted(user.interviews, key=lambda i: i.created_at, reverse=True)[:5]

    return {
        "interviews_completed": len(completed),
        "average_performance": round(sum(iv.performance_running_score for iv in completed) / len(completed), 1) if completed else 0,
        "technical_score": round(sum(tech_scores) / len(tech_scores), 1) if tech_scores else 0,
        "communication_score": round(sum(comm_scores) / len(comm_scores), 1) if comm_scores else 0,
        "strongest_domains": [d for d, _ in ranked[:3]],
        "weakest_domains": [d for d, _ in ranked[-3:]] if ranked else [],
        "recent_interviews": [
            {"id": iv.id, "company": iv.company, "role": iv.role, "status": iv.status,
             "score": iv.performance_running_score, "created_at": iv.created_at.isoformat()}
            for iv in recent
        ],
        "learning_progress": learning_progress,
        "recommended_next_practice": ranked[-1][0] if ranked else None,
    }
