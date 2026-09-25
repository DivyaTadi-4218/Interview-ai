"""
Coding Practice Mode. This is intentionally separate from the voice
interview loop (per spec: "Do NOT require typing during normal voice
interviews — provide a code editor only in Coding Practice Mode").

For safety, this does not execute arbitrary submitted code sandboxed on
the server; it sends the code to the LLM for a correctness/quality
review instead. Swap in a real sandboxed runner here if needed.
"""
from fastapi import APIRouter

from schemas import CodeRunRequest
from services.llm_service import llm_service

router = APIRouter(prefix="/coding", tags=["coding"])


@router.post("/review")
async def review_code(payload: CodeRunRequest):
    system = (
        "You are a senior engineer reviewing a candidate's code during "
        "interview practice. Be specific and constructive."
    )
    user = f"""Language: {payload.language}
Code:
```
{payload.code}
```
Return JSON: {{"correct": true|false, "time_complexity": "...",
"space_complexity": "...", "feedback": "2-4 sentences", "bugs": ["..."]}}"""
    result = await llm_service.complete_json(system, user, max_tokens=500)
    if not result:
        result = {
            "correct": None,
            "time_complexity": "unknown",
            "space_complexity": "unknown",
            "feedback": "Automated review unavailable (no LLM configured). Code received and saved.",
            "bugs": [],
        }
    return result
