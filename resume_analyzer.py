"""
resume_analyzer.py
--------------------
Compares a resume against a job description and produces:
  - an ATS-style match score (0-100), via TF-IDF cosine similarity
  - the job-description keywords the resume is missing
  - the keywords the resume already covers

No external NLP corpus downloads are required (no nltk/spacy) - a small
built-in stopword list keeps this fully offline and dependency-light.
"""
import re
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover
    PdfReader = None

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "is", "are", "was", "were",
    "be", "been", "being", "to", "of", "in", "on", "for", "with", "at",
    "by", "from", "as", "into", "about", "this", "that", "these", "those",
    "it", "its", "their", "they", "you", "your", "we", "our", "will",
    "can", "should", "would", "may", "might", "must", "have", "has",
    "had", "do", "does", "did", "not", "no", "so", "than", "then",
    "also", "such", "who", "which", "what", "when", "where", "how",
    "experience", "role", "job", "work", "working", "including", "etc",
    "years", "year", "strong", "good", "excellent", "team", "skills",
}

TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z+#\.\-]{1,}")


def read_resume_text(path: str) -> str:
    """Reads resume text from a .txt or .pdf file."""
    p = Path(path)
    if p.suffix.lower() == ".pdf":
        if PdfReader is None:
            raise RuntimeError("pypdf is required to read PDF resumes: pip install pypdf")
        reader = PdfReader(str(p))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return p.read_text(encoding="utf-8", errors="ignore")


def _tokenize(text: str) -> list:
    tokens = TOKEN_RE.findall(text.lower())
    return [t.strip(".-") for t in tokens if t.strip(".-") not in STOPWORDS and len(t) > 1]


def _top_keywords(text: str, top_n: int = 25) -> list:
    """Ranks words in `text` by TF-IDF weight against itself (single document
    term-frequency proxy) to surface the most distinctive/important terms."""
    tokens = _tokenize(text)
    if not tokens:
        return []
    vectorizer = TfidfVectorizer(stop_words=None, token_pattern=r"(?u)\b\w[\w+#\.\-]+\b")
    try:
        matrix = vectorizer.fit_transform([" ".join(tokens)])
    except ValueError:
        return []
    scores = matrix.toarray()[0]
    vocab = vectorizer.get_feature_names_out()
    ranked = sorted(zip(vocab, scores), key=lambda x: x[1], reverse=True)
    return [word for word, score in ranked[:top_n] if score > 0]


def match_score(resume_text: str, jd_text: str) -> float:
    """Cosine similarity between resume and job description, scaled 0-100."""
    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        tfidf = vectorizer.fit_transform([resume_text, jd_text])
    except ValueError:
        return 0.0
    sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return round(float(sim) * 100, 1)


def analyze(resume_text: str, jd_text: str, top_n: int = 20) -> dict:
    """Full analysis: score + missing/matched keywords."""
    score = match_score(resume_text, jd_text)

    jd_keywords = set(_top_keywords(jd_text, top_n=top_n))
    resume_tokens = set(_tokenize(resume_text))

    matched = sorted(jd_keywords & resume_tokens)
    missing = sorted(jd_keywords - resume_tokens)

    return {
        "match_score": score,
        "matched_keywords": matched,
        "missing_keywords": missing,
    }


def print_report(result: dict) -> None:
    print(f"\nATS Match Score: {result['match_score']}%")
    if result["match_score"] >= 75:
        verdict = "Strong match - resume closely aligns with this job description."
    elif result["match_score"] >= 50:
        verdict = "Moderate match - consider adding some of the missing keywords below."
    else:
        verdict = "Weak match - this resume likely needs to be tailored for this role."
    print(verdict)

    print(f"\nMatched keywords ({len(result['matched_keywords'])}):")
    print(", ".join(result["matched_keywords"]) or "  (none found)")

    print(f"\nMissing keywords ({len(result['missing_keywords'])}):")
    print(", ".join(result["missing_keywords"]) or "  (none - great coverage!)")
