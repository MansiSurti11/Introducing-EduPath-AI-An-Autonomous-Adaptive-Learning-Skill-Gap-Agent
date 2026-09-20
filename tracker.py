import json
import re
from typing import List, Dict, Any
from state import LearnerProfile, save_profile, Skill
from llm import call_llm


def clean_json(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()


def generate_quiz(profile: LearnerProfile, skill_name: str) -> List[str]:
    """Generates exactly 3 conceptual and scenario-based diagnostic questions for a skill."""
    skill = profile.skills.get(skill_name)
    score = skill.mastery_score if skill else 0.4
    
    prompt = f"""Generate exactly 3 short, diagnostic quiz questions to assess understanding of "{skill_name}".
The learner's estimated current mastery level is {score:.2f} (scale 0 to 1.0).
Include one foundational concept question, one practical application question, and one edge-case / debugging question.

Respond ONLY with a JSON array of strings, for example:
["Question 1...", "Question 2...", "Question 3..."]"""

    raw = call_llm(prompt, system_prompt="You are a technical examiner. Return JSON array only.")
    try:
        data = json.loads(clean_json(raw))
        if isinstance(data, list) and len(data) >= 1:
            return data[:3]
    except Exception:
        pass

    return [
        f"Explain the primary architecture and mental model behind {skill_name}.",
        f"In a real-world scenario, how would you design and implement a solution using {skill_name}?",
        f"What are the most common pitfalls or performance bottlenecks encountered when using {skill_name}, and how do you resolve them?"
    ]


def grade_quiz(profile: LearnerProfile, skill_name: str, answers: List[str]) -> Dict[str, Any]:
    """Evaluates learner responses, provides constructive pedagogical feedback,
    and calculates an updated mastery score.
    """
    skill = profile.skills.get(skill_name)
    prior_score = skill.mastery_score if skill else 0.35
    failed_attempts = skill.failed_attempts if skill else 0

    prompt = f"""You are grading technical quiz answers for the skill "{skill_name}".
Prior mastery score: {prior_score:.2f}. Past failed attempts: {failed_attempts}.

Learner Answers:
{json.dumps(answers, indent=2)}

Judge the conceptual correctness, completeness, and practical reasoning of these answers.
Rubric:
- Score >= 0.80 -> verdict: "mastered"
- Score 0.55 to 0.79 -> verdict: "in_progress" (on track)
- Score < 0.55 -> verdict: "struggling"

Respond ONLY with valid JSON:
{{
  "new_mastery": <float between 0.0 and 1.0>,
  "verdict": "struggling|in_progress|mastered",
  "feedback": "<2-3 constructive sentences explaining strengths and weaknesses>"
}}"""

    raw = call_llm(prompt, system_prompt="You are an encouraging but rigorous technical evaluator. Output JSON only.")
    
    try:
        result = json.loads(clean_json(raw))
        # Ensure proper bounds
        score = float(result.get("new_mastery", 0.6))
        score = max(0.0, min(1.0, score))
        verdict = result.get("verdict", "in_progress")
        if verdict not in ["struggling", "in_progress", "mastered"]:
            verdict = "mastered" if score >= 0.8 else ("struggling" if score < 0.55 else "in_progress")
        return {
            "new_mastery": score,
            "verdict": verdict,
            "feedback": result.get("feedback", "Assessment evaluated successfully.")
        }
    except Exception:
        # Fallback heuristic
        combined = " ".join(answers).lower()
        struggle_cues = ["don't know", "dont know", "not sure", "unsure", "confused", "no idea", "need to learn"]
        if any(c in combined for c in struggle_cues) or len(combined.strip()) < 50:
            return {
                "new_mastery": 0.35,
                "verdict": "struggling",
                "feedback": "Responses showed hesitation or fundamental gaps on core concepts. Additional guided practice is recommended."
            }
        else:
            return {
                "new_mastery": 0.85,
                "verdict": "mastered",
                "feedback": "Demonstrated sound understanding of core principles and practical trade-offs."
            }


def apply_quiz_result(profile: LearnerProfile, skill_name: str, result: Dict[str, Any]):
    """Applies quiz outcome to the learner's skill state and logs the activity."""
    if skill_name not in profile.skills:
        profile.skills[skill_name] = Skill(name=skill_name)
    
    skill = profile.skills[skill_name]
    skill.mastery_score = result["new_mastery"]
    skill.state = result["verdict"]

    if result["verdict"] == "struggling":
        skill.failed_attempts += 1
    elif result["verdict"] == "mastered":
        skill.failed_attempts = 0

    profile.activity_log.append({
        "event": "quiz_submitted",
        "skill": skill_name,
        "score": result["new_mastery"],
        "verdict": result["verdict"],
        "feedback": result["feedback"]
    })
    save_profile(profile)


def update_task(profile: LearnerProfile, task_id: str, done: bool = True):
    """Marks a task as completed or uncompleted and records hours completed."""
    found = False
    for week_tasks in profile.plan.values():
        if not week_tasks:
            continue
        for t in week_tasks:
            if t.id == task_id:
                t.done = done
                found = True
                profile.activity_log.append({
                    "event": "task_updated",
                    "task_id": task_id,
                    "skill": t.skill,
                    "done": done,
                    "hours": t.est_hours
                })
                # If it's practice and completed, boost skill state to in_progress if not_started
                s = profile.skills.get(t.skill)
                if s and s.state == "not_started" and done:
                    s.state = "in_progress"
                    s.mastery_score = max(s.mastery_score, 0.5)
                break
        if found:
            break
    save_profile(profile)
    return found


def needs_replan(profile: LearnerProfile) -> bool:
    """Returns True if any skill is marked as struggling, indicating an adaptive replan is needed."""
    return any(s.state == "struggling" for s in profile.skills.values())


def advance_week(profile: LearnerProfile):
    """Advances learner to the next week in their curriculum."""
    profile.current_week += 1
    profile.activity_log.append({
        "event": "advanced_week",
        "new_week": profile.current_week
    })
    save_profile(profile)