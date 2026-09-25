"""
Extracts text from an uploaded resume PDF and structures it into
skills/projects/experience/education. Only ever surfaces information
actually present in the resume — never invents content.
"""
import io
import re
from typing import Any, Dict

from pypdf import PdfReader

from services.llm_service import llm_service


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def _heuristic_parse(text: str) -> Dict[str, Any]:
    skill_keywords = [
        "Python", "Java", "JavaScript", "TypeScript", "React", "Node.js",
        "FastAPI", "Flask", "Django", "SQL", "PostgreSQL", "MySQL", "MongoDB",
        "AWS", "GCP", "Azure", "Docker", "Kubernetes", "Git", "REST", "GraphQL",
        "TensorFlow", "PyTorch", "Pandas", "NumPy", "C++", "C#", "Go",
    ]
    found_skills = sorted({s for s in skill_keywords if re.search(rf"\b{re.escape(s)}\b", text, re.I)})

    project_lines = [
        ln.strip("-•* \t") for ln in text.splitlines()
        if re.search(r"\bproject\b", ln, re.I) and len(ln.strip()) > 8
    ][:5]

    return {
        "skills": found_skills,
        "projects": [{"title": p, "description": p} for p in project_lines],
        "experience": [],
        "education": [],
    }


async def analyze_resume(text: str) -> Dict[str, Any]:
    system = (
        "You extract structured facts from a resume. Only include "
        "information explicitly present in the text. Never invent "
        "companies, projects, or skills that are not there."
    )
    user = f"""Resume text:
---
{text[:6000]}
---
Return JSON: {{"skills": [strings], "projects": [{{"title": str, "description": str}}],
"experience": [{{"company": str, "role": str, "summary": str}}],
"education": [{{"institution": str, "degree": str}}]}}
Only include what is actually present in the text above."""
    result = await llm_service.complete_json(system, user, max_tokens=800)
    if result and any(result.get(k) for k in ("skills", "projects", "experience", "education")):
        for key in ("skills", "projects", "experience", "education"):
            result.setdefault(key, [])
        return result
    return _heuristic_parse(text)
