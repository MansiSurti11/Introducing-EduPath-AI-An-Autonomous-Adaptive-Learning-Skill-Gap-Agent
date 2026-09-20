"""Skill taxonomy: the backbone of gap analysis.
Add more roles/skills here — everything else adapts automatically.
"""
import json
import os

TAXONOMY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "taxonomy.json")


def load_taxonomy() -> dict:
    with open(TAXONOMY_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_all_skill_names() -> list[str]:
    """Every skill mentioned across all roles (deduplicated)."""
    tax = load_taxonomy()
    names = set()
    for role in tax["roles"].values():
        names.update(role["skills"].keys())
        for spec in role["skills"].values():
            names.update(spec.get("prereqs", []))
    return sorted(names)


def get_roles() -> dict:
    """role_key -> display name, for dropdowns."""
    return {k: v["display_name"] for k, v in load_taxonomy()["roles"].items()}


def get_required_skills(role_key: str) -> dict:
    tax = load_taxonomy()
    if role_key not in tax["roles"]:
        return {}
    return tax["roles"][role_key]["skills"]


def get_role_description(role_key: str) -> str:
    tax = load_taxonomy()
    return tax["roles"].get(role_key, {}).get("description", "")