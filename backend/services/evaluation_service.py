"""Aggregates per-question evaluations into the final interview report."""
from typing import Any, Dict, List

from sqlalchemy.orm import Session

import models
from tools.learning_tool import generate_roadmap


def _avg(values: List[float]) -> float:
    return round(sum(values) / len(values), 1) if values else 0.0


async def build_report(db: Session, interview: models.Interview) -> Dict[str, Any]:
    questions = interview.questions
    evaluated = [(q, q.evaluation) for q in questions if q.evaluation is not None]

    overall_scores = [e.overall_score for _, e in evaluated]
    technical_scores = [e.technical_correctness for _, e in evaluated]
    communication_scores = [e.communication for _, e in evaluated]

    well = sorted(evaluated, key=lambda qe: qe[1].overall_score, reverse=True)[:3]
    weak = sorted(evaluated, key=lambda qe: qe[1].overall_score)[:3]

    strengths, weak_areas = [], []
    for q, e in evaluated:
        if e.overall_score >= 7 and q.topic:
            strengths.append(q.topic)
        if e.overall_score < 5 and q.topic:
            weak_areas.append(q.topic)
    strengths = sorted(set(strengths)) or ["Consistent engagement throughout the interview"]
    weak_areas = sorted(set(weak_areas)) or ["No major weak areas identified — keep practicing depth"]

    roadmap_days = await generate_roadmap(
        interview.company, interview.role, interview.domain,
        interview.experience_level, interview.interview_type,
    )

    recommended_questions = [q.text for q, e in weak] or [q.text for q in questions[:3]]

    return {
        "interview_id": interview.id,
        "overall_score": _avg(overall_scores),
        "technical_score": _avg(technical_scores),
        "communication_score": _avg(communication_scores),
        "strengths": strengths,
        "weak_areas": weak_areas,
        "questions_answered_well": [
            {"question": q.text, "score": e.overall_score, "feedback": e.feedback} for q, e in well
        ],
        "questions_needing_improvement": [
            {"question": q.text, "score": e.overall_score, "feedback": e.feedback,
             "suggested_answer": e.suggested_answer} for q, e in weak
        ],
        "topics_to_study": weak_areas,
        "roadmap": roadmap_days,
        "recommended_practice_questions": recommended_questions,
    }
