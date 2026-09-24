"""
AI Career & Interview Assistant - Flask blueprint.
Wraps resume_analyzer.py and interview_engine.py (unchanged from the
standalone version) behind /career-assistant/ routes.
"""
from flask import Blueprint, render_template, request, jsonify

from . import resume_analyzer
from . import interview_engine

bp = Blueprint("career_assistant", __name__, url_prefix="/career-assistant")


@bp.route("/", methods=["GET"])
def index():
    return render_template("career_assistant/index.html", active="career_assistant", roles=interview_engine.available_roles())


@bp.route("/analyze", methods=["POST"])
def analyze():
    resume_text = request.form.get("resume_text", "")
    jd_text = request.form.get("jd_text", "")
    result = None
    error = None
    if not resume_text.strip() or not jd_text.strip():
        error = "Please paste both your resume text and the job description."
    else:
        result = resume_analyzer.analyze(resume_text, jd_text)
    return render_template(
        "career_assistant/index.html",
        active="career_assistant",
        roles=interview_engine.available_roles(),
        result=result,
        error=error,
        resume_text=resume_text,
        jd_text=jd_text,
    )


@bp.route("/questions", methods=["POST"])
def questions():
    role = request.form.get("role", "")
    error = None
    generated = None
    try:
        generated = interview_engine.generate_questions(role, num_questions=6)
    except ValueError as e:
        error = str(e)
    return render_template(
        "career_assistant/index.html",
        active="career_assistant",
        roles=interview_engine.available_roles(),
        questions=generated,
        selected_role=role,
        q_error=error,
    )


# ---------------- Mock Interview (JSON API, driven by client-side JS) ----------------

@bp.route("/api/mock-interview/start", methods=["POST"])
def api_start_mock_interview():
    """Returns the question set for the chosen role, as JSON, for the
    client to step through one at a time (spoken aloud + typed answers)."""
    payload = request.get_json(silent=True) or {}
    role = payload.get("role", "")
    num_questions = payload.get("num_questions", 5)
    try:
        num_questions = max(1, min(int(num_questions), 10))
    except (TypeError, ValueError):
        num_questions = 5

    try:
        questions = interview_engine.generate_questions(role, num_questions=num_questions)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"role": role, "questions": questions})


@bp.route("/api/mock-interview/score", methods=["POST"])
def api_score_mock_answer():
    """Scores one typed answer against its question (with keywords),
    using the same heuristic as the CLI version."""
    payload = request.get_json(silent=True) or {}
    question = payload.get("question")
    answer = payload.get("answer", "")

    if not question or "question" not in question:
        return jsonify({"error": "Missing question data."}), 400

    outcome = interview_engine.score_answer(question, answer)
    return jsonify(outcome)


@bp.route("/api/mock-interview/summary", methods=["POST"])
def api_summarize_mock_interview():
    payload = request.get_json(silent=True) or {}
    results = payload.get("results", [])
    summary = interview_engine.summarize_session(results)
    # strongest/weakest hold full result dicts with feedback lists; trim to scores only for the client
    if summary.get("total_questions"):
        summary["strongest_score"] = summary.pop("strongest")["score"]
        summary["weakest_score"] = summary.pop("weakest")["score"]
    return jsonify(summary)
