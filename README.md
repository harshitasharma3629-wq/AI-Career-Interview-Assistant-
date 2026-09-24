# Harshita Sharma — Project Portfolio

Four projects, one app. A single Flask site with a home page linking out to
four working tools — each one previously a separate console script, now
with a real web front end.

**Run once, use all four:**
```bash
pip install -r requirements.txt
python app.py
```
Then open **http://127.0.0.1:5000** — every project is one click away from
the home page.

## What's inside

| Project | Route | What it does |
|---|---|---|
| 🏠 House Price Prediction | `/house-price/` | Estimates property price from a form (location, size, rooms, age) using a trained Random Forest regression model |
| 🔐 Image Steganography | `/steganography/` | Upload an image + a message → download an identical-looking image with the message hidden inside (LSB technique). Upload an encoded image → extract the hidden message |
| 🎓 Student Management System | `/student-management/` | Add/delete students, update GPA, mark attendance, and pull an attendance-percentage report — backed by SQLite |
| 🎯 AI Career & Interview Assistant | `/career-assistant/` | Paste a resume + job description for an ATS-style match score, generate role-specific interview questions, or start a **Mock Interview** — an animated AI interviewer avatar reads each question aloud (English, browser text-to-speech) and scores your typed answer instantly |

## Mock Interview Mode (AI-narrated)
The Career Assistant's "Mock Interview" tab is a fully interactive session:
1. Pick a role and how many questions you want.
2. An animated avatar "speaks" each question aloud using the browser's
   built-in **Web Speech API** (`speechSynthesis`) — no API keys, no
   internet service, no cost. English voice, with a "Replay" button if you
   missed it.
3. Type your answer; it's scored instantly (same heuristic as the CLI
   version) with specific feedback.
4. After the last question, see a session summary (average, best, weakest).

This only needs a browser that supports `speechSynthesis` (Chrome, Edge,
Safari all do). If a browser doesn't support it, the avatar and questions
still work — it just stays silent and you read the question text as normal.

## Project Structure
```
portfolio/
├── app.py                      # registers all 4 blueprints + home route
├── requirements.txt
├── static/
│   ├── style.css                # shared design system for every page
│   └── uploads/                 # images uploaded to the steganography tool
├── templates/
│   ├── base.html                 # shared nav + layout
│   ├── home.html                 # landing page with 4 project cards
│   ├── house_price/index.html
│   ├── steganography/index.html
│   ├── student_mgmt/index.html
│   └── career_assistant/index.html
├── house_price/
│   ├── __init__.py               # Flask blueprint + model training
│   └── data/housing.csv
├── steganography/
│   └── __init__.py               # Flask blueprint + LSB encode/decode
├── student_mgmt/
│   ├── __init__.py               # Flask blueprint (routes)
│   └── db_logic.py               # SQLite CRUD functions
└── career_assistant/
    ├── __init__.py               # Flask blueprint
    ├── resume_analyzer.py        # TF-IDF resume/JD matching
    ├── interview_engine.py       # question generation + answer scoring
    └── data/
        ├── question_bank.json
        └── role_mapping.json
```

Each project's core logic lives in its own Python package (`house_price/`,
`steganography/`, `student_mgmt/`, `career_assistant/`) as a **Flask
Blueprint** — Flask's way of keeping separate features cleanly separated
while still running under one app. `app.py` just imports and registers all
four.

## Why one combined app instead of four separate ones
- One command (`python app.py`) instead of four
- One consistent look and navigation bar across all four tools
- Easier to demo live in an interview — no switching ports/terminals
- Still shows four distinct, meaningfully different technical skills:
  regression/ML, security/bit manipulation, relational databases, and NLP/
  text processing

## Tech Stack
- **Backend:** Python, Flask
- **ML / Data:** pandas, NumPy, scikit-learn
- **Image processing:** Pillow
- **Database:** SQLite (`sqlite3`, standard library)
- **PDF parsing:** pypdf
- **Frontend:** server-rendered HTML/CSS (no JS framework — plain Flask templates + a shared stylesheet)

## Notes
- The house price model is trained once, in memory, when the app starts
  (on synthetic data — see `house_price/data/`). Restarting the app
  retrains it; there's no saved model file to keep the repo light.
- The student database (`student_mgmt/students.db`) and uploaded images
  (`static/uploads/`) are created automatically on first use and are
  git-ignored, so the repo stays clean.
