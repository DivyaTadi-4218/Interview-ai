"""
Question selection. Tries the LLM first (so questions are genuinely
adaptive to the candidate's running performance and history); falls back
to a curated static bank keyed by domain/interview type so the interview
still works end-to-end with zero API key configured.
"""
import random
from typing import Any, Dict, List, Optional

from services.llm_service import llm_service

FALLBACK_BANK: Dict[str, List[str]] = {
    "HR Interview": [
        "Tell me about yourself.",
        "Why do you want to work at this company?",
        "What are your greatest strengths?",
        "What is one weakness you're actively working on?",
        "Where do you see yourself in five years?",
        "Describe a time you handled conflict with a teammate.",
        "Why should we hire you over other candidates?",
    ],
    "Behavioral Interview": [
        "Tell me about a time you failed and what you learned from it.",
        "Describe a situation where you had to meet a tight deadline.",
        "Tell me about a time you disagreed with a manager's decision.",
        "Describe a time you had to learn something new very quickly.",
    ],
    "Project Interview": [
        "Can you walk me through a project you're proud of?",
        "What problem did that project solve?",
        "Why did you choose that particular technology stack?",
        "What was your specific contribution to the project?",
        "What was the hardest technical challenge you faced, and how did you solve it?",
        "What database did you use, and why?",
        "How did you test the project before shipping it?",
        "How would you improve the project if you revisited it today?",
        "What would need to change if the number of users grew 100x?",
    ],
    "Managerial Interview": [
        "How do you prioritize tasks across a team with competing deadlines?",
        "Tell me about a time you had to give difficult feedback.",
        "How do you handle underperformance on your team?",
    ],
    "Resume Interview": [
        "Walk me through your resume, starting with your most recent role.",
    ],
    "SQL Interview": [
        "What is the difference between WHERE and HAVING?",
        "Explain the difference between INNER JOIN and LEFT JOIN.",
        "What is a primary key versus a foreign key?",
        "How would you find duplicate rows in a table?",
        "What is normalization, and why does it matter?",
        "Explain indexing and when it can hurt write performance.",
    ],
    "AI/ML Interview": [
        "What is the difference between supervised and unsupervised learning?",
        "Explain overfitting and how you'd address it.",
        "What is the bias-variance tradeoff?",
        "How would you evaluate a classification model?",
        "What is a transformer architecture used for?",
    ],
    "Coding Interview": [
        "How would you approach reversing a linked list? Explain your logic out loud.",
        "How would you detect a cycle in a graph? Talk through the approach.",
        "Explain how you'd design an algorithm to find the two numbers in an array that sum to a target.",
    ],
    "_domain_default": {
        "Python": [
            "What are Python decorators and when would you use one?",
            "Explain the difference between a list and a tuple.",
            "What is the GIL, and how does it affect multithreading in Python?",
            "How does exception handling work in Python?",
        ],
        "Java": [
            "What is the difference between an interface and an abstract class?",
            "Explain how garbage collection works in the JVM.",
            "What are the four pillars of OOP, and can you give an example of each?",
        ],
        "JavaScript": [
            "Explain the difference between var, let, and const.",
            "What is a closure, and can you describe a practical use case?",
            "How does the event loop work in JavaScript?",
        ],
        "React": [
            "What is the difference between state and props?",
            "Explain how the useEffect hook works and a common pitfall with it.",
            "What is the virtual DOM, and why does it help performance?",
        ],
        "FastAPI": [
            "What is FastAPI, and what makes it different from Flask?",
            "How would you implement request validation in FastAPI?",
            "How does dependency injection work in FastAPI?",
        ],
        "Node.js": [
            "Explain the event-driven, non-blocking model of Node.js.",
            "What is middleware in the context of an Express/Node app?",
        ],
        "AWS": [
            "What is the difference between EC2 and Lambda?",
            "How would you design a highly available architecture on AWS?",
        ],
        "System Design": [
            "How would you design a URL shortener?",
            "How would you design a rate limiter?",
        ],
        "Database": [
            "What is database normalization, and what problem does it solve?",
            "Explain ACID properties in the context of transactions.",
        ],
        "DevOps": [
            "What is the difference between continuous integration and continuous deployment?",
            "How would you roll back a bad deployment safely?",
        ],
        "Cybersecurity": [
            "What is the difference between authentication and authorization?",
            "How would you defend against a SQL injection attack?",
        ],
        "Testing / QA": [
            "What is the difference between unit testing and integration testing?",
            "How would you prioritize which test cases to automate first?",
        ],
    },
}


def _fallback_question(domain: str, interview_type: str, asked: List[str]) -> str:
    pool: List[str] = []
    pool += FALLBACK_BANK.get(interview_type, [])
    pool += FALLBACK_BANK["_domain_default"].get(domain, [])
    if not pool:
        pool = FALLBACK_BANK["_domain_default"]["Python"]
    remaining = [q for q in pool if q not in asked]
    if not remaining:
        remaining = pool
    return random.choice(remaining)


async def select_next_question(
    company: str,
    role: str,
    domain: str,
    experience_level: str,
    interview_type: str,
    difficulty: str,
    asked_questions: List[str],
    last_answer: Optional[str],
    last_score: Optional[float],
    topics_covered: List[str],
    resume_context: Optional[str] = None,
) -> Dict[str, Any]:
    """Returns {"text": ..., "topic": ..., "difficulty": ..., "is_followup": bool}"""

    system = (
        "You are an experienced technical/HR interviewer conducting a "
        "Company-Focused Practice mock interview. You are NOT claiming to "
        "have real confidential questions from the company — you generate "
        "realistic practice questions in that company's typical style. "
        "Ask exactly one question at a time, tailored to the candidate's "
        "role, domain, experience level, interview type, and how well they "
        "answered the previous question. Never repeat a question already asked."
    )
    user = f"""
Company: {company}
Role: {role}
Domain: {domain}
Experience level: {experience_level}
Interview type: {interview_type}
Current difficulty: {difficulty}
Topics already covered: {topics_covered}
Questions already asked: {asked_questions}
Candidate's last answer: {last_answer!r}
Score of last answer (0-10, null if first question): {last_score}
Resume context (only use facts actually present, never invent): {resume_context or "N/A"}

Decide the single best next interview question. If the last answer was
strong (score >= 7), go deeper on the same topic or raise difficulty.
If weak (score < 5), ask a simpler clarifying/follow-up question on the
same concept rather than moving on. Otherwise progress to a new relevant
topic for this domain/role/interview type.

Return JSON: {{"text": "<question>", "topic": "<short topic label>",
"difficulty": "easy|medium|hard", "is_followup": true|false}}
"""
    result = await llm_service.complete_json(system, user, max_tokens=400)
    if result and result.get("text"):
        return {
            "text": result["text"],
            "topic": result.get("topic", domain),
            "difficulty": result.get("difficulty", difficulty),
            "is_followup": bool(result.get("is_followup", False)),
        }

    # Deterministic fallback
    text = _fallback_question(domain, interview_type, asked_questions)
    return {"text": text, "topic": domain, "difficulty": difficulty, "is_followup": False}
