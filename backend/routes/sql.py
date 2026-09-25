"""SQL Practice Mode — LLM-reviewed query feedback, separate from the voice flow."""
from fastapi import APIRouter
from pydantic import BaseModel

from services.llm_service import llm_service

router = APIRouter(prefix="/sql", tags=["sql"])


class SQLReviewRequest(BaseModel):
    question: str
    query: str


@router.post("/review")
async def review_sql(payload: SQLReviewRequest):
    system = "You are a SQL interviewer reviewing a candidate's query for correctness and style."
    user = f"""Interview question: {payload.question}
Candidate's SQL:
```sql
{payload.query}
```
Return JSON: {{"correct": true|false, "feedback": "2-4 sentences",
"optimized_query": "a cleaner/faster version if applicable"}}"""
    result = await llm_service.complete_json(system, user, max_tokens=400)
    if not result:
        result = {
            "correct": None,
            "feedback": "Automated review unavailable (no LLM configured). Query received.",
            "optimized_query": payload.query,
        }
    return result
