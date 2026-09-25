"""Pydantic request/response schemas."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class StartInterviewRequest(BaseModel):
    company: str
    role: str
    domain: str
    experience_level: str
    interview_type: str
    user_name: Optional[str] = "Guest"
    use_resume: Optional[bool] = False


class QuestionOut(BaseModel):
    id: int
    order_index: int
    text: str
    topic: Optional[str] = None
    difficulty: str


class StartInterviewResponse(BaseModel):
    interview_id: int
    greeting: str
    first_question: QuestionOut
    total_planned_questions: int


class VoiceAnswerRequest(BaseModel):
    transcript: str


class VoiceAnswerResponse(BaseModel):
    acknowledgement: str
    evaluation_summary: Dict[str, Any]
    next_question: Optional[QuestionOut] = None
    interview_complete: bool
    progress: Dict[str, int]


class InterviewReportResponse(BaseModel):
    interview_id: int
    overall_score: float
    technical_score: float
    communication_score: float
    strengths: List[str]
    weak_areas: List[str]
    questions_answered_well: List[Dict[str, Any]]
    questions_needing_improvement: List[Dict[str, Any]]
    topics_to_study: List[str]
    roadmap: List[Dict[str, Any]]
    recommended_practice_questions: List[str]


class ResumeAnalyzeResponse(BaseModel):
    skills: List[str]
    projects: List[Dict[str, Any]]
    experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]


class LearningRoadmapRequest(BaseModel):
    company: Optional[str] = None
    role: str
    domain: str
    experience_level: str
    interview_type: Optional[str] = "Mixed Interview"


class CodeRunRequest(BaseModel):
    language: str
    code: str
