"""
utils/ai_helper.py
All AI-powered functions using Groq API (Free & Fast!)
"""

import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_MODEL = "llama-3.3-70b-versatile"# Free & powerful model

def get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set in .env file")
    return Groq(api_key=api_key)


def _call_groq(system_prompt: str, user_message: str, max_tokens: int = 1500) -> str:
    """Core function to call Groq API."""
    client = get_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content


# ── 1. NOTE SUMMARIZER ────────────────────────────────────────────────────────

def summarize_notes(notes_text: str, subject: str = "General") -> dict:
    """
    Summarize notes into overview + key points.
    Returns dict with 'overview' and 'key_points' (list).
    """
    system = """You are an expert study assistant helping students understand their notes.
Respond ONLY with valid JSON in this exact format:
{
  "overview": "2-3 sentence overview of the notes",
  "key_points": ["point 1", "point 2", "point 3", ...],
  "important_terms": ["term: definition", ...],
  "difficulty": "Easy/Medium/Hard"
}
Keep language clear and student-friendly. Maximum 8 key points."""

    prompt = f"Subject: {subject}\n\nNotes to summarize:\n{notes_text}"
    raw = _call_groq(system, prompt, max_tokens=1200)
    try:
        clean = re.sub(r"```json|```", "", raw).strip()
        return json.loads(clean)
    except Exception:
        return {
            "overview": raw[:500],
            "key_points": ["Could not parse structured response. See overview."],
            "important_terms": [],
            "difficulty": "Unknown"
        }


# ── 2. QUESTION GENERATOR ─────────────────────────────────────────────────────

def generate_questions(notes_text: str, q_type: str = "MCQ", count: int = 5, subject: str = "General") -> list:
    """
    Generate questions from notes.
    q_type: 'MCQ' | 'Short' | 'Viva'
    Returns list of question dicts.
    """
    if q_type == "MCQ":
        system = """You are a question paper setter. Generate MCQ questions from the given notes.
Respond ONLY with valid JSON array:
[
  {
    "question": "Question text?",
    "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
    "answer": "A",
    "explanation": "Why this is correct"
  }
]"""
        prompt = f"Subject: {subject}\nGenerate {count} MCQ questions from:\n{notes_text}"

    elif q_type == "Short":
        system = """You are a question paper setter. Generate short answer questions from the given notes.
Respond ONLY with valid JSON array:
[
  {
    "question": "Question text?",
    "answer": "Expected answer (2-4 sentences)",
    "marks": 2
  }
]"""
        prompt = f"Subject: {subject}\nGenerate {count} short answer questions from:\n{notes_text}"

    else:  # Viva
        system = """You are a viva examiner. Generate viva/oral exam questions from the given notes.
Respond ONLY with valid JSON array:
[
  {
    "question": "Viva question?",
    "answer": "Detailed expected answer",
    "follow_up": "Possible follow-up question"
  }
]"""
        prompt = f"Subject: {subject}\nGenerate {count} viva questions from:\n{notes_text}"

    raw = _call_groq(system, prompt, max_tokens=1500)
    try:
        clean = re.sub(r"```json|```", "", raw).strip()
        return json.loads(clean)
    except Exception:
        return []


# ── 3. DOUBT SOLVER ───────────────────────────────────────────────────────────

def solve_doubt(question: str, subject: str = "General", context: str = "") -> str:
    """
    Solve a student's doubt with a clear explanation.
    """
    system = f"""You are a patient, expert tutor specializing in {subject}.
Explain concepts clearly to a student:
- Use simple language
- Give real-world examples where possible
- Break down complex topics step by step
- End with a quick summary tip
Keep your answer focused and under 400 words."""

    user_msg = f"Subject: {subject}\n"
    if context:
        user_msg += f"Context from my notes: {context[:500]}\n\n"
    user_msg += f"My doubt: {question}"

    return _call_groq(system, user_msg, max_tokens=800)


# ── 4. STUDY PLANNER ──────────────────────────────────────────────────────────

def generate_study_plan(exam_name: str, exam_date: str, subjects: list, hours_per_day: int, weak_subjects: list = []) -> dict:
    """
    Generate a day-by-day study timetable until exam date.
    Returns dict with 'plan' (list of day dicts) and 'tips'.
    """
    subjects_str = ", ".join(subjects)
    weak_str = ", ".join(weak_subjects) if weak_subjects else "None specified"

    system = """You are a study coach creating a personalized study plan.
Respond ONLY with valid JSON:
{
  "plan": [
    {
      "day": 1,
      "date": "DD-MM-YYYY",
      "schedule": [
        {"time": "9:00 AM - 11:00 AM", "subject": "Math", "topic": "Algebra", "type": "Study"},
        {"time": "11:15 AM - 12:15 PM", "subject": "Science", "topic": "Review", "type": "Revision"}
      ]
    }
  ],
  "tips": ["Tip 1", "Tip 2", "Tip 3"],
  "weekly_targets": {"Math": "Ch 1-3", "Science": "Unit 1"}
}
Keep plan realistic. Include breaks. Prioritize weak subjects."""

    prompt = f"""
Exam: {exam_name}
Exam Date: {exam_date}
Subjects: {subjects_str}
Weak Subjects: {weak_str}
Available study hours per day: {hours_per_day}
Create a complete study plan from today until exam date."""

    raw = _call_groq(system, prompt, max_tokens=2000)
    try:
        clean = re.sub(r"```json|```", "", raw).strip()
        return json.loads(clean)
    except Exception:
        return {"plan": [], "tips": [raw[:300]], "weekly_targets": {}}


# ── 5. QUIZ GENERATOR ─────────────────────────────────────────────────────────

def generate_quiz(topic: str, difficulty: str = "Medium", count: int = 10) -> list:
    """
    Generate a quick quiz on a topic.
    Returns list of MCQ dicts.
    """
    system = """You are a quiz master. Generate engaging quiz questions.
Respond ONLY with valid JSON array:
[
  {
    "question": "Question?",
    "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
    "answer": "B",
    "explanation": "Brief explanation"
  }
]"""

    prompt = f"Topic: {topic}\nDifficulty: {difficulty}\nGenerate {count} MCQ quiz questions."
    raw = _call_groq(system, prompt, max_tokens=1500)
    try:
        clean = re.sub(r"```json|```", "", raw).strip()
        return json.loads(clean)
    except Exception:
        return []


# ── 6. FLASHCARD GENERATOR ────────────────────────────────────────────────────

def generate_flashcards(notes_text: str, count: int = 8) -> list:
    """Generate flashcard-style Q&A from notes."""
    system = """Generate study flashcards from the notes.
Respond ONLY with valid JSON array:
[{"front": "Term or Question", "back": "Definition or Answer"}]"""

    raw = _call_groq(system, f"Generate {count} flashcards from:\n{notes_text}", max_tokens=800)
    try:
        clean = re.sub(r"```json|```", "", raw).strip()
        return json.loads(clean)
    except Exception:
        return []