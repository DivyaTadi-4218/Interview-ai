from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

import models
from database import get_db
from schemas import ResumeAnalyzeResponse
from services.resume_service import extract_text_from_pdf, analyze_resume

router = APIRouter(prefix="/resume", tags=["resume"])


def _get_or_create_user(db: Session, name: str) -> models.User:
    user = db.query(models.User).filter(models.User.name == name).first()
    if not user:
        user = models.User(name=name)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@router.post("/upload", response_model=ResumeAnalyzeResponse)
async def upload_resume(file: UploadFile = File(...), user_name: str = "Guest",
                         db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Please upload a PDF resume.")

    content = await file.read()
    text = extract_text_from_pdf(content)
    if not text.strip():
        raise HTTPException(400, "Could not extract text from this PDF.")

    parsed = await analyze_resume(text)
    user = _get_or_create_user(db, user_name)

    existing = db.query(models.ResumeData).filter(models.ResumeData.user_id == user.id).first()
    if existing:
        existing.raw_text = text
        existing.parsed = parsed
    else:
        db.add(models.ResumeData(user_id=user.id, raw_text=text, parsed=parsed))
    db.commit()

    return ResumeAnalyzeResponse(**parsed)


@router.post("/analyze", response_model=ResumeAnalyzeResponse)
def analyze_existing(user_name: str = "Guest", db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.name == user_name).first()
    resume = db.query(models.ResumeData).filter(models.ResumeData.user_id == user.id).first() if user else None
    if not resume:
        raise HTTPException(404, "No resume uploaded yet.")
    return ResumeAnalyzeResponse(**resume.parsed)
