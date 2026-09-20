import json
import uuid
from typing import List, Dict, Any
from state import Task, LearnerProfile
from resources import find_resources
from practice import generate_practice_task, generate_project_idea
from llm import call_llm

PLANNER_PROMPT = """You are a senior curriculum planner. Create a personalized weekly learning plan for Week {week}.

Learner Profile:
- Weekly available time budget: {hours_per_week} hours.
- Prioritized Skill Gaps:
{gaps}

Curated Learning Resources Available:
{resources}

Planning Rules:
1. Total estimated hours across all tasks MUST sum to approximately {hours_per_week} hours (within +/- 1 hour).
2. For skills where the learner is "struggling", provide smaller, highly-scaffolded conceptual refreshers and guided drills.
3. Balance task modalities: include reading/video (conceptual), hands-on practice (application), and a checkpoint quiz.
4. Each task must have an informative, actionable description.

Return ONLY valid JSON matching:
{{
  "week": {week},
  "objectives": ["<Specific Measurable Objective 1>", "<Specific Measurable Objective 2>"],
  "tasks": [
    {{
      "skill": "<Skill Name>",
      "type": "video|reading|practice|project|quiz",
      "description": "<Clear instruction on what to learn or code>",
      "resource": "<URL or resource title>",
      "est_hours": 1.5
    }}
  ]
}}"""


def clean_json(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()


def generate_week(profile: LearnerProfile, gaps: List[Dict[str, Any]], week: int = 1) -> List[Task]:
    """Generates an adaptive weekly plan tailored to learner time budget and gap priorities."""
    if not gaps:
        tasks = [
            Task(
                id=uuid.uuid4().hex[:8],
                skill="Capstone Project",
                type="project",
                description="Synthesize all acquired skills into a portfolio showcase project with complete CI/CD.",
                resource="GitHub Capstone Repository",
                resource_url="https://github.com",
                est_hours=min(profile.hours_per_week, 6.0),
                done=False
            )
        ]
        profile.plan[str(week)] = tasks
        return tasks

    # Prioritize struggling skills, or rotate through gaps week by week
    struggling_skills = [s.name for s in profile.skills.values() if s.state == "struggling"]
    if struggling_skills:
        week_gaps = [g for g in gaps if g["skill"] in struggling_skills]
        for g in gaps:
            if g not in week_gaps:
                week_gaps.append(g)
    else:
        # Cycle through roadmap: Week 1 gets gaps 0-1, Week 2 gets gaps 1-2 or 2-3, etc.
        offset = ((week - 1) * 2) % max(1, len(gaps))
        week_gaps = gaps[offset:offset + 2]
        if not week_gaps:
            week_gaps = gaps[:2]

    # Pre-fetch curated catalog resources
    catalog_by_skill = {}
    for g in week_gaps:
        lvl = g.get("current_level") or "beginner"
        catalog_by_skill[g["skill"]] = find_resources(skill=g["skill"], level=lvl, k=4)

    gaps_payload = [
        {
            "skill": g["skill"],
            "required_level": g["required_level"],
            "current_level": g["current_level"],
            "is_struggling": g["skill"] in struggling_skills,
            "unmet_prereqs": g.get("unmet_prereqs", [])
        }
        for g in week_gaps
    ]

    prompt = PLANNER_PROMPT.format(
        week=week,
        hours_per_week=profile.hours_per_week,
        gaps=json.dumps(gaps_payload, indent=2),
        resources=json.dumps({
            k: [f"{r['title']} -> {r['url']}" for r in v]
            for k, v in catalog_by_skill.items()
        }, indent=2)
    )

    raw = call_llm(prompt, system_prompt="You are an adaptive curriculum architect. Output JSON only.")
    
    try:
        data = json.loads(clean_json(raw))
        tasks_data = data.get("tasks", [])
        objectives = data.get("objectives", [])
    except Exception:
        tasks_data = []
        objectives = [f"Week {week} focus: Advance competency in {week_gaps[0]['skill']}"]

    tasks: List[Task] = []
    primary_skill = week_gaps[0]["skill"]
    primary_res = catalog_by_skill.get(primary_skill, [])

    if tasks_data:
        for t in tasks_data:
            s_name = t.get("skill", primary_skill)
            t_type = t.get("type", "reading")
            s_res_list = catalog_by_skill.get(s_name) or find_resources(skill=s_name, level="beginner", k=3)
            
            # Match appropriate resource URL by type
            matched_res = None
            for r in s_res_list:
                if t_type == "video" and r.get("type") == "video":
                    matched_res = r
                    break
                elif t_type == "reading" and r.get("type") in ["reading", "book", "course"]:
                    matched_res = r
                    break
            if not matched_res and s_res_list:
                matched_res = s_res_list[0]

            r_title = matched_res.get("title") if matched_res else t.get("resource", f"{s_name} Resource")
            r_url = matched_res.get("url") if matched_res else None
            
            if t_type == "quiz":
                r_title = "In-App Diagnostic Quiz"
                r_url = None

            tasks.append(
                Task(
                    id=uuid.uuid4().hex[:8],
                    skill=s_name,
                    type=t_type,
                    description=t.get("description", "Study core curriculum topic"),
                    resource=r_title,
                    resource_url=r_url,
                    est_hours=float(t.get("est_hours", 1.5)),
                    done=False
                )
            )
    else:
        # High quality deterministic tasks with verified links
        video_res = next((r for r in primary_res if r.get("type") == "video"), primary_res[0] if primary_res else None)
        reading_res = next((r for r in primary_res if r.get("type") in ["reading", "book", "course"]), primary_res[-1] if primary_res else None)

        tasks = [
            Task(
                id=uuid.uuid4().hex[:8],
                skill=primary_skill,
                type="video",
                description=f"Watch conceptual video tutorial and take structured notes on {primary_skill}.",
                resource=video_res.get("title", f"{primary_skill} Video Guide") if video_res else f"{primary_skill} Video",
                resource_url=video_res.get("url", "https://www.youtube.com") if video_res else "https://www.youtube.com",
                est_hours=1.5,
                done=False
            ),
            Task(
                id=uuid.uuid4().hex[:8],
                skill=primary_skill,
                type="reading",
                description=f"Read official documentation and step-by-step code walkthroughs for {primary_skill}.",
                resource=reading_res.get("title", f"{primary_skill} Official Docs") if reading_res else f"{primary_skill} Docs",
                resource_url=reading_res.get("url", "https://docs.python.org") if reading_res else "https://docs.python.org",
                est_hours=1.5,
                done=False
            ),
            Task(
                id=uuid.uuid4().hex[:8],
                skill=primary_skill,
                type="practice",
                description=f"Hands-on Coding Lab: Implement practical algorithms and solve edge-case challenges in {primary_skill}.",
                resource="Interactive Practice Lab (GitHub)",
                resource_url="https://github.com",
                est_hours=2.0,
                done=False
            ),
            Task(
                id=uuid.uuid4().hex[:8],
                skill=primary_skill,
                type="quiz",
                description=f"Mastery Checkpoint: Take the 3-question diagnostic assessment for {primary_skill}.",
                resource="In-App Diagnostic Quiz",
                resource_url=None,
                est_hours=0.5,
                done=False
            )
        ]

    # Save to profile
    profile.plan[str(week)] = tasks
    profile.learning_objectives[str(week)] = objectives
    profile.activity_log.append({
        "event": "week_plan_generated",
        "week": week,
        "tasks_count": len(tasks),
        "objectives": objectives
    })

    # Also generate a project idea if none exists yet
    if not profile.project_ideas:
        known = [s.name for s in profile.skills.values() if s.mastery_score >= 0.5]
        p_idea = generate_project_idea(
            target_role=profile.target_role or "ml_engineer",
            known_skills=known,
            target_gap=week_gaps[0]["skill"] if week_gaps else "Python",
            level="intermediate" if profile.years_experience > 1 else "beginner"
        )
        from state import ProjectIdea
        profile.project_ideas.append(ProjectIdea(**p_idea))

    return tasks