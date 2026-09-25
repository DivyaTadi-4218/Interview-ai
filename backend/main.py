from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import init_db
from routes import companies, domains, interviews, voice, resume, coding, sql, dashboard, learning

app = FastAPI(title="AI Mock Interview Assistant", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok", "llm_configured": bool(settings.anthropic_api_key)}


app.include_router(companies.router)
app.include_router(domains.router)
app.include_router(interviews.router)
app.include_router(voice.router)
app.include_router(resume.router)
app.include_router(coding.router)
app.include_router(sql.router)
app.include_router(dashboard.router)
app.include_router(learning.router)
