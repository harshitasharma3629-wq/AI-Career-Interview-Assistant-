# AI Career & Interview Assistant

A Flask web app that helps job seekers prepare for interviews.

## Features
1. **Resume match score** - paste a resume and a job description. The app scores the match from 0 to 100 using TF-IDF vectorisation and cosine similarity, and lists the job-description keywords your resume already covers and the ones it is missing.
2. **Role-based questions** - pick a target role and get a set of interview questions drawn from a JSON question bank (221 questions, 13 categories, 12 roles).
3. **Mock interview** - an animated interviewer reads each question aloud using your browser's built-in text-to-speech (Web Speech API, no API key or internet service needed). You type your answer and get an instant score out of 10 with feedback. At the end you see the average, best and weakest scores. If your browser has no speech support, the questions still appear as text.

## How answers are scored (out of 10)
- Length: up to 3 points
- Keyword coverage: up to 5 points
- Filler words ("um", "uh", "like", ...): 1 point if used sparingly
- Behavioural questions: 1 point for mentioning a result or outcome (a STAR-style check)

This is a simple rule-based heuristic, not a trained model.

## Run it
Requires Python 3.10 or newer.
```bash
pip install -r requirements.txt
python app.py          # opens http://127.0.0.1:5000
```

## Project structure
```
app.py                        # Flask app
career_assistant/
  __init__.py                 # blueprint: pages + mock-interview JSON API
  resume_analyzer.py          # TF-IDF resume vs job description matching
  interview_engine.py         # question generation + answer scoring
  data/question_bank.json     # 221 questions in 13 categories
  data/role_mapping.json      # 12 roles mapped to categories
templates/                    # HTML pages (mock interview UI is in career_assistant/index.html)
static/style.css
```

## API routes
- `POST /career-assistant/analyze` - resume vs job description
- `POST /career-assistant/questions` - questions for a role
- `POST /career-assistant/api/mock-interview/start` - JSON question set
- `POST /career-assistant/api/mock-interview/score` - score one answer
- `POST /career-assistant/api/mock-interview/summary` - session summary

## Tech
Python, Flask, scikit-learn, pypdf
