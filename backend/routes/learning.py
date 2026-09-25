from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
from database import get_db
from schemas import LearningRoadmapRequest
from tools.learning_tool import generate_roadmap

router = APIRouter(prefix="/learning", tags=["learning"])


@router.post("/roadmap")
async def roadmap(payload: LearningRoadmapRequest, user_name: str = "Guest",
                   db: Session = Depends(get_db)):
    days = await generate_roadmap(
        payload.company, payload.role, payload.domain,
        payload.experience_level, payload.interview_type,
    )

    user = db.query(models.User).filter(models.User.name == user_name).first()
    if not user:
        user = models.User(name=user_name)
        db.add(user)
        db.commit()
        db.refresh(user)

    plan_key = f"{payload.role}-{payload.domain}"
    for d in days:
        exists = db.query(models.LearningProgress).filter(
            models.LearningProgress.user_id == user.id,
            models.LearningProgress.plan_key == plan_key,
            models.LearningProgress.day == d["day"],
        ).first()
        if not exists:
            db.add(models.LearningProgress(
                user_id=user.id, topic=d["topic"], day=d["day"],
                plan_key=plan_key, completed=False, content=d,
            ))
    db.commit()

    return {"plan_key": plan_key, "days": days}


@router.post("/progress/{progress_id}/complete")
def mark_complete(progress_id: int, db: Session = Depends(get_db)):
    row = db.query(models.LearningProgress).get(progress_id)
    if row:
        row.completed = True
        db.commit()
    return {"status": "ok"}
