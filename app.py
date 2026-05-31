"""
app.py  —  AI Study Assistant 
Main entry point for the Streamlit application
Run with: streamlit run app.py
"""

import streamlit as st
from utils.database import init_db
from modules.auth import show_auth_page
from modules.notes_summarizer import show_notes_summarizer
from modules.question_generator import show_question_generator
from modules.doubt_solver import show_doubt_solver
from modules.study_planner import show_study_planner
from modules.quiz_mode import show_quiz_mode
from modules.progress_tracker import show_progress_tracker

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StudyAI — AI Study Assistant",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="auto"
)

# ── Custom CSS Theme ──────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background-color: #0d0f14; color: #e8eaf0; }
[data-testid="stSidebar"] { background-color: #13161e; border-right: 1px solid #252a38; }
[data-testid="stHeader"] { background: transparent; }
h1, h2, h3 { color: #e8eaf0 !important; }
p, label, .stMarkdown { color: #c9ccd4; }
.stButton > button { border-radius: 10px !important; font-weight: 600 !important; transition: all 0.2s !important; }
.stButton > button[kind="primary"] { background: linear-gradient(135deg, #7c6af7, #9b8cf9) !important; border: none !important; color: white !important; }
.stButton > button[kind="primary"]:hover { transform: translateY(-2px) !important; box-shadow: 0 4px 15px #7c6af755 !important; }
.stTextInput > div > div > input, .stTextArea > div > div > textarea, .stSelectbox > div > div { background: #1a1e29 !important; border: 1px solid #252a38 !important; color: #e8eaf0 !important; border-radius: 10px !important; }
[data-testid="stMetricValue"] { color: #7c6af7 !important; font-weight: 800 !important; }
.stTabs [data-baseweb="tab"] { color: #6b7280 !important; }
.stTabs [data-baseweb="tab"][aria-selected="true"] { color: #7c6af7 !important; }
hr { border-color: #252a38 !important; }
.stProgress > div > div { background: linear-gradient(90deg, #7c6af7, #5ddba8) !important; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #13161e; }
::-webkit-scrollbar-thumb { background: #252a38; border-radius: 3px; }

/* Delete confirmation button styling */
.delete-warning { background: #2a1a1a; border: 1px solid #f8717144;
    border-radius: 10px; padding: 14px 18px; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

# ── Init DB ───────────────────────────────────────────────────────────────────
init_db()

# ── Session State Init ────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None

# ── Auth Gate ─────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    show_auth_page()
    st.stop()


# ── History Delete Helper ─────────────────────────────────────────────────────
def delete_all_history(user_id: int, history_type: str):
    """Delete all history of given type for a user."""
    import sqlite3
    from utils.database import get_connection

    conn = get_connection()
    table_map = {
        "notes":     "notes",
        "summaries": "summaries",
        "questions": "questions",
        "quizzes":   "quiz_attempts",
        "doubts":    "doubts",
        "topics":    "topics",
        "plans":     "study_plans",
    }
    table = table_map.get(history_type)
    if table:
        conn.execute(f"DELETE FROM {table} WHERE user_id = ?", (user_id,))
        conn.commit()
    conn.close()


def show_delete_section(user_id: int):
    """Render the history delete panel inside sidebar."""
    st.markdown("---")
    st.markdown("### 🗑️ Delete History")

    options = {
        "📝 Notes":           "notes",
        "✨ Summaries":       "summaries",
        "❓ Questions":       "questions",
        "🎯 Quiz Results":    "quizzes",
        "🤔 Doubts":          "doubts",
        "📊 Topics":          "topics",
        "📅 Study Plans":     "plans",
    }

    selected_label = st.selectbox(
        "What to delete?",
        list(options.keys()),
        key="del_history_select"
    )
    selected_type = options[selected_label]

    # Confirm toggle
    confirm_key = f"confirm_del_{selected_type}"
    if confirm_key not in st.session_state:
        st.session_state[confirm_key] = False

    if not st.session_state[confirm_key]:
        if st.button(f"🗑️ Delete {selected_label}", use_container_width=True):
            st.session_state[confirm_key] = True
            st.rerun()
    else:
        st.markdown(
            f"<div class='delete-warning'>⚠️ <b>Are you sure?</b><br>"
            f"This will permanently delete all <b>{selected_label}</b> history.</div>",
            unsafe_allow_html=True
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, Delete", type="primary", use_container_width=True):
                delete_all_history(user_id, selected_type)
                st.session_state[confirm_key] = False
                st.success(f"✅ {selected_label} deleted!")
                st.rerun()
        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state[confirm_key] = False
                st.rerun()


# ── Dashboard function ────────────────────────────────────────────────────────
def show_dashboard(user):
    from utils.database import get_notes, get_summaries, get_quiz_history, get_topics, get_doubts
    import pandas as pd

    user_id = user["id"]
    username = user["username"]

    st.markdown(f"## 👋 Welcome back, **{username}**!")
    st.caption("Here's your study overview.")
    st.markdown("---")

    notes      = get_notes(user_id)
    summaries  = get_summaries(user_id)
    quiz_history = get_quiz_history(user_id)
    topics     = get_topics(user_id)
    doubts     = get_doubts(user_id)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("📝 Notes",     len(notes))
    col2.metric("✨ Summaries", len(summaries))
    col3.metric("🎯 Quizzes",   len(quiz_history))
    col4.metric("📊 Topics",    len(topics))
    col5.metric("❓ Doubts",    len(doubts))

    completed_topics = sum(1 for t in topics if t["status"] == "completed")
    if topics:
        pct = round((completed_topics / len(topics)) * 100)
        st.markdown(f"**📈 Topic Completion: {pct}%**")
        st.progress(pct / 100)

    st.markdown("---")
    st.markdown("### 🚀 Quick Actions")
    col_a, col_b, col_c, col_d = st.columns(4)

    cards = [
        ("📝", "Summarize Notes", "Upload PDF or paste text", "notes",   "#7c6af733"),
        ("🎯", "Take a Quiz",     "Test your knowledge",      "quiz",    "#f7a26a33"),
        ("📅", "Study Planner",   "Plan for your exam",       "planner", "#5ddba833"),
        ("🤔", "Ask a Doubt",     "AI explains instantly",    "doubts",  "#f8717133"),
    ]
    for col, (icon, title, desc, page, border) in zip([col_a, col_b, col_c, col_d], cards):
        with col:
            st.markdown(
                f"""<div style='background:#1a1e29; border:1px solid {border};
                border-radius:12px; padding:16px; text-align:center;'>
                <div style='font-size:2rem;'>{icon}</div>
                <div style='font-weight:700; margin:8px 0 4px;'>{title}</div>
                <div style='color:#888; font-size:12px;'>{desc}</div></div>""",
                unsafe_allow_html=True
            )
            if st.button("Open →", key=f"d_{page}", use_container_width=True):
                st.session_state.current_page = page
                st.rerun()

    if quiz_history:
        st.markdown("---")
        st.markdown("### 🎯 Recent Quiz Results")
        rows = [{
            "Date":    h["attempted_at"][:10],
            "Subject": h["subject"],
            "Score":   f"{h['score']}/{h['total']}",
            "Grade":   f"{round(h['score']/h['total']*100) if h['total'] else 0}%"
        } for h in quiz_history[:5]]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ── Sidebar Navigation ────────────────────────────────────────────────────────
user = st.session_state.user

with st.sidebar:
    st.markdown(
        "<h2 style='color:#7c6af7; margin:0 0 4px;'>📚 Study<span style='color:#f7a26a;'>AI</span></h2>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<div style='background:#1a1e29; border:1px solid #252a38; border-radius:8px;"
        f"padding:8px 12px; font-size:0.85rem; color:#888; margin-bottom:15px;'>"
        f"👤 {user['username']}</div>",
        unsafe_allow_html=True
    )

    PAGES = {
        "🏠 Dashboard":         "dashboard",
        "📝 Notes Summarizer":  "notes",
        "❓ Question Generator": "questions",
        "🤔 Doubt Solver":      "doubts",
        "📅 Study Planner":     "planner",
        "🎯 Quiz Mode":         "quiz",
        "📊 Progress Tracker":  "progress",
    }

    if "current_page" not in st.session_state:
        st.session_state.current_page = "dashboard"

    for label, page_id in PAGES.items():
        is_active = st.session_state.current_page == page_id
        if st.button(
            label,
            key=f"nav_{page_id}",
            use_container_width=True,
            type="primary" if is_active else "secondary"
        ):
            st.session_state.current_page = page_id
            st.rerun()

    # ── History Delete Section ────────────────────────────────────────────
    show_delete_section(user["id"])

    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.markdown(
        "<div style='text-align:center; color:#444; font-size:11px; margin-top:20px;'>"
        "Powered by Claude AI</div>",
        unsafe_allow_html=True
    )

# ── Page Router ───────────────────────────────────────────────────────────────
page = st.session_state.current_page

if page == "dashboard":
    show_dashboard(user)
elif page == "notes":
    show_notes_summarizer()
elif page == "questions":
    show_question_generator()
elif page == "doubts":
    show_doubt_solver()
elif page == "planner":
    show_study_planner()
elif page == "quiz":
    show_quiz_mode()
elif page == "progress":
    show_progress_tracker()