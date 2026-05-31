"""
modules/question_generator.py
Generate MCQ, Short Answer, and Viva questions from notes
"""

import streamlit as st
import json
from utils.database import get_notes, save_questions, get_questions
from utils.ai_helper import generate_questions

SUBJECTS = [
    "General",
    # ── Core Sciences ──────────────────────────────────────────────────────
    "Mathematics", "Physics", "Chemistry", "Biology", "Science",
    # ── Computer Science ───────────────────────────────────────────────────
    "Computer Science",
    "Data Structures & Algorithms (DSA)",
    "Web Programming",
    "Computer Vision",
    "Blockchain",
    "Security & Risk Management",
    "Cyber Security Basics",
    # ── Data & Analytics ───────────────────────────────────────────────────
    "Introduction to Data Science",
    "Data Science with Python",
    "Data Analytics",
    "Big Data Analytics",
    "Power BI",
    # ── AI / ML / DL ───────────────────────────────────────────────────────
    "Artificial Intelligence",
    "Machine Learning",
    "Deep Learning",
    "Neural Networks",
    "Natural Language Processing",
    # ── Generative AI & LLMs ──────────────────────────────────────────────
    "Generative AI",
    "Generative AI Frameworks",
    "Transformers Architecture",
    "Prompt Engineering",
    "Retrieval-Augmented Generation (RAG)",
    "LangChain / LlamaIndex",
    "Agentic AI",
    "AI Agents",
    # ── IoT & DB ───────────────────────────────────────────────────────────
    "Internet of Things (IoT)",
    "Database Management System",
    # ── Research & Others ──────────────────────────────────────────────────
    "Research Methodology",
    # ── Humanities & Commerce ─────────────────────────────────────────────
    "History", "Geography", "English",
    "Economics", "Political Science",
    "Other",
]


def show_question_generator():
    user_id = st.session_state.user["id"]

    st.markdown("## ❓ Question Generator")
    st.caption("AI will generate exam-ready questions from your notes.")

    tab_gen, tab_saved = st.tabs(["🔧 Generate Questions", "📋 Saved Questions"])

    with tab_gen:
        notes = get_notes(user_id)

        col1, col2 = st.columns(2)
        with col1:
            input_method = st.radio("Notes Source", ["📝 Paste Text", "📂 From Saved Notes"], horizontal=True)
        with col2:
            subject = st.selectbox("Subject", SUBJECTS, key="qgen_subject")

        notes_text = ""
        if input_method == "📝 Paste Text":
            notes_text = st.text_area("Paste notes here", height=200, placeholder="Paste your notes...")
        else:
            if not notes:
                st.info("No saved notes found. Please add notes in the Summarizer first.")
            else:
                note_options = {f"{n['title']} ({n['subject']})": n for n in notes}
                selected = st.selectbox("Select Note", list(note_options.keys()))
                if selected:
                    notes_text = note_options[selected]["content"]
                    st.caption(f"📄 {len(notes_text)} characters loaded")

        st.markdown("---")
        col3, col4, col5 = st.columns(3)
        with col3:
            q_type = st.selectbox("Question Type", ["MCQ", "Short", "Viva"])
        with col4:
            q_count = st.slider("Number of Questions", 3, 15, 5)
        with col5:
            st.markdown("&nbsp;")
            gen_btn = st.button("🚀 Generate Questions", type="primary", use_container_width=True)

        if gen_btn:
            if not notes_text.strip():
                st.warning("Please provide notes text first.")
            else:
                with st.spinner(f"🤖 Generating {q_count} {q_type} questions..."):
                    questions = generate_questions(notes_text, q_type, q_count, subject)

                if not questions:
                    st.error("Could not generate questions. Try again.")
                    return

                save_questions(user_id, json.dumps(questions), q_type, subject)
                st.success(f"✅ {len(questions)} questions generated and saved!")

                _display_questions(questions, q_type)

    with tab_saved:
        saved = get_questions(user_id)
        if not saved:
            st.info("No questions saved yet. Generate some above!")
            return

        st.markdown(f"**{len(saved)} question sets saved**")

        for qset in saved:
            label = f"{qset['question_type']} | {qset['subject']} | {qset['created_at'][:10]}"
            with st.expander(f"📋 {label}"):
                try:
                    qs = json.loads(qset["question_data"])
                    _display_questions(qs, qset["question_type"])
                except Exception:
                    st.write(qset["question_data"])


def _display_questions(questions: list, q_type: str):
    """Render questions nicely based on type."""

    if q_type == "MCQ":
        for i, q in enumerate(questions, 1):
            st.markdown(f"**Q{i}.** {q.get('question', '')}")
            options = q.get("options", [])
            for opt in options:
                st.markdown(f"&nbsp;&nbsp;&nbsp;{opt}")
            with st.expander(f"Show Answer — Q{i}"):
                st.markdown(f"✅ **Correct Answer:** {q.get('answer', '')}")
                explanation = q.get("explanation", "")
                if explanation:
                    st.markdown(f"💡 {explanation}")
            st.markdown("---")

    elif q_type == "Short":
        for i, q in enumerate(questions, 1):
            marks = q.get("marks", 2)
            st.markdown(f"**Q{i}.** {q.get('question', '')} &nbsp; *[{marks} marks]*")
            with st.expander(f"Model Answer — Q{i}"):
                st.write(q.get("answer", ""))
            st.markdown("---")

    else:  # Viva
        for i, q in enumerate(questions, 1):
            st.markdown(f"**Q{i}.** {q.get('question', '')}")
            with st.expander(f"Expected Answer — Q{i}"):
                st.write(q.get("answer", ""))
                follow_up = q.get("follow_up", "")
                if follow_up:
                    st.markdown(f"🔄 **Follow-up:** {follow_up}")
            st.markdown("---")