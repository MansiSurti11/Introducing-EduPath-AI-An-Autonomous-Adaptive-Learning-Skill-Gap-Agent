import json
import re
from typing import Dict, Any, Optional
from state import LearnerProfile, Skill
from taxonomy import get_all_skill_names
from llm import call_llm

EXTRACTION_PROMPT = """You are a specialized AI Skills Extraction Engine.
Analyze the following learner profile / resume / portfolio / project description:

{resume_text}

Known skill taxonomy to map against (use these exact names where relevant):
{taxonomy}

Return ONLY valid JSON matching this schema:
{{
  "skills": [
    {{
      "name": "<Skill Name>",
      "level": "beginner|intermediate|advanced",
      "evidence": "<Direct phrase or context explaining proficiency>"
    }}
  ],
  "years_experience": <integer>,
  "projects": ["<Project 1>", "<Project 2>"],
  "certifications": ["<Cert 1>", "<Cert 2>"]
}}"""


def parse_resume(text: str) -> Dict[str, Any]:
    taxonomy = ", ".join(get_all_skill_names())
    prompt = EXTRACTION_PROMPT.format(
        resume_text=text[:12000],
        taxonomy=taxonomy
    )
    
    raw = call_llm(prompt, system_prompt="You are a precise technical skill extractor. Return JSON only.")
    
    # Clean JSON markdown fences
    cleaned = raw.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
    except Exception:
        # Fallback regex extraction if malformed json
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
            except Exception:
                data = {"skills": [], "years_experience": 1, "projects": [], "certifications": []}
        else:
            data = {"skills": [], "years_experience": 1, "projects": [], "certifications": []}

    return data


def build_profile(
    text: str,
    target_role: Optional[str] = None,
    career_goal: Optional[str] = "",
    hours_per_week: int = 6
) -> LearnerProfile:
    parsed = parse_resume(text)
    profile = LearnerProfile(
        raw_text=text,
        target_role=target_role,
        career_goal=career_goal or "",
        hours_per_week=hours_per_week,
        years_experience=parsed.get("years_experience", 0)
    )
    
    level_scores = {"beginner": 0.35, "intermediate": 0.65, "advanced": 0.90}
    
    for s in parsed.get("skills", []):
        name = s.get("name")
        if not name:
            continue
        level = s.get("level", "beginner")
        if level not in level_scores:
            level = "beginner"
        score = level_scores.get(level, 0.35)
        
        profile.skills[name] = Skill(
            name=name,
            current_level=level,
            state="in_progress" if score >= 0.5 else "not_started",
            mastery_score=score,
            evidence=s.get("evidence", "")
        )
    
    profile.activity_log.append({
        "event": "profile_created",
        "skills_detected": len(profile.skills),
        "target_role": target_role,
        "career_goal": career_goal
    })
    
    return profile