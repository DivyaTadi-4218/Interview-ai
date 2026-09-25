from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
from database import get_db
from schemas import (
    StartInterviewRequest, StartInterviewResponse, QuestionOut,
    VoiceAnswerRequest, VoiceAnswerResponse, InterviewReportResponse,
)
from agents.interview_agent import start_interview, submit_answer_and_advance, greeting_for
from services.evaluation_service import build_report

router = APIRouter(prefix="/interviews", tags=["interviews"])


def _get_or_create_user(db: Session, name: str) -> models.User:
    user = db.query(models.User).filter(models.User.name == name).first()
    if not user:
        user = models.User(name=name)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def _resume_context(db: Session, user_id: int) -> Optional[str]:
    resume = db.query(models.ResumeData).filter(models.ResumeData.user_id == user_id).first()
    if not resume:
        return None
    parsed = resume.parsed or {}
    skills = ", ".join(parsed.get("skills", [])[:15])
    projects = "; ".join(p.get("title", "") for p in parsed.get("projects", [])[:5])
    return f"Skills: {skills}. Projects: {projects}"


@router.post("/start", response_model=StartInterviewResponse)
async def start(payload: StartInterviewRequest, db: Session = Depends(get_db)):
    user = _get_or_create_user(db, payload.user_name or "Guest")

    interview = models.Interview(
        user_id=user.id, company=payload.company, role=payload.role,
        domain=payload.domain, experience_level=payload.experience_level,
        interview_type=payload.interview_type, status="in_progress",
        difficulty="medium", current_question_index=0, topics_covered=[],
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)

    resume_ctx = _resume_context(db, user.id) if payload.use_resume else None
    first_q = await start_interview(db, interview, resume_context=resume_ctx)

    return StartInterviewResponse(
        interview_id=interview.id,
        greeting=greeting_for(user.name, payload.company),
        first_question=QuestionOut(
            id=first_q.id, order_index=first_q.order_index, text=first_q.text,
            topic=first_q.topic, difficulty=first_q.difficulty,
        ),
        total_planned_questions=8,
    )


@router.post("/{interview_id}/voice-answer", response_model=VoiceAnswerResponse)
async def voice_answer(interview_id: int, payload: VoiceAnswerRequest, db: Session = Depends(get_db)):
    interview = db.query(models.Interview).get(interview_id)
    if not interview:
        raise HTTPException(404, "Interview not found")
    if interview.status == "completed":
        raise HTTPException(400, "Interview already completed")

    current_question = interview.questions[-1] if interview.questions else None
    if not current_question:
        raise HTTPException(400, "No active question for this interview")

    resume_ctx = _resume_context(db, interview.user_id)
    result = await submit_answer_and_advance(
        db, interview, current_question, payload.transcript, resume_context=resume_ctx
    )

    score = result["evaluation"].get("overall_score", 5)
    if result["interview_complete"]:
        ack = "Thank you. That completes the interview — great effort! Your detailed report is ready."
    elif score >= 7:
        ack = "Good answer. Let's move to the next question."
    elif score < 5:
        ack = "Thanks for that. Let's clarify with a related question."
    else:
        ack = "Thank you. Let's move to the next question."

    next_q_out = None
    if result["next_question"]:
        nq = result["next_question"]
        next_q_out = QuestionOut(id=nq.id, order_index=nq.order_index, text=nq.text,
                                  topic=nq.topic, difficulty=nq.difficulty)

    return VoiceAnswerResponse(
        acknowledgement=ack,
        evaluation_summary={"overall_score": score, "feedback": result["evaluation"].get("feedback")},
        next_question=next_q_out,
        interview_complete=result["interview_complete"],
        progress=result["progress"],
    )


@router.get("/{interview_id}/next-question", response_model=QuestionOut)
def next_question(interview_id: int, db: Session = Depends(get_db)):
    interview = db.query(models.Interview).get(interview_id)
    if not interview or not interview.questions:
        raise HTTPException(404, "No question found")
    q = interview.questions[-1]
    return QuestionOut(id=q.id, order_index=q.order_index, text=q.text, topic=q.topic, difficulty=q.difficulty)


@router.post("/{interview_id}/complete")
def complete_interview(interview_id: int, db: Session = Depends(get_db)):
    interview = db.query(models.Interview).get(interview_id)
    if not interview:
        raise HTTPException(404, "Interview not found")
    import datetime as dt
    interview.status = "completed"
    interview.completed_at = dt.datetime.utcnow()
    db.commit()
    return {"status": "completed"}


@router.get("/{interview_id}/report", response_model=InterviewReportResponse)
async def get_report(interview_id: int, db: Session = Depends(get_db)):
    interview = db.query(models.Interview).get(interview_id)
    if not interview:
        raise HTTPException(404, "Interview not found")
    report = await build_report(db, interview)
    return InterviewReportResponse(**report)


@router.get("/history")
def history(user_name: str = "Guest", db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.name == user_name).first()
    if not user:
        return {"interviews": []}
    out = []
    for iv in sorted(user.interviews, key=lambda i: i.created_at, reverse=True):
        out.append({
            "id": iv.id, "company": iv.company, "role": iv.role, "domain": iv.domain,
            "interview_type": iv.interview_type, "status": iv.status,
            "score": iv.performance_running_score, "created_at": iv.created_at.isoformat(),
        })
    return {"interviews": out}
