# InterviewAI — Voice-Only Mock Interview Platform

A full-stack voice-only AI mock interview assistant. The candidate never
types during an interview — they speak, the AI evaluates and adapts,
and speaks the next question back.

## Architecture

```
Microphone (browser)
  → Web Speech API (SpeechRecognition, in-browser STT)
  → React frontend
  → FastAPI backend
  → Interview Agent (state machine)
  → Question Agent + Evaluation Agent (Claude via Anthropic API, with
    deterministic fallbacks when no API key is set)
  → SQLite database
  → Web Speech API (SpeechSynthesis, in-browser TTS)
  → AI voice back to the candidate
```

## Why voice runs client-side

STT/TTS use the browser's native Web Speech API (`SpeechRecognition` /
`speechSynthesis`) instead of a paid cloud provider. That means:
- **Zero API keys needed for voice** — it works immediately.
- **Lowest latency** — no audio round-trip to a server.
- **Provider-independent by design** — `backend/routes/voice.py` and
  `backend/services/` are already structured so a real STT/TTS provider
  (Whisper, Deepgram, ElevenLabs, Azure Speech) can be dropped in later
  without changing the frontend contract: the frontend calls
  `POST /voice/transcribe` first and only falls back to the browser API
  if that route isn't configured (currently returns 501 by design).
- Requires Chrome or Edge on desktop (Web Speech API support is
  inconsistent in Firefox/Safari as of writing — check before demoing).

## What's fully working out of the box (no API key needed)

- Company/domain/role/experience/interview-type selection
- The full voice interview loop: greeting → question → listening →
  transcript → evaluation → adaptive next question → completion
- Adaptive difficulty (deterministic fallback: strong answers escalate
  difficulty, weak answers trigger a simpler follow-up)
- Interview report with charts, strengths/weak areas, and a study roadmap
- Resume upload + heuristic keyword/skill extraction from the PDF
- Dashboard, history, and a "Prepare Before Interview" learning roadmap
  (fallback topic list per domain)
- Coding Practice Mode and SQL Practice Mode as separate typing-based
  pages, kept fully outside the voice interview flow as the spec requires

## What gets meaningfully better with `ANTHROPIC_API_KEY` set

Question selection, answer evaluation, resume parsing, and roadmap
generation all call Claude when a key is present
(`backend/services/llm_service.py`), producing genuinely adaptive,
context-aware interviews instead of the static fallback question bank
and heuristic scoring. Nothing needs to change in the frontend to
enable this — just set the env var.

## What is intentionally scoped down

- **Coding/SQL review is LLM-based feedback, not sandboxed code
  execution.** Running arbitrary user-submitted code server-side is a
  security risk; `routes/coding.py` and `routes/sql.py` send the
  submission to the LLM for a correctness/complexity review instead. A
  real sandboxed runner (e.g. Judge0, a Docker-isolated executor) can
  replace this later behind the same `/coding/review` contract.
- **Resume parsing without an API key** uses a keyword-matching
  heuristic (a fixed skill list + lines containing "project"), not true
  NLP extraction — good enough to demo the flow, not production-grade.
  With `ANTHROPIC_API_KEY` set it uses the LLM instead and is much better.
- The static fallback question bank (`tools/question_tool.py`) covers
  the interview types and domains in the spec but is not exhaustive —
  it's meant to keep the demo fully functional offline, with the LLM
  path being the real adaptive experience.

## Running it

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # optional but recommended
pip install -r requirements.txt
cp .env.example .env   # then add your ANTHROPIC_API_KEY if you have one
uvicorn main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for the interactive API docs.
The SQLite file (`interview.db`) is created automatically on first run.
To migrate to Postgres later, just change `DATABASE_URL` in `.env` —
no code changes needed (`database.py` is already dialect-agnostic).

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`. It talks to the backend at
`http://localhost:8000` by default — set `VITE_API_URL` in a `.env` file
in `frontend/` to point elsewhere.

**Use Chrome or Edge** — the voice interview needs `SpeechRecognition`,
which those browsers support well.

## Project structure

```
backend/
  main.py, config.py, database.py, models.py, schemas.py
  agents/            interview_agent.py (state machine), plus thin
                      question/evaluation/learning agent wrappers
  routes/            interviews, companies, domains, voice, resume,
                      coding, sql, dashboard, learning
  services/          llm_service (Anthropic API), resume_service,
                      evaluation_service (report builder)
  tools/             question_tool, evaluation_tool, learning_tool
                      (LLM-first, deterministic-fallback logic)
  data/companies.py  companies/domains/roles/experience/interview-type lists

frontend/
  src/api/client.ts       typed fetch wrapper for every backend route
  src/hooks/              useSpeechRecognition, useSpeechSynthesis
  src/components/         AIAvatar, MicButton, Waveform, ProgressBar, Navbar
  src/pages/              Dashboard, Companies, InterviewSetup,
                          InterviewLive (the voice screen), InterviewReport,
                          Learning, Resume, History
```

## How it works

InterviewAI conducts mock interviews entirely by voice. The candidate selects a company, role, domain and interview type. Speech-to-text and text-to-speech run in the browser, while the backend's interview agent tracks state, evaluates each answer for technical and communication quality, and adaptively picks the next question. When no LLM key is configured, it falls back to deterministic logic, so the app works either way.
