"""
The Interview Agent owns interview state and orchestrates the other
agents/tools. Routes stay thin — all decision-making funnels through
here, per the "AI Interview Agent" section of the spec.
"""
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

import models
from tools.question_tool import select_next_question
from tools.evaluation_tool import evaluate_answer

MAX_QUESTIONS = 8


def greeting_for(user_name: str, company: str) -> str:
    return (
        f"Hello {user_name}. Welcome to your mock interview for {company}. "
        f"This is a Company-Focused Practice session, not an exact replica of "
        f"{company}'s real questions. Let's begin."
    )


async def start_interview(db: Session, interview: models.Interview,
                           resume_context: Optional[str] = None) -> models.Question:
    """Create and persist the first question."""
    q = await select_next_question(
        company=interview.company, role=interview.role, domain=interview.domain,
        experience_level=interview.experience_level, interview_type=interview.interview_type,
        difficulty=interview.difficulty, asked_questions=[], last_answer=None,
        last_score=None, topics_covered=[], resume_context=resume_context,
    )
    question = models.Question(
        interview_id=interview.id, order_index=0, text=q["text"],
        topic=q["topic"], difficulty=q["difficulty"], is_followup=False,
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


async def submit_answer_and_advance(
    db: Session, interview: models.Interview, current_question: models.Question,
    transcript: str, resume_context: Optional[str] = None,
) -> Dict[str, Any]:
    """Records the answer, evaluates it, updates difficulty/topics, and
    either returns the next question or marks the interview complete."""

    answer = models.Answer(question_id=current_question.id, transcript=transcript)
    db.add(answer)

    eval_result = await evaluate_answer(
        current_question.text, transcript, interview.domain, interview.role,
        interview.experience_level,
    )
    evaluation = models.Evaluation(
        question_id=current_question.id,
        technical_correctness=eval_result.get("technical_correctness", 5),
        relevance=eval_result.get("relevance", 5),
        completeness=eval_result.get("completeness", 5),
        communication=eval_result.get("communication", 5),
        clarity=eval_result.get("clarity", 5),
        confidence=eval_result.get("confidence", 5),
        structure=eval_result.get("structure", 5),
        overall_score=eval_result.get("overall_score", 5),
        feedback=eval_result.get("feedback"),
        suggested_answer=eval_result.get("suggested_answer"),
    )
    db.add(evaluation)

    # Adapt difficulty based on this answer's score
    score = eval_result.get("overall_score", 5)
    if score >= 7 and interview.difficulty != "hard":
        interview.difficulty = "hard" if interview.difficulty == "medium" else "medium"
    elif score < 5 and interview.difficulty != "easy":
        interview.difficulty = "medium" if interview.difficulty == "hard" else "easy"

    topics = list(interview.topics_covered or [])
    if current_question.topic and current_question.topic not in topics:
        topics.append(current_question.topic)
    interview.topics_covered = topics

    prev_scores = [q.evaluation.overall_score for q in interview.questions if q.evaluation]
    interview.performance_running_score = round(sum(prev_scores) / len(prev_scores), 2) if prev_scores else score

    next_index = current_question.order_index + 1
    interview_complete = next_index >= MAX_QUESTIONS

    next_question_out = None
    if not interview_complete:
        asked = [q.text for q in interview.questions]
        q = await select_next_question(
            company=interview.company, role=interview.role, domain=interview.domain,
            experience_level=interview.experience_level, interview_type=interview.interview_type,
            difficulty=interview.difficulty, asked_questions=asked, last_answer=transcript,
            last_score=score, topics_covered=topics, resume_context=resume_context,
        )
        next_question = models.Question(
            interview_id=interview.id, order_index=next_index, text=q["text"],
            topic=q["topic"], difficulty=q["difficulty"], is_followup=q["is_followup"],
        )
        db.add(next_question)
        db.commit()
        db.refresh(next_question)
        next_question_out = next_question
    else:
        interview.status = "completed"
        import datetime as dt
        interview.completed_at = dt.datetime.utcnow()
        db.commit()

    return {
        "evaluation": eval_result,
        "next_question": next_question_out,
        "interview_complete": interview_complete,
        "progress": {"current": next_index, "total": MAX_QUESTIONS},
    }
