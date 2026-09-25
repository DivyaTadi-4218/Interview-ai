"""Generates a day-by-day preparation roadmap, LLM-first with a static fallback."""
from typing import Any, Dict, List, Optional

from services.llm_service import llm_service

FALLBACK_TOPICS: Dict[str, List[str]] = {
    "Python": ["Python basics", "OOP in Python", "Data structures", "SQL fundamentals",
               "FastAPI / REST APIs", "Testing & debugging", "Mock interview"],
    "React": ["JavaScript/TS refresher", "React fundamentals", "Hooks deep-dive",
              "State management", "Performance & testing", "System design basics",
              "Mock interview"],
    "AI/ML": ["Python & NumPy/Pandas", "Core ML algorithms", "Model evaluation",
              "Deep learning basics", "Deploying models", "Case studies", "Mock interview"],
}


def _fallback_roadmap(domain: str, role: str) -> List[Dict[str, Any]]:
    topics = FALLBACK_TOPICS.get(domain) or FALLBACK_TOPICS["Python"]
    return [
        {
            "day": i + 1,
            "topic": t,
            "explanation": f"Core concepts and common interview angles for {t}.",
            "key_concepts": [f"{t} fundamentals", f"{t} common pitfalls"],
            "interview_questions": [f"Explain the basics of {t}.", f"What's a tricky edge case in {t}?"],
            "quiz": [{"q": f"One key idea behind {t}?", "a": "See explanation above."}],
            "coding_practice": t.lower() not in ("mock interview",),
        }
        for i, t in enumerate(topics)
    ]


async def generate_roadmap(company: Optional[str], role: str, domain: str,
                            experience_level: str, interview_type: str) -> List[Dict[str, Any]]:
    system = (
        "You build focused, practical interview-preparation roadmaps for "
        "software candidates. Be concrete and concise."
    )
    user = f"""
Company (context only, do not claim confidential info): {company or "General"}
Role: {role}
Domain: {domain}
Experience level: {experience_level}
Interview type: {interview_type}

Build a day-by-day roadmap (5-7 days) ending in a mock interview day.
For each day return: day (int), topic (str), explanation (1-2 sentences),
key_concepts (3-5 short strings), interview_questions (2-4 strings),
quiz (2 objects with "q" and "a"), coding_practice (bool).

Return JSON: {{"days": [ {{...}}, ... ]}}
"""
    result = await llm_service.complete_json(system, user, max_tokens=1500)
    if result and isinstance(result.get("days"), list) and result["days"]:
        return result["days"]
    return _fallback_roadmap(domain, role)
