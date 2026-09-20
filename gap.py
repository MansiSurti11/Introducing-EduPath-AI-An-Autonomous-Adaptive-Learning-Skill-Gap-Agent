"""Skill Gap Analysis Engine: compares learner capabilities against role requirements,
evaluates prerequisite Directed Acyclic Graphs (DAG), and derives structured learning objectives.
"""
from typing import List, Dict, Any
from taxonomy import get_required_skills

LEVEL_ORDER = {"beginner": 1, "intermediate": 2, "advanced": 3}

# Pedagogical learning objective templates based on target level
OBJECTIVE_TEMPLATES = {
    "beginner": [
        "Grasp foundational terminology, mental models, and syntax of {skill}",
        "Run minimal reproducible working examples and configure standard environments",
        "Explain key use cases, architectural roles, and boundaries of {skill}"
    ],
    "intermediate": [
        "Implement end-to-end practical workflows applying {skill} in real projects",
        "Debug typical runtime exceptions, optimize configurations, and follow idiomatic practices",
        "Integrate {skill} with upstream and downstream components in the tech stack"
    ],
    "advanced": [
        "Architect scalable, fault-tolerant production solutions utilizing {skill}",
        "Optimize throughput, resource constraints, latency, and security hardening",
        "Evaluate architectural trade-offs and mentor cross-functional implementations"
    ]
}


def compute_gaps(profile, role_key: str) -> List[Dict[str, Any]]:
    """Identifies skills missing or below target level, resolves prerequisite DAG,
    and returns prioritized gap items with structured learning objectives.
    """
    required = get_required_skills(role_key)
    if not required:
        return []

    gaps = []

    for skill_name, req in required.items():
        learner_skill = profile.skills.get(skill_name)
        missing = learner_skill is None or learner_skill.current_level is None
        
        current_lvl = None if missing else learner_skill.current_level
        req_lvl = req.get("required", "intermediate")

        is_below = False
        if not missing:
            cur_val = LEVEL_ORDER.get(current_lvl, 0)
            req_val = LEVEL_ORDER.get(req_lvl, 2)
            if cur_val < req_val:
                is_below = True

        if missing or is_below or (learner_skill and learner_skill.state == "struggling"):
            unmet_prereqs = []
            for prereq in req.get("prereqs", []):
                ps = profile.skills.get(prereq)
                # Prereq is unmet if missing or mastery < 0.65 or state != 'mastered'
                if ps is None or (ps.state != "mastered" and ps.mastery_score < 0.65):
                    unmet_prereqs.append(prereq)

            status_badge = "Missing" if missing else ("Struggling" if (learner_skill and learner_skill.state == "struggling") else "Proficiency Gap")

            templates = OBJECTIVE_TEMPLATES.get(req_lvl, OBJECTIVE_TEMPLATES["intermediate"])
            objectives = [t.format(skill=skill_name) for t in templates]

            gaps.append({
                "skill": skill_name,
                "required_level": req_lvl,
                "current_level": current_lvl,
                "missing": missing,
                "status": status_badge,
                "unmet_prereqs": unmet_prereqs,
                "objectives": objectives,
                "priority": 0,
            })

    # Prerequisite depth computation via DAG recursion
    depth_cache = {}

    def depth(skill_name: str, visited=None) -> int:
        if visited is None:
            visited = set()
        if skill_name in depth_cache:
            return depth_cache[skill_name]
        if skill_name in visited:
            return 0  # guard against cycles
        visited.add(skill_name)

        req = required.get(skill_name, {})
        prereqs = req.get("prereqs", [])
        if not prereqs:
            d = 0
        else:
            d = 1 + max(depth(p, visited.copy()) for p in prereqs)
        depth_cache[skill_name] = d
        return d

    for g in gaps:
        s = profile.skills.get(g["skill"])
        # Give highest urgency to struggling skills so the learner recovers immediately
        struggle_urgency = -10 if (s and s.state == "struggling") else 0
        
        # Priority formula: Lower number = address earlier
        # Dependencies with depth 0 and no unmet prereqs come first
        g["priority"] = depth(g["skill"]) + (len(g["unmet_prereqs"]) * 3) + struggle_urgency

        if g["missing"]:
            g["reason"] = f"Skill not detected in your profile. Role requires {g['required_level']} mastery."
        elif s and s.state == "struggling":
            g["reason"] = f"Diagnostic assessment flagged friction in {g['skill']}. Remedial reinforcement is prioritized."
        else:
            g["reason"] = f"Current proficiency ({g['current_level']}) is below target role requirements ({g['required_level']})."

        if g["unmet_prereqs"]:
            g["reason"] += f" Recommended to complete prerequisites first: {', '.join(g['unmet_prereqs'])}."

    # Return sorted by priority (lowest number first)
    return sorted(gaps, key=lambda x: x["priority"])