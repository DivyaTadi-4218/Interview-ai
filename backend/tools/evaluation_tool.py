"""
Scores a candidate's spoken answer along the dimensions the spec calls
for. Uses the LLM when configured; otherwise falls back to a simple
heuristic (length/keyword based) so the interview still produces a
report without an API key.
"""
from typing import Any, Dict, Optional

from services.llm_service import llm_service

DIMENSIONS = [
    "technical_correctness", "relevance", "completeness", "communication",
    "clarity", "confidence", "structure",
]


def _heuristic_eval(question: str, answer: str) -> Dict[str, Any]:
    words = len(answer.split())
    base = 3.0
    if words > 15:
        base += 2
    if words > 40:
        base += 1.5
    if any(w in answer.lower() for w in ["for example", "i built", "i used", "because"]):
        base += 1.0
    base = min(base, 8.0)
    scores = {d: round(base + (i % 3) * 0.2 - 0.2, 1) for i, d in enumerate(DIMENSIONS)}
    overall = round(sum(scores.values()) / len(scores), 1)
    return {
        **scores,
        "overall_score": overall,
        "feedback": "Answer captured. Consider adding a concrete example and quantifying impact where possible.",
        "suggested_answer": None,
    }


async def evaluate_answer(question: str, answer: str, domain: str, role: str,
                           experience_level: str) -> Dict[str, Any]:
    if not answer or not answer.strip():
        return {**{d: 0 for d in DIMENSIONS}, "overall_score": 0,
                "feedback": "No answer was captured.", "suggested_answer": None}

    system = (
        "You are an expert interview evaluator. Score the candidate's "
        "spoken answer honestly but fairly for their stated experience "
        "level. Do not be harsh about spoken-language disfluencies "
        "(the answer came from speech-to-text)."
    )
    user = f"""
Role: {role}
Domain: {domain}
Experience level: {experience_level}
Question: {question}
Candidate's answer (transcribed from speech): {answer}

Score each dimension from 0-10: technical_correctness, relevance,
completeness, communication, clarity, confidence, structure.
Also give: overall_score (0-10, weighted average), feedback (1-2 sentences,
supportive but honest), suggested_answer (a strong model answer, 2-4
sentences).

Return JSON with exactly these keys: technical_correctness, relevance,
completeness, communication, clarity, confidence, structure, overall_score,
feedback, suggested_answer.
"""
    result: Optional[Dict[str, Any]] = await llm_service.complete_json(system, user, max_tokens=600)
    if result and "overall_score" in result:
        for d in DIMENSIONS:
            result.setdefault(d, 5)
        return result

    return _heuristic_eval(question, answer)
