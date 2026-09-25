"""
Database models. Kept intentionally normalized but simple — every table
named in the spec (users, companies, roles, domains, interviews, questions,
answers, evaluations, learning_progress, resume_data) is represented.
"""
import datetime as dt
from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON, Boolean
)
from sqlalchemy.orm import relationship

from database import Base


def now():
    return dt.datetime.utcnow()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, default="Guest")
    created_at = Column(DateTime, default=now)

    interviews = relationship("Interview", back_populates="user")
    resume = relationship("ResumeData", uselist=False, back_populates="user")
    learning_progress = relationship("LearningProgress", back_populates="user")


class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)


class Domain(Base):
    __tablename__ = "domains"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)


class Interview(Base):
    __tablename__ = "interviews"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    company = Column(String)
    role = Column(String)
    domain = Column(String)
    experience_level = Column(String)
    interview_type = Column(String)

    status = Column(String, default="in_progress")  # in_progress | completed
    difficulty = Column(String, default="medium")
    current_question_index = Column(Integer, default=0)
    topics_covered = Column(JSON, default=list)
    performance_running_score = Column(Float, default=0.0)

    created_at = Column(DateTime, default=now)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="interviews")
    questions = relationship("Question", back_populates="interview", order_by="Question.order_index")


class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"))
    order_index = Column(Integer)
    text = Column(Text)
    topic = Column(String, nullable=True)
    difficulty = Column(String, default="medium")
    is_followup = Column(Boolean, default=False)

    interview = relationship("Interview", back_populates="questions")
    answer = relationship("Answer", uselist=False, back_populates="question")
    evaluation = relationship("Evaluation", uselist=False, back_populates="question")


class Answer(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    transcript = Column(Text)
    created_at = Column(DateTime, default=now)

    question = relationship("Question", back_populates="answer")


class Evaluation(Base):
    __tablename__ = "evaluations"
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"))

    technical_correctness = Column(Float, default=0)
    relevance = Column(Float, default=0)
    completeness = Column(Float, default=0)
    communication = Column(Float, default=0)
    clarity = Column(Float, default=0)
    confidence = Column(Float, default=0)
    structure = Column(Float, default=0)
    overall_score = Column(Float, default=0)
    feedback = Column(Text, nullable=True)
    suggested_answer = Column(Text, nullable=True)

    question = relationship("Question", back_populates="evaluation")


class LearningProgress(Base):
    __tablename__ = "learning_progress"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    topic = Column(String)
    day = Column(Integer)
    plan_key = Column(String)  # groups a roadmap together
    completed = Column(Boolean, default=False)
    content = Column(JSON, default=dict)  # explanation, concepts, questions, quiz

    user = relationship("User", back_populates="learning_progress")


class ResumeData(Base):
    __tablename__ = "resume_data"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    raw_text = Column(Text)
    parsed = Column(JSON, default=dict)  # skills, projects, experience, education
    uploaded_at = Column(DateTime, default=now)

    user = relationship("User", back_populates="resume")
