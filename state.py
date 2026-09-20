from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict, Any
import json, os, uuid

Level = Literal["beginner", "intermediate", "advanced"]
SkillState = Literal["not_started", "in_progress", "struggling", "mastered"]

class Skill(BaseModel):
    name: str
    current_level: Optional[Level] = None      # None = missing entirely
    state: SkillState = "not_started"
    mastery_score: float = 0.0                 # 0–1, updated by quizzes
    failed_attempts: int = 0
    evidence: Optional[str] = None

class Task(BaseModel):
    id: str
    skill: str
    type: Literal["video", "reading", "practice", "project", "quiz"]
    description: str
    resource: Optional[str] = None
    resource_url: Optional[str] = None
    est_hours: float = 1.0
    done: bool = False

class ProjectIdea(BaseModel):
    title: str
    description: str = ""                       # kept for backward compatibility
    problem_statement: Optional[str] = None
    proposed_solution: Optional[str] = None
    architecture: Optional[Dict] = None
    tech_stack: List[str] = []
    target_skills: List[str] = []
    milestones: List[Any] = []                   # can be strings or detailed dicts
    learning_outcomes: List[str] = []
    est_hours: float = 5.0

    class Config:
        extra = "allow"

class LearnerProfile(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])
    raw_text: str = ""
    target_role: Optional[str] = None
    career_goal: Optional[str] = ""
    years_experience: int = 0
    hours_per_week: int = 6
    skills: Dict[str, Skill] = {}
    plan: Dict[str, List[Task]] = {}           # str(week) -> tasks
    current_week: int = 1
    activity_log: List[dict] = []
    project_ideas: List[ProjectIdea] = []
    learning_objectives: Dict[str, List[str]] = {}

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db")
os.makedirs(DB_DIR, exist_ok=True)

def save_profile(p: LearnerProfile):
    with open(f"{DB_DIR}/{p.id}.json", "w", encoding="utf-8") as f:
        json.dump(p.model_dump(), f, indent=2)

def load_profile(pid: str) -> LearnerProfile:
    path = f"{DB_DIR}/{pid}.json"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Profile {pid} not found")
    with open(path, "r", encoding="utf-8") as f:
        return LearnerProfile(**json.load(f))