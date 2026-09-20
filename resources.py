import chromadb
import json
import os
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CHROMA_DIR = os.path.join(BASE_DIR, "chroma")
RESOURCES_FILE = os.path.join(DATA_DIR, "resources.json")

_catalog_cache: Optional[Dict[str, List[Dict[str, Any]]]] = None


def load_raw_catalog() -> Dict[str, List[Dict[str, Any]]]:
    global _catalog_cache
    if _catalog_cache is None:
        with open(RESOURCES_FILE, encoding="utf-8") as f:
            _catalog_cache = json.load(f)
    return _catalog_cache


def build_index():
    catalog = load_raw_catalog()
    os.makedirs(CHROMA_DIR, exist_ok=True)
    try:
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        col = client.get_or_create_collection("resources")

        for skill, resources in catalog.items():
            for r in resources:
                col.upsert(
                    ids=[f"{skill}|{r['title']}"],
                    documents=[f"{skill}: {r['title']}. Level: {r.get('level', 'beginner')}. Type: {r.get('type', 'reading')}."],
                    metadatas=[{**r, "skill": skill}],
                )
        return col
    except Exception as e:
        # Graceful fallback if ChromaDB native library encounters issues
        return None


def get_collection():
    try:
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        return client.get_or_create_collection("resources")
    except Exception:
        return None


def find_resources(*args, **kwargs) -> List[Dict[str, Any]]:
    """Flexible resource lookup supporting:
    find_resources(skill, level, k=3)
    find_resources(col, skill, level, k=3)
    find_resources(skill="Python", level="beginner")
    """
    skill = kwargs.get("skill")
    level = kwargs.get("level", "beginner")
    k = kwargs.get("k", 3)

    if args:
        if len(args) == 1:
            skill = args[0]
        elif len(args) == 2:
            if isinstance(args[0], str):
                skill, level = args[0], args[1]
            else:
                skill, level = args[1], "beginner"
        elif len(args) >= 3:
            if isinstance(args[0], str):
                skill, level, k = args[0], args[1], args[2]
            else:
                # First arg was col
                skill, level = args[1], args[2]
                if len(args) >= 4:
                    k = args[3]

    skill = skill or "General"
    catalog = load_raw_catalog()

    # If ChromaDB collection is available, try semantic query
    col = get_collection()
    if col is not None:
        try:
            results = col.query(
                query_texts=[f"{skill} {level} learning resources tutorials books"],
                where={"skill": skill},
                n_results=k,
            )
            if results and results.get("metadatas") and results["metadatas"][0]:
                return [m for m in results["metadatas"][0]]
        except Exception:
            pass

    # Direct catalog filter and match
    skill_resources = catalog.get(skill, [])
    if not skill_resources:
        # fuzzy match
        for s, res_list in catalog.items():
            if skill.lower() in s.lower() or s.lower() in skill.lower():
                skill_resources = res_list
                break

    if not skill_resources:
        return [
            {
                "title": f"{skill} Official Guide & Documentation",
                "type": "reading",
                "url": f"https://www.google.com/search?q={skill}+documentation",
                "level": level,
                "skill": skill
            }
        ]

    # Prioritize resources matching learner level
    matched = [r for r in skill_resources if r.get("level") == level]
    unmatched = [r for r in skill_resources if r.get("level") != level]
    combined = (matched + unmatched)[:k]
    return [{**r, "skill": skill} for r in combined]