"""
interview_engine.py
---------------------
Loads the question bank, generates a question set for a target role, and
scores a candidate's typed answers using keyword coverage, length, and
(for behavioral questions) a lightweight STAR-structure heuristic.
"""
import json
import random
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
FILLER_PATTERN = re.compile(
    r"\b(?:um|uh|like|you know|basically|actually|sort of|kind of)\b", re.IGNORECASE
)
STAR_HINT_WORDS = {"result", "achieved", "improved", "learned", "outcome", "impact", "reduced", "increased"}


def load_question_bank() -> dict:
    with open(DATA_DIR / "question_bank.json", encoding="utf-8") as f:
        return json.load(f)


def load_role_mapping() -> dict:
    with open(DATA_DIR / "role_mapping.json", encoding="utf-8") as f:
        return json.load(f)


def available_roles() -> list:
    return sorted(load_role_mapping().keys())


def generate_questions(role: str, num_questions: int = 6, seed: int | None = None) -> list:
    """Builds a question set for `role` by sampling across its mapped categories."""
    bank = load_question_bank()
    mapping = load_role_mapping()

    role_key = role.strip().lower()
    categories = mapping.get(role_key)
    if categories is None:
        raise ValueError(
            f"Unknown role '{role}'. Available roles: {', '.join(available_roles())}"
        )

    pool = []
    for cat in categories:
        for item in bank.get(cat, []):
            pool.append({**item, "category": cat})

    rng = random.Random(seed)
    rng.shuffle(pool)

    # Try to keep at least one behavioral question in the mix.
    behavioral = [q for q in pool if q["category"] == "behavioral"]
    technical = [q for q in pool if q["category"] != "behavioral"]

    selected = []
    if behavioral:
        selected.append(behavioral[0])
    remaining_slots = num_questions - len(selected)
    selected += technical[:remaining_slots]

    return selected[:num_questions]


def _count_filler_words(answer: str) -> int:
    # Whole-word match, so "number" or "summary" don't count as "um".
    return len(FILLER_PATTERN.findall(answer))


def score_answer(question: dict, answer: str) -> dict:
    """Heuristic scoring out of 10 based on length, keyword coverage,
    filler-word usage, and (for behavioral questions) STAR-style structure."""
    answer = answer.strip()
    word_count = len(answer.split())
    feedback = []

    if word_count == 0:
        return {"score": 0, "feedback": ["No answer given."]}

    # --- Length component (max 3 points) ---
    if word_count < 15:
        length_score = 1
        feedback.append("Answer is quite short - try to elaborate with a concrete example.")
    elif word_count < 40:
        length_score = 2
        feedback.append("Decent length - adding one more specific detail or outcome would help.")
    else:
        length_score = 3
        feedback.append("Good level of detail.")

    # --- Keyword coverage component (max 5 points) ---
    keywords = question.get("keywords", [])
    answer_lower = answer.lower()
    hit_count = sum(1 for kw in keywords if kw.lower() in answer_lower)
    coverage_ratio = hit_count / len(keywords) if keywords else 1.0
    keyword_score = round(coverage_ratio * 5)
    if keywords:
        if coverage_ratio < 0.34:
            feedback.append(
                f"Try to mention concepts like: {', '.join(keywords)}."
            )
        elif coverage_ratio < 0.7:
            missing = [k for k in keywords if k.lower() not in answer_lower]
            feedback.append(f"Good start - you could also touch on: {', '.join(missing)}.")
        else:
            feedback.append("Strong use of relevant technical terms.")

    # --- Filler words (max 1 point, deduct if overused) ---
    filler_count = _count_filler_words(answer)
    filler_score = 1 if filler_count <= 1 else 0
    if filler_count > 1:
        feedback.append(f"Watch filler words ('um', 'like', etc.) - counted {filler_count}.")

    # --- STAR structure for behavioral questions (max 1 point) ---
    star_score = 0
    if question.get("category") == "behavioral":
        if any(w in answer_lower for w in STAR_HINT_WORDS):
            star_score = 1
            feedback.append("Nice - you included a clear outcome/result (good STAR structure).")
        else:
            feedback.append(
                "For behavioral questions, close with the RESULT: what changed or what you learned."
            )
    else:
        star_score = 1  # not applicable, don't penalize technical answers

    total = length_score + keyword_score + filler_score + star_score
    return {"score": min(total, 10), "feedback": feedback}


def summarize_session(results: list) -> dict:
    if not results:
        return {"average_score": 0, "total_questions": 0}
    avg = sum(r["score"] for r in results) / len(results)
    return {
        "average_score": round(avg, 1),
        "total_questions": len(results),
        "strongest": max(results, key=lambda r: r["score"]),
        "weakest": min(results, key=lambda r: r["score"]),
    }
