"""Practice challenges + project ideas. Problems, starter code, test cases — no online judge."""
import json
import random
import time
from typing import Dict, Any, List

try:
    from llm import call_llm
except Exception:
    def call_llm(prompt, system_prompt=""):
        return "{}"


def clean_json(text: str) -> str:
    cleaned = (text or "").strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()


SKILL_LANGUAGE_MAP = {
    "python": "python", "pandas": "python", "machine learning fundamentals": "python",
    "ml pipelines": "python", "pytorch": "python", "statistics": "python", "linear algebra": "python",
    "javascript": "javascript", "react": "jsx", "node.js": "javascript", "html/css": "html",
    "rest apis": "javascript", "sql": "sql", "tableau": "text", "docker": "dockerfile",
    "kubernetes": "yaml", "ci/cd pipelines": "yaml", "cloud architecture (aws)": "yaml",
    "git": "bash", "linux": "bash", "network security": "bash", "siem tools": "text",
    "vulnerability assessment": "text",
}


def _language_for(skill: str) -> str:
    return SKILL_LANGUAGE_MAP.get(skill.lower().strip(), "python")


def _fallback_challenge(skill: str, level: str) -> Dict[str, Any]:
    random.seed(int(time.time() * 1000) % 100000)
    sk = skill.lower().strip()
    lang = _language_for(skill)

    if "python" in sk:
        c = {
            "title": "Smart Log Parser & Summarizer",
            "problem_statement": "Build a log analysis utility. Write summarize_logs(lines) that reads a list of log lines, extracts timestamps and severity levels, and returns a summary dict with counts per severity, earliest, latest, and total.",
            "starter_code": (
                "from typing import List, Dict, Any\n\n"
                "def summarize_logs(lines: List[str]) -> Dict[str, Any]:\n"
                "    \"\"\"Expected line: 'YYYY-MM-DD HH:MM:SS [LEVEL] message'\"\"\"\n"
                "    result = {\"counts\": {}, \"earliest\": None, \"latest\": None, \"total\": 0}\n"
                "    # TODO: parse lines and fill result\n"
                "    return result\n\n"
                "if __name__ == \"__main__\":\n"
                "    sample = [\n"
                "        \"2024-01-15 10:00:01 [INFO] started\",\n"
                "        \"2024-01-15 10:00:05 [ERROR] failed\",\n"
                "    ]\n"
                "    print(summarize_logs(sample))\n"
            ),
            "test_cases": [
                {"input": "['2024-01-15 10:00:01 [INFO] started', '2024-01-15 10:00:05 [ERROR] failed']", "expected_output": "{'counts': {'INFO': 1, 'ERROR': 1}, 'earliest': '2024-01-15 10:00:01', 'latest': '2024-01-15 10:00:05', 'total': 2}", "explanation": "Multi-level count and min/max"},
                {"input": "[]", "expected_output": "{'counts': {}, 'earliest': None, 'latest': None, 'total': 0}", "explanation": "Empty input"},
            ],
            "acceptance_criteria": ["Counts each severity level", "Returns earliest and latest timestamps", "Handles empty input"],
            "hints": ["Use split() to extract date, time, and [LEVEL]", "Skip lines that don't match"],
        }
    elif "pandas" in sk:
        c = {
            "title": "DataFrame Cleaning Pipeline",
            "problem_statement": "Load a CSV, drop rows with missing target, fill numeric NaNs with the column median, return the cleaned DataFrame.",
            "starter_code": "import pandas as pd\n\ndef clean_dataframe(df: pd.DataFrame, target_col: str) -> pd.DataFrame:\n    # TODO\n    return df\n",
            "test_cases": [{"input": "3-row df with 1 NaN", "expected_output": "No null target, NaN imputed", "explanation": "Standard cleaning"}],
            "acceptance_criteria": ["No NaN in target", "Numeric NaNs imputed"],
            "hints": ["df.dropna(subset=[target_col])", "df.fillna(df.median(numeric_only=True))"],
        }
    elif "linear" in sk or "algebra" in sk:
        c = {
            "title": "Transpose a Matrix",
            "problem_statement": "Implement transpose(A) for a matrix as a list of lists.",
            "starter_code": "from typing import List\n\ndef transpose(A: List[List[float]]) -> List[List[float]]:\n    # TODO\n    return []\n",
            "test_cases": [{"input": "[[1,2,3],[4,5,6]]", "expected_output": "[[1,4],[2,5],[3,6]]", "explanation": "2x3 -> 3x2"}],
            "acceptance_criteria": ["Correct transpose", "Works for 1x1"],
            "hints": ["New rows = old columns", "zip(*A)"],
        }
    elif "stat" in sk:
        c = {
            "title": "Mean, Median, Mode Calculator",
            "problem_statement": "Implement mean, median, mode for a list of numbers.",
            "starter_code": "from typing import List\nfrom collections import Counter\n\ndef mean(data: List[float]) -> float:\n    return 0.0\n\ndef median(data: List[float]) -> float:\n    return 0.0\n\ndef mode(data: List[float]) -> float:\n    return 0.0\n",
            "test_cases": [{"input": "[1,2,2,3,4]", "expected_output": "mean=2.4, median=2, mode=2", "explanation": "Basic stats"}],
            "acceptance_criteria": ["Correct mean", "Correct median", "Correct mode"],
            "hints": ["sum/len", "sort then middle", "Counter.most_common"],
        }
    elif "sql" in sk:
        c = {
            "title": "Top Customers by Revenue",
            "problem_statement": "Write a SQL query returning the top 5 customers by total order amount. Tables: customers(id,name), orders(id,customer_id,amount).",
            "starter_code": "-- Tables: customers(id, name), orders(id, customer_id, amount)\nSELECT c.name, SUM(o.amount) AS total\nFROM customers c\nJOIN orders o ON c.id = o.customer_id\nGROUP BY c.id, c.name\nORDER BY total DESC\nLIMIT 5;\n",
            "test_cases": [{"input": "orders DB", "expected_output": "Top 5 by total DESC", "explanation": "Aggregation + ranking"}],
            "acceptance_criteria": ["JOIN", "GROUP BY customer", "ORDER BY total DESC LIMIT 5"],
            "hints": ["JOIN customers to orders", "SUM(amount) GROUP BY"],
        }
    elif "tableau" in sk:
        c = {
            "title": "Tableau Sales Dashboard Spec",
            "problem_statement": "Design a Tableau workbook that visualizes monthly revenue by region. Write the specification as a numbered build sheet.",
            "starter_code": "# Tableau Dashboard Build Sheet\n# 1. Data Source: orders.csv (order_id, date, region, amount)\n# 2. Connection: Extract\n# 3. Dimensions: [Region], [Order Date]\n# 4. Measures: SUM([Amount]) AS Revenue\n# 5. Calculated Field: MoM Growth = (SUM([Amount]) - LOOKUP(SUM([Amount]), -1)) / LOOKUP(SUM([Amount]), -1)\n# 6. Sheet 1: Line chart — Month vs Revenue, color by Region\n# 7. Sheet 2: Bar chart — Region vs Revenue\n# 8. Dashboard: combine sheets, add Region filter\n# TODO: Fill in YoY growth calculation.\n",
            "test_cases": [{"input": "orders.csv", "expected_output": "12 points per region, MoM % on hover", "explanation": "Time-series dashboard"}],
            "acceptance_criteria": ["Extract connection", "Two sheets on one dashboard", "MoM field uses LOOKUP"],
            "hints": ["LOOKUP(expr, -1) = previous row", "Quick Table Calculation → Percent Difference"],
        }
    elif "machine" in sk or "ml pipelines" in sk or "pytorch" in sk:
        c = {
            "title": "Accuracy Score Calculator",
            "problem_statement": "Implement accuracy(y_true, y_pred) returning the fraction of correct predictions.",
            "starter_code": "from typing import List\n\ndef accuracy(y_true: List, y_pred: List) -> float:\n    # TODO\n    return 0.0\n",
            "test_cases": [{"input": "[0,1,1,0], [0,1,0,0]", "expected_output": "0.75", "explanation": "3 of 4 correct"}],
            "acceptance_criteria": ["Correct fraction", "Handles all-correct"],
            "hints": ["count matches / length"],
        }
    elif "react" in sk:
        c = {
            "title": "React Searchable List Component",
            "problem_statement": "Build <SearchableList items={string[]} /> with a text filter using useState + useMemo.",
            "starter_code": "import { useState, useMemo } from 'react';\n\nexport default function SearchableList({ items }) {\n  const [query, setQuery] = useState('');\n  const filtered = useMemo(() => {\n    // TODO: filter items by query (case-insensitive)\n    return items;\n  }, [items, query]);\n\n  return (\n    <div>\n      <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder=\"Search...\" />\n      <ul>{filtered.map((item) => <li key={item}>{item}</li>)}</ul>\n    </div>\n  );\n}\n",
            "test_cases": [{"input": "items=['Apple','Banana'], query='an'", "expected_output": "Renders only 'Banana'", "explanation": "Case-insensitive"}],
            "acceptance_criteria": ["Uses useMemo", "Case-insensitive", "Controlled input"],
            "hints": ["items.filter(i => i.toLowerCase().includes(query.toLowerCase()))"],
        }
    elif "node" in sk:
        c = {
            "title": "Express JSON API Endpoint",
            "problem_statement": "Build an Express server exposing GET /api/users/:id returning JSON or 404.",
            "starter_code": "const express = require('express');\nconst app = express();\n\nconst USERS = { '1': { id: 1, name: 'Ada' }, '2': { id: 2, name: 'Alan' } };\n\napp.get('/api/users/:id', (req, res) => {\n  // TODO: validate id, look up user, respond 200 or 404\n  res.status(501).json({ error: 'not implemented' });\n});\n\napp.listen(3000);\n",
            "test_cases": [{"input": "GET /api/users/1", "expected_output": "200 {id:1,name:'Ada'}", "explanation": "Happy path"}, {"input": "GET /api/users/999", "expected_output": "404", "explanation": "Not found"}],
            "acceptance_criteria": ["Express routing", "Numeric id validation", "Correct status codes"],
            "hints": ["Number.isInteger(Number(req.params.id))"],
        }
    elif "html" in sk or "css" in sk:
        c = {
            "title": "Responsive Card Grid (HTML + CSS)",
            "problem_statement": "Responsive product grid: 3-up desktop, 2-up tablet, 1-up mobile — no JS.",
            "starter_code": "<!DOCTYPE html>\n<html>\n<head>\n<style>\n  .grid { display: grid; /* TODO: responsive columns */ gap: 1rem; padding: 1rem; }\n  .card { /* TODO */ }\n</style>\n</head>\n<body>\n<div class=\"grid\">\n  <div class=\"card\">Card 1</div>\n  <div class=\"card\">Card 2</div>\n  <div class=\"card\">Card 3</div>\n</div>\n</body>\n</html>\n",
            "test_cases": [{"input": "Viewport ≥1024px", "expected_output": "3 columns", "explanation": "Desktop"}, {"input": "Viewport <768px", "expected_output": "1 column", "explanation": "Mobile"}],
            "acceptance_criteria": ["CSS Grid", "No JS", "Responsive at 3 breakpoints"],
            "hints": ["grid-template-columns: repeat(auto-fit, minmax(280px, 1fr))"],
        }
    elif "javascript" in sk or "js" in sk:
        c = {
            "title": "Debounce Helper",
            "problem_statement": "Implement debounce(fn, waitMs).",
            "starter_code": "function debounce(fn, waitMs) {\n  let timer = null;\n  return function (...args) {\n    // TODO\n  };\n}\n",
            "test_cases": [{"input": "rapid calls", "expected_output": "fn runs once with last args", "explanation": "Classic debounce"}],
            "acceptance_criteria": ["Only last call runs", "Timer cleared on new calls"],
            "hints": ["setTimeout + clearTimeout"],
        }
    elif "rest" in sk or "api" in sk:
        c = {
            "title": "REST Client with Retry & Backoff",
            "problem_statement": "Write fetchWithRetry(url, {retries=3, baseDelayMs=200}) with exponential backoff.",
            "starter_code": "export async function fetchWithRetry(url, { retries = 3, baseDelayMs = 200 } = {}) {\n  // TODO\n  throw new Error('not implemented');\n}\n",
            "test_cases": [{"input": "500 then 200", "expected_output": "JSON on 2nd attempt", "explanation": "Retry on 5xx"}],
            "acceptance_criteria": ["Exponential backoff", "Only retries 5xx"],
            "hints": ["await new Promise(r => setTimeout(r, delay))"],
        }
    elif "docker" in sk:
        c = {
            "title": "Multi-stage Dockerfile for a Python API",
            "problem_statement": "Multi-stage Dockerfile: builder installs deps, final runs uvicorn on 8000.",
            "starter_code": "FROM python:3.11-slim AS builder\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install --user -r requirements.txt\n\nFROM python:3.11-slim\nWORKDIR /app\nCOPY --from=builder /root/.local /root/.local\nCOPY . .\nENV PATH=/root/.local/bin:$PATH\nEXPOSE 8000\nCMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n",
            "test_cases": [{"input": "docker build .", "expected_output": "Image builds", "explanation": "Multi-stage"}],
            "acceptance_criteria": ["Multi-stage build", "EXPOSE 8000", "Runs uvicorn"],
            "hints": ["builder stage for pip"],
        }
    elif "kubernetes" in sk or "k8s" in sk:
        c = {
            "title": "Kubernetes Deployment + Service",
            "problem_statement": "Write deployment.yaml + service.yaml: 3 replicas, probes, ClusterIP.",
            "starter_code": "apiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: web\nspec:\n  replicas: 3\n  selector:\n    matchLabels: { app: web }\n  template:\n    metadata:\n      labels: { app: web }\n    spec:\n      containers:\n        - name: web\n          image: myorg/web:1.0\n          ports: [{ containerPort: 8000 }]\n          # TODO: add livenessProbe + readinessProbe\n---\napiVersion: v1\nkind: Service\nmetadata:\n  name: web\nspec:\n  selector: { app: web }\n  ports: [{ port: 80, targetPort: 8000 }]\n  type: ClusterIP\n",
            "test_cases": [{"input": "kubectl apply", "expected_output": "3 pods Running", "explanation": "Replica count"}],
            "acceptance_criteria": ["replicas: 3", "probes", "ClusterIP"],
            "hints": ["httpGet.path: /healthz"],
        }
    elif "ci/cd" in sk or "pipeline" in sk:
        c = {
            "title": "GitHub Actions CI Pipeline",
            "problem_statement": "Write .github/workflows/ci.yml: lint + tests on 3.11, cache pip, fail on coverage <80%.",
            "starter_code": "name: CI\non:\n  push: { branches: [main] }\n  pull_request:\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - uses: actions/setup-python@v5\n        with: { python-version: '3.11' }\n      - name: Cache pip\n        # TODO: actions/cache@v4\n      - run: pip install -r requirements.txt\n      - run: ruff check .\n      - run: pytest --cov=app --cov-fail-under=80\n",
            "test_cases": [{"input": "push to main", "expected_output": "Workflow green", "explanation": "Happy path"}],
            "acceptance_criteria": ["push + PR triggers", "Caches pip", "Fails under 80%"],
            "hints": ["actions/cache@v4 with hashFiles key"],
        }
    elif "aws" in sk or "cloud" in sk:
        c = {
            "title": "S3 + CloudFront Static Hosting Spec",
            "problem_statement": "Write a spec for S3 + CloudFront static site with HTTPS and cache invalidation.",
            "starter_code": "# S3 + CloudFront Spec\n# 1. S3 bucket my-site-prod, static hosting\n# 2. Block public access; serve only via CloudFront OAC\n# 3. CloudFront distribution with origin = S3 REST endpoint\n# 4. ACM certificate for my-site.example.com\n# 5. Route 53 alias -> CloudFront\n# 6. Deploy: aws s3 sync ./dist s3://my-site-prod --delete\n# 7. Invalidate: aws cloudfront create-invalidation --distribution-id XXX --paths '/*'\n# TODO: add Bucket Policy for CloudFront OAC\n",
            "test_cases": [{"input": "Deploy", "expected_output": "HTTPS on custom domain", "explanation": "E2E"}],
            "acceptance_criteria": ["S3 not public", "CloudFront OAC", "ACM cert valid"],
            "hints": ["OAC replaced OAI in 2022+"],
        }
    elif "git" in sk:
        c = {
            "title": "Recover a Lost Commit with Reflog",
            "problem_statement": "You hard-reset away a commit. Write the exact Git commands to find and restore it.",
            "starter_code": "# Scenario: git reset --hard HEAD~1 lost work.\n# 1. git reflog\n# 2. Find lost SHA (e.g. a1b2c3d)\n# 3. git branch recovered a1b2c3d\n# TODO: Write the single command to recover onto current branch.\n",
            "test_cases": [{"input": "post reset --hard", "expected_output": "Lost commit recovered", "explanation": "Reflog recovery"}],
            "acceptance_criteria": ["Uses reflog", "No data loss"],
            "hints": ["git reset --hard <sha> or git branch <new> <sha>"],
        }
    else:
        c = {
            "title": f"{skill} Core Challenge",
            "problem_statement": f"Implement a practical utility demonstrating key {skill} concepts.",
            "starter_code": f"# Challenge: {skill}\n\ndef solve(input_data):\n    # TODO\n    return input_data\n",
            "test_cases": [{"input": "\"hello\"", "expected_output": "hello", "explanation": "Basic case"}],
            "acceptance_criteria": ["Implements core behavior", "Handles edge cases"],
            "hints": ["Start with the function signature"],
        }

    return {
        "title": c["title"], "difficulty": level, "skill": skill, "language": lang,
        "problem_statement": c["problem_statement"], "starter_code": c["starter_code"],
        "test_cases": c["test_cases"], "acceptance_criteria": c["acceptance_criteria"],
        "hints": c.get("hints", []),
        "learning_objectives": [f"Apply core {skill} techniques", "Write clean, testable code"],
        "est_hours": 1.5 if level == "beginner" else 2.0,
    }


def generate_practice_task(skill: str, level: str = "intermediate", context: str = "") -> Dict[str, Any]:
    prompt = f"""Create one coding challenge for skill "{skill}" at level "{level}".
Return ONLY JSON with keys: title, difficulty, skill, language, problem_statement, starter_code,
test_cases (list of {{input, expected_output, explanation}}), acceptance_criteria, hints, learning_objectives, est_hours.
Starter code must be real code with TODOs. Seed: {int(time.time()*1000)%100000}"""
    try:
        raw = call_llm(prompt, system_prompt="Return pure JSON only.")
        data = json.loads(clean_json(raw))
        thin = (not data.get("starter_code") or not data.get("test_cases") or len(str(data.get("problem_statement", ""))) < 40)
        if thin:
            return _fallback_challenge(skill, level)
        data.setdefault("skill", skill)
        data.setdefault("difficulty", level)
        data.setdefault("est_hours", 1.5)
        data.setdefault("language", _language_for(skill))
        return data
    except Exception:
        return _fallback_challenge(skill, level)


def generate_project_idea(target_role: str, known_skills: List[str], target_gap: str, level: str = "intermediate") -> Dict[str, Any]:
    random.seed(int(time.time() * 1000) % 100000)
    templates = [
        {
            "title": f"Smart {target_gap} Insight Engine",
            "problem_statement": f"Build a tool that uses {target_gap} to surface insights automatically.",
            "proposed_solution": f"Pipeline: ingest → {target_gap} process → report.",
            "architecture": {"overview": f"Ingestion → {target_gap} engine → reporter", "components": ["Ingestion", f"{target_gap} Engine", "Reporter"], "data_flow": "input → process → insights"},
            "milestones": [
                {"name": "Milestone 1: Foundation", "deliverables": ["Skeleton", "Data loader", "Tests"], "est_hours": 1.5},
                {"name": "Milestone 2: Core", "deliverables": [f"{target_gap} logic", "Scoring", "E2E"], "est_hours": 2.5},
                {"name": "Milestone 3: Polish", "deliverables": ["CLI", "README", "Docker optional"], "est_hours": 1.5},
            ],
        },
        {
            "title": f"{target_role.replace('_', ' ').title()} Assistant – {target_gap}",
            "problem_statement": f"Productivity tool powered by {target_gap}.",
            "proposed_solution": f"Inputs → {target_gap} → recommendations.",
            "architecture": {"overview": "Adapter → core → recommendations", "components": ["Input Adapter", f"{target_gap} Core", "Reco Layer"], "data_flow": "input → analysis → report"},
            "milestones": [
                {"name": "Milestone 1: Scaffold", "deliverables": ["Schemas", "Stubs", "Harness"], "est_hours": 1.5},
                {"name": "Milestone 2: Logic", "deliverables": [f"{target_gap} impl", "3 scenarios"], "est_hours": 2.5},
                {"name": "Milestone 3: Ship", "deliverables": ["CLI", "Docs", "README"], "est_hours": 1.5},
            ],
        },
    ]
    t = random.choice(templates)
    folder = "project-root/\n├── src/\n│   ├── config.py\n│   ├── data/\n│   │   └── loader.py\n│   ├── engine/\n│   │   └── core.py\n│   └── api/\n│       └── app.py\n├── tests/\n├── Dockerfile\n└── README.md"
    return {
        "title": t["title"], "description": t["problem_statement"],
        "problem_statement": t["problem_statement"], "proposed_solution": t["proposed_solution"],
        "architecture": t["architecture"], "folder_structure": folder,
        "tech_stack": [target_gap] + (known_skills or [])[:3],
        "milestones": t["milestones"],
        "learning_outcomes": [f"Master {target_gap} in a realistic context", "Ship a small complete system"],
        "target_skills": [target_gap] + (known_skills or [])[:2],
        "est_hours": 5.0,
    }