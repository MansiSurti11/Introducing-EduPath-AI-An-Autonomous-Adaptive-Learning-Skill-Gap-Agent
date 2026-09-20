import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict
from pydantic import BaseModel
import io
import pypdf

from parser import build_profile
from gap import compute_gaps
from planner import generate_week
from tracker import (
    update_task, apply_quiz_result, needs_replan, advance_week,
    generate_quiz, grade_quiz,
)
from practice import generate_practice_task, generate_project_idea
from reports import answer_question_with_gaps, build_report
from state import save_profile, load_profile, ProjectIdea
from taxonomy import load_taxonomy

app = FastAPI(
    title="EduPath API",
    description="Adaptive AI Learning & Skill Gap Agent",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str
    chat_history: Optional[List[Dict[str, str]]] = []


@app.get("/roles")
def list_roles():
    tax = load_taxonomy()
    return [
        {
            "key": k,
            "display_name": v["display_name"],
            "description": v.get("description", ""),
            "skills_count": len(v.get("skills", {})),
        }
        for k, v in tax["roles"].items()
    ]


@app.post("/profile")
def create_profile(
    resume_text: str = Form(...),
    target_role: str = Form("ml_engineer"),
    career_goal: Optional[str] = Form(""),
    hours: int = Form(6),
):
    p = build_profile(
        text=resume_text,
        target_role=target_role,
        career_goal=career_goal or "",
        hours_per_week=hours,
    )
    gaps = compute_gaps(p, target_role)
    generate_week(p, gaps, week=1)
    save_profile(p)
    return {
        "profile_id": p.id,
        "target_role": p.target_role,
        "career_goal": p.career_goal,
        "skills": {k: v.model_dump() for k, v in p.skills.items()},
        "gaps": gaps,
        "week1": [t.model_dump() for t in p.plan.get("1", [])],
        "project_ideas": [pi.model_dump() for pi in p.project_ideas],
    }


@app.post("/upload_resume")
async def upload_resume(
    file: UploadFile = File(...),
    target_role: str = Form("ml_engineer"),
    career_goal: Optional[str] = Form(""),
    hours: int = Form(6),
):
    content = await file.read()
    extracted_text = ""
    if file.filename.lower().endswith(".pdf"):
        try:
            reader = pypdf.PdfReader(io.BytesIO(content))
            extracted_text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as e:
            raise HTTPException(400, f"Could not read PDF: {str(e)}")
    else:
        try:
            extracted_text = content.decode("utf-8")
        except Exception:
            extracted_text = content.decode("latin-1", errors="ignore")
    if not extracted_text.strip():
        extracted_text = "Experienced software practitioner and technology enthusiast."

    p = build_profile(
        text=extracted_text,
        target_role=target_role,
        career_goal=career_goal or "",
        hours_per_week=hours,
    )
    gaps = compute_gaps(p, target_role)
    generate_week(p, gaps, week=1)
    save_profile(p)
    return {
        "profile_id": p.id,
        "target_role": p.target_role,
        "career_goal": p.career_goal,
        "skills": {k: v.model_dump() for k, v in p.skills.items()},
        "gaps": gaps,
        "week1": [t.model_dump() for t in p.plan.get("1", [])],
        "project_ideas": [pi.model_dump() for pi in p.project_ideas],
    }


@app.get("/profile/{pid}")
def get_profile(pid: str):
    p = load_profile(pid)
    gaps = compute_gaps(p, p.target_role) if p.target_role else []
    return {
        "profile_id": p.id,
        "target_role": p.target_role,
        "career_goal": p.career_goal,
        "raw_text": p.raw_text,
        "current_week": p.current_week,
        "hours_per_week": p.hours_per_week,
        "skills": {k: v.model_dump() for k, v in p.skills.items()},
        "gaps": gaps,
        "plan": {
            wk: [t.model_dump() for t in tasks]
            for wk, tasks in p.plan.items()
            if tasks is not None
        },
        "learning_objectives": p.learning_objectives,
        "project_ideas": [pi.model_dump() for pi in p.project_ideas],
        "needs_replan": needs_replan(p),
    }


@app.get("/gaps/{pid}")
def get_gaps(pid: str):
    p = load_profile(pid)
    if not p.target_role:
        return []
    return compute_gaps(p, p.target_role)


@app.post("/task/{pid}/{task_id}")
def complete_task(pid: str, task_id: str, done: bool = True):
    p = load_profile(pid)
    found = update_task(p, task_id, done)
    if not found:
        raise HTTPException(404, f"Task {task_id} not found")
    return {"ok": True, "task_id": task_id, "done": done, "replan_triggered": needs_replan(p)}


@app.get("/quiz/{pid}/{skill}")
def get_quiz(pid: str, skill: str):
    p = load_profile(pid)
    return {"skill": skill, "questions": generate_quiz(p, skill)}


@app.post("/quiz/{pid}/{skill}")
def submit_quiz(pid: str, skill: str, answers: List[str]):
    p = load_profile(pid)
    result = grade_quiz(p, skill, answers)
    apply_quiz_result(p, skill, result)
    return {
        "skill": skill,
        "verdict": result["verdict"],
        "new_mastery": result["new_mastery"],
        "feedback": result["feedback"],
        "replan_triggered": needs_replan(p),
    }


@app.post("/replan/{pid}")
def replan(pid: str):
    p = load_profile(pid)
    gaps = compute_gaps(p, p.target_role)
    generate_week(p, gaps, week=p.current_week)
    save_profile(p)
    return {
        "week": p.current_week,
        "replan_success": True,
        "tasks": [t.model_dump() for t in p.plan[str(p.current_week)]],
        "objectives": p.learning_objectives.get(str(p.current_week), []),
    }


@app.post("/next_week/{pid}")
def next_week(pid: str):
    p = load_profile(pid)
    advance_week(p)
    gaps = compute_gaps(p, p.target_role)
    generate_week(p, gaps, week=p.current_week)
    save_profile(p)
    return {
        "week": p.current_week,
        "tasks": [t.model_dump() for t in p.plan[str(p.current_week)]],
        "objectives": p.learning_objectives.get(str(p.current_week), []),
    }


@app.get("/practice/{pid}/{skill}")
def get_practice(pid: str, skill: str):
    """Fresh problem + starter code + test cases (no online judge)."""
    p = load_profile(pid)
    s = p.skills.get(skill)
    lvl = s.current_level if s and s.current_level else "intermediate"
    return generate_practice_task(skill=skill, level=lvl)


@app.get("/project/{pid}")
def get_project(pid: str, refresh: bool = False):
    """Capstone project. Pass ?refresh=true for a new idea every time."""
    p = load_profile(pid)
    if p.project_ideas and not refresh:
        return p.project_ideas[0].model_dump()

    known = [s.name for s in p.skills.values() if s.mastery_score >= 0.5]
    gaps = compute_gaps(p, p.target_role)
    top_gap = gaps[0]["skill"] if gaps else "Core Architecture"

    idea_dict = generate_project_idea(
        target_role=p.target_role or "ml_engineer",
        known_skills=known,
        target_gap=top_gap,
        level="intermediate" if getattr(p, "years_experience", 0) > 1 else "beginner",
    )
    if not idea_dict.get("description"):
        idea_dict["description"] = (
            idea_dict.get("problem_statement")
            or idea_dict.get("proposed_solution")
            or ""
        )
    idea = ProjectIdea(**idea_dict)
    p.project_ideas = [idea] + p.project_ideas[:4]
    save_profile(p)
    return idea.model_dump()


@app.get("/report/{pid}")
def report(pid: str):
    p = load_profile(pid)
    stats = build_report(p)
    narrative = answer_question_with_gaps(
        p,
        "Synthesize a periodic progress report: wins, friction, next steps.",
        gaps=compute_gaps(p, p.target_role) if p.target_role else [],
    )
    return {"stats": stats, "narrative": narrative}


# ─────────────── FIXED ASK ENDPOINT ───────────────
@app.post("/ask/{pid}")
def ask(pid: str, body: AskRequest):
    p = load_profile(pid)
    gaps = compute_gaps(p, p.target_role) if p.target_role else []
    answer = answer_question_with_gaps(
        profile=p,
        question=body.question,
        gaps=gaps,
        chat_history=body.chat_history or []
    )
    return {"answer": answer}


@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}