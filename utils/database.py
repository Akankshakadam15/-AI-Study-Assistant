"""
utils/database.py
SQLite database setup and all CRUD operations
"""

import sqlite3
import bcrypt
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "study_assistant.db")


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = get_connection()
    c = conn.cursor()

    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Notes table
    c.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            subject TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # Summaries table
    c.execute("""
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            note_id INTEGER,
            title TEXT,
            summary_text TEXT NOT NULL,
            key_points TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # Questions table
    c.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            note_id INTEGER,
            question_type TEXT,
            question_data TEXT NOT NULL,
            subject TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # Quiz attempts table
    c.execute("""
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject TEXT,
            score INTEGER,
            total INTEGER,
            attempted_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # Study planner table
    c.execute("""
        CREATE TABLE IF NOT EXISTS study_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            exam_name TEXT,
            exam_date TEXT,
            subjects TEXT,
            plan_data TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # Topics progress table
    c.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            topic_name TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            confidence INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # Doubts table
    c.execute("""
        CREATE TABLE IF NOT EXISTS doubts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            answer TEXT,
            subject TEXT,
            asked_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# ─── USER FUNCTIONS ────────────────────────────────────────────────────────────

def create_user(username, password, email=""):
    conn = get_connection()
    try:
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        conn.execute(
            "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
            (username, hashed, email)
        )
        conn.commit()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    finally:
        conn.close()


def verify_user(username, password):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    if row and bcrypt.checkpw(password.encode(), row["password_hash"].encode()):
        return True, dict(row)
    return False, None


def get_user_by_id(user_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ─── NOTES FUNCTIONS ──────────────────────────────────────────────────────────

def save_note(user_id, title, content, subject="General"):
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO notes (user_id, title, content, subject) VALUES (?,?,?,?)",
        (user_id, title, content, subject)
    )
    note_id = cur.lastrowid
    conn.commit()
    conn.close()
    return note_id


def get_notes(user_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM notes WHERE user_id=? ORDER BY created_at DESC", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_note(note_id, user_id):
    conn = get_connection()
    conn.execute("DELETE FROM notes WHERE id=? AND user_id=?", (note_id, user_id))
    conn.commit()
    conn.close()


# ─── SUMMARY FUNCTIONS ───────────────────────────────────────────────────────

def save_summary(user_id, title, summary_text, key_points, note_id=None):
    conn = get_connection()
    conn.execute(
        "INSERT INTO summaries (user_id, note_id, title, summary_text, key_points) VALUES (?,?,?,?,?)",
        (user_id, note_id, title, summary_text, key_points)
    )
    conn.commit()
    conn.close()


def get_summaries(user_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM summaries WHERE user_id=? ORDER BY created_at DESC", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── QUESTION FUNCTIONS ──────────────────────────────────────────────────────

def save_questions(user_id, question_data, question_type, subject, note_id=None):
    conn = get_connection()
    conn.execute(
        "INSERT INTO questions (user_id, note_id, question_type, question_data, subject) VALUES (?,?,?,?,?)",
        (user_id, note_id, question_type, question_data, subject)
    )
    conn.commit()
    conn.close()


def get_questions(user_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM questions WHERE user_id=? ORDER BY created_at DESC", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── QUIZ FUNCTIONS ──────────────────────────────────────────────────────────

def save_quiz_result(user_id, subject, score, total):
    conn = get_connection()
    conn.execute(
        "INSERT INTO quiz_attempts (user_id, subject, score, total) VALUES (?,?,?,?)",
        (user_id, subject, score, total)
    )
    conn.commit()
    conn.close()


def get_quiz_history(user_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM quiz_attempts WHERE user_id=? ORDER BY attempted_at DESC", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── STUDY PLAN FUNCTIONS ────────────────────────────────────────────────────

def save_study_plan(user_id, exam_name, exam_date, subjects, plan_data):
    conn = get_connection()
    conn.execute(
        "INSERT INTO study_plans (user_id, exam_name, exam_date, subjects, plan_data) VALUES (?,?,?,?,?)",
        (user_id, exam_name, exam_date, subjects, plan_data)
    )
    conn.commit()
    conn.close()


def get_study_plans(user_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM study_plans WHERE user_id=? ORDER BY created_at DESC", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── TOPICS / PROGRESS FUNCTIONS ────────────────────────────────────────────

def add_topic(user_id, subject, topic_name):
    conn = get_connection()
    conn.execute(
        "INSERT INTO topics (user_id, subject, topic_name) VALUES (?,?,?)",
        (user_id, subject, topic_name)
    )
    conn.commit()
    conn.close()


def get_topics(user_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM topics WHERE user_id=? ORDER BY subject, topic_name", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_topic_status(topic_id, status, confidence):
    conn = get_connection()
    conn.execute(
        "UPDATE topics SET status=?, confidence=?, updated_at=? WHERE id=?",
        (status, confidence, datetime.now().isoformat(), topic_id)
    )
    conn.commit()
    conn.close()


def delete_topic(topic_id):
    conn = get_connection()
    conn.execute("DELETE FROM topics WHERE id=?", (topic_id,))
    conn.commit()
    conn.close()


# ─── DOUBTS FUNCTIONS ────────────────────────────────────────────────────────

def save_doubt(user_id, question, answer, subject):
    conn = get_connection()
    conn.execute(
        "INSERT INTO doubts (user_id, question, answer, subject) VALUES (?,?,?,?)",
        (user_id, question, answer, subject)
    )
    conn.commit()
    conn.close()


def get_doubts(user_id, limit=20):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM doubts WHERE user_id=? ORDER BY asked_at DESC LIMIT ?",
        (user_id, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
