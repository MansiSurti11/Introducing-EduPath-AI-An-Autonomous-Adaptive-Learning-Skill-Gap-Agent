"""Context-aware chat + report generation for the EduPath mentor."""
import json
from typing import Dict, Any, List, Optional
from state import LearnerProfile
from taxonomy import get_required_skills, get_role_description
from llm import call_llm

try:
    from resources import find_resources
except Exception:
    def find_resources(*args, **kwargs):
        return []


def build_report(profile: LearnerProfile) -> Dict[str, Any]:
    skills = profile.skills
    role = profile.target_role or "ml_engineer"
    required = get_required_skills(role)

    mastered = [k for k, v in skills.items() if v.state == "mastered"]
    in_prog = [k for k, v in skills.items() if v.state == "in_progress"]
    struggling = [k for k, v in skills.items() if v.state == "struggling"]
    not_started = [k for k, v in skills.items() if v.state == "not_started"]

    remaining_gaps = []
    for req_skill, spec in required.items():
        s = skills.get(req_skill)
        if s is None or s.state != "mastered":
            remaining_gaps.append({
                "skill": req_skill,
                "required_level": spec.get("required", "intermediate"),
                "current_level": s.current_level if s else None,
                "state": s.state if s else "missing",
                "mastery_score": round(s.mastery_score, 2) if s else 0.0,
            })

    total_hours_planned = 0.0
    total_hours_done = 0.0
    for tasks in profile.plan.values():
        if tasks:
            for t in tasks:
                total_hours_planned += t.est_hours
                if t.done:
                    total_hours_done += t.est_hours

    completion_rate = (round((total_hours_done / total_hours_planned) * 100, 1) if total_hours_planned > 0 else 0.0)

    recommended_steps = []
    if struggling:
        recommended_steps.append(f"Review remedial micro-lessons for struggling skills: {', '.join(struggling)}.")
    if in_prog:
        recommended_steps.append(f"Complete hands-on practice challenges in {in_prog[0]} to advance toward mastery.")
    if remaining_gaps:
        recommended_steps.append(f"Next high-priority gap on your roadmap: {remaining_gaps[0]['skill']}.")
    else:
        recommended_steps.append("Congratulations! All target competencies for this role have been reached.")

    return {
        "profile_id": profile.id,
        "target_role": profile.target_role,
        "career_goal": profile.career_goal,
        "current_week": profile.current_week,
        "skills_acquired": mastered,
        "skills_in_progress": in_prog,
        "struggling": struggling,
        "not_started": not_started,
        "remaining_gaps": remaining_gaps,
        "hours_completed": round(total_hours_done, 1),
        "hours_planned": round(total_hours_planned, 1),
        "completion_rate_percent": completion_rate,
        "recommended_next_steps": recommended_steps,
    }


def _truncate(text: str, limit: int = 1500) -> str:
    if not text:
        return ""
    text = text.strip()
    return text if len(text) <= limit else text[:limit] + " …[truncated]"


def build_chat_context(profile: LearnerProfile) -> str:
    skills = profile.skills or {}
    role = profile.target_role or "ml_engineer"
    required = get_required_skills(role) or {}
    role_desc = get_role_description(role)

    skill_lines = []
    for name, s in skills.items():
        req = required.get(name, {})
        skill_lines.append(
            f"- {name}: state={s.state}, level={s.current_level or 'unknown'}, "
            f"mastery={round(s.mastery_score * 100)}%, required={req.get('required','—')}, "
            f"failed_attempts={s.failed_attempts}"
            + (f", evidence={_truncate(s.evidence or '', 160)}" if s.evidence else "")
        )
    skills_block = "\n".join(skill_lines) or "(no skills detected yet)"

    req_lines = [f"- {n}: required={sp.get('required','intermediate')}, prereqs={sp.get('prereqs', [])}" for n, sp in required.items()]
    role_req_block = "\n".join(req_lines) or "(none)"

    week = profile.current_week
    tasks = profile.plan.get(str(week), []) or []
    task_lines = [f"- [{'x' if t.done else ' '}] {t.skill} ({t.type}, {t.est_hours}h): {t.description}" for t in tasks]
    tasks_block = "\n".join(task_lines) or "(no tasks this week yet)"
    objectives = profile.learning_objectives.get(str(week), []) or []
    objectives_block = "\n".join(f"- {o}" for o in objectives) or "(none)"

    events = profile.activity_log[-10:]
    activity_lines = [
        f"- {e.get('event')}: " + ", ".join(f"{k}={_truncate(str(v), 80)}" for k, v in e.items() if k != "event")
        for e in events
    ]
    activity_block = "\n".join(activity_lines) or "(no recent activity)"

    proj_lines = [
        f"- {p.title}: {p.problem_statement or p.description}" for p in (profile.project_ideas or [])[:3]
    ]
    proj_block = "\n".join(proj_lines) or "(none yet)"

    stats = build_report(profile)
    resume_excerpt = _truncate(profile.raw_text or "", 2500) or "(no resume text stored)"

    return f"""# LEARNER PROFILE CONTEXT

## Identity
- Learner ID: {profile.id}
- Target Role: {role}
- Role Description: {role_desc or '—'}
- Career Goal: {profile.career_goal or 'Not specified'}
- Years of Experience: {profile.years_experience}
- Weekly Study Budget: {profile.hours_per_week} hours
- Current Week: {week}
- Needs Replan: {any(s.state == 'struggling' for s in skills.values())}

## Resume / Portfolio (raw text provided by learner)
{resume_excerpt}

## Detected Skills
{skills_block}

## Known Gaps
(see gap details in the following lines if provided)

## Role Requirements (taxonomy)
{role_req_block}

## This Week's Plan (Week {week})
Objectives:
{objectives_block}

Tasks:
{tasks_block}

## Recent Activity (last 10 events)
{activity_block}

## Project Ideas
{proj_block}

## Progress Stats
- Skills Mastered: {stats['skills_acquired'] or 'none'}
- Skills In Progress: {stats['skills_in_progress'] or 'none'}
- Struggling: {stats['struggling'] or 'none'}
- Hours Completed: {stats['hours_completed']} / {stats['hours_planned']}
- Completion Rate: {stats['completion_rate_percent']}%
"""


SYSTEM_PROMPT = """You are EduPath, an empathetic, expert AI Learning Mentor and Career Coach.

You have COMPLETE knowledge of this learner's profile, resume, skills, gaps, weekly plan, quiz history, and project ideas (provided in the context block below).

Rules:
1. ALWAYS ground your answer in the learner's actual data.
2. Answer ONLY the current question — do not repeat previous answers or boilerplate.
3. Be concise but warm (3–6 short paragraphs or bullets).
4. When suggesting next steps, be specific: name the skill, name the resource, estimate hours.
5. If the context doesn't cover something, say so honestly.
6. Never invent mastery scores, task IDs, or role requirements.
7. If conversation history is provided, use it to stay consistent and avoid repeating yourself.

Tone: supportive, professional, direct.
"""


def answer_question(profile: LearnerProfile, question: str) -> str:
    return answer_question_with_gaps(profile, question, gaps=None, chat_history=None)


def answer_question_with_gaps(
    profile: LearnerProfile,
    question: str,
    gaps: Optional[List[Dict[str, Any]]] = None,
    chat_history: Optional[List[Dict[str, str]]] = None,
) -> str:
    """
    Answer a learner question with full profile context + optional conversation history.

    chat_history format:
    [
        {"role": "user", "content": "What should I study this week?"},
        {"role": "assistant", "content": "Focus on Python and Pandas..."},
        ...
    ]
    """
    gaps = gaps or []
    context = build_chat_context(profile)

    if gaps:
        gap_lines = []
        for g in gaps:
            line = (
                f"- {g.get('skill')}: {g.get('status')} "
                f"({g.get('current_level')} → {g.get('required_level')}), "
                f"priority={g.get('priority')}"
            )
            if g.get("unmet_prereqs"):
                line += f", unmet_prereqs={g['unmet_prereqs']}"
            if g.get("reason"):
                line += f" — {_truncate(g['reason'], 200)}"
            gap_lines.append(line)
        context = context.replace(
            "## Known Gaps\n(see gap details in the following lines if provided)",
            "## Known Gaps\n" + "\n".join(gap_lines),
        )

    q = (question or "").strip()
    if not q:
        return "Ask me anything about your roadmap — skills, gaps, what to study next, or how your resume maps to your target role."

    # Build recent conversation block (last 6 messages = ~3 turns)
    history_block = ""
    if chat_history:
        recent = chat_history[-6:]
        lines = []
        for msg in recent:
            role = msg.get("role", "user").upper()
            content = _truncate(msg.get("content", ""), 600)
            lines.append(f"{role}: {content}")
        history_block = "\n## Recent Conversation\n" + "\n".join(lines)

    prompt = f"""{context}

{history_block}

---

# LEARNER QUESTION
{q}

---

Answer the learner's question using the profile context and recent conversation above.
Be specific, cite their real skills / gaps / tasks, and keep it actionable.
Do NOT repeat previous answers. Build on what was already said if relevant."""

    answer = call_llm(prompt, system_prompt=SYSTEM_PROMPT, max_tokens=1200)
    return answer.strip() if answer else "I couldn't reach the reasoning engine. Please try again."