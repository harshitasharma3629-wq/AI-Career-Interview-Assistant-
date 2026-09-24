# AI Career & Interview Assistant

A Python toolkit that helps job seekers prepare for interviews. It has two parts that share one codebase:

1. **Resume screener** (`resume_analyzer.py`) – scores a resume against a job description from 0 to 100 using TF-IDF vectorisation and cosine similarity, and lists the job-description keywords the resume already covers and the ones it is missing. Reads `.txt` and `.pdf` resumes (PDF needs `pypdf`).
2. **Mock-interview engine** (`interview_engine.py`) – builds a question set for a target role from a JSON question bank and scores typed answers out of 10 using answer length, keyword coverage, filler-word usage, and a STAR-structure check for behavioural questions.

`__init__.py` wraps both parts as a Flask blueprint (`/career-assistant/`) with a JSON API for stepping through a mock interview.

## Data

| File | Contents |
|---|---|
| `data/question_bank.json` | 221 questions across 13 categories (Python, OOP, SQL, DBMS, ML, data analysis, behavioural, frontend, backend, DevOps, system design, QA, product management) |
| `data/role_mapping.json` | 12 target roles, each mapped to the categories it draws questions from |

## Setup

Requires Python 3.10 or newer.

```bash
pip install -r requirements.txt
```

## Quick use (no web server needed)

Run from the folder that contains this project:

```python
from resume_analyzer import analyze
from interview_engine import generate_questions, score_answer

result = analyze("your resume text", "job description text")
print(result["match_score"], result["missing_keywords"])

questions = generate_questions("python developer", num_questions=5)
print(score_answer(questions[0], "my typed answer ..."))
```

## Flask blueprint

`__init__.py` registers the `career_assistant` blueprint. To use it inside a Flask app, place this folder as a package and provide a `templates/career_assistant/index.html` page. API routes:

- `POST /career-assistant/analyze` – resume vs job description
- `POST /career-assistant/questions` – questions for a role
- `POST /career-assistant/api/mock-interview/start` – JSON question set
- `POST /career-assistant/api/mock-interview/score` – score one answer
- `POST /career-assistant/api/mock-interview/summary` – session summary

## How scoring works (out of 10)

- Length: up to 3 points
- Keyword coverage: up to 5 points
- Filler words ("um", "uh", "like", ...): 1 point if used sparingly
- STAR result/outcome wording (behavioural questions): 1 point

Scoring is a simple heuristic, not a trained model.

## Tech

Python · scikit-learn · Flask · pypdf
