"""
modules/notes_summarizer.py
Upload notes (PDF/TXT) and get AI summaries with key points
"""

import streamlit as st
import json
from utils.database import save_note, get_notes, save_summary, get_summaries, delete_note
from utils.ai_helper import summarize_notes, generate_flashcards
from utils.file_parser import extract_text_from_file

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


def show_notes_summarizer():
    user_id = st.session_state.user["id"]

    st.markdown("## 📝 Notes Summarizer")
    st.caption("Upload your notes or paste text — AI will create a smart summary with key points.")

    tab_new, tab_history = st.tabs(["➕ New Summary", "📚 Summary History"])

    # ── NEW SUMMARY ──────────────────────────────────────────────────────────
    with tab_new:
        col1, col2 = st.columns([2, 1])
        with col1:
            note_title = st.text_input("Note Title", placeholder="e.g. Chapter 3 - Photosynthesis")
        with col2:
            subject = st.selectbox("Subject", SUBJECTS)

        input_method = st.radio("Input Method", ["✍️ Type/Paste Text", "📁 Upload File (PDF/TXT)"], horizontal=True)

        notes_text = ""
        if input_method == "✍️ Type/Paste Text":
            notes_text = st.text_area(
                "Paste your notes here",
                placeholder="Paste your class notes, textbook content, or any study material...",
                height=280
            )
        else:
            uploaded = st.file_uploader("Upload PDF or TXT file", type=["pdf", "txt"])
            if uploaded:
                with st.spinner("Reading file..."):
                    notes_text = extract_text_from_file(uploaded)
                if notes_text:
                    st.success(f"✅ Extracted {len(notes_text)} characters from file")
                    with st.expander("Preview extracted text"):
                        st.text(notes_text[:1000] + ("..." if len(notes_text) > 1000 else ""))
                else:
                    st.error("Could not extract text from file.")

        col_a, col_b = st.columns(2)
        with col_a:
            summarize_btn = st.button("✨ Summarize with AI", type="primary", use_container_width=True)
        with col_b:
            flashcard_btn = st.button("🃏 Generate Flashcards", use_container_width=True)

        if summarize_btn:
            if not notes_text.strip():
                st.warning("Please enter or upload some notes first.")
            elif not note_title.strip():
                st.warning("Please enter a title for these notes.")
            else:
                with st.spinner("🤖 AI is reading your notes..."):
                    result = summarize_notes(notes_text, subject)

                note_id = save_note(user_id, note_title, notes_text, subject)
                save_summary(
                    user_id=user_id,
                    title=note_title,
                    summary_text=result.get("overview", ""),
                    key_points=json.dumps(result.get("key_points", [])),
                    note_id=note_id
                )

                st.markdown("---")
                difficulty_colors = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴", "Unknown": "⚪"}
                diff = result.get("difficulty", "Unknown")
                st.markdown(f"**Difficulty:** {difficulty_colors.get(diff, '⚪')} {diff}")

                st.markdown("### 📋 Overview")
                st.info(result.get("overview", "No overview generated."))

                st.markdown("### 🎯 Key Points")
                for i, point in enumerate(result.get("key_points", []), 1):
                    st.markdown(f"**{i}.** {point}")

                terms = result.get("important_terms", [])
                if terms:
                    st.markdown("### 📖 Important Terms")
                    cols = st.columns(2)
                    for i, term in enumerate(terms):
                        with cols[i % 2]:
                            st.markdown(f"• {term}")

                st.success("✅ Summary saved to history!")

        if flashcard_btn:
            if not notes_text.strip():
                st.warning("Please enter some notes first.")
            else:
                with st.spinner("🃏 Generating flashcards..."):
                    cards = generate_flashcards(notes_text)

                if cards:
                    st.markdown("### 🃏 Flashcards")
                    for i, card in enumerate(cards, 1):
                        with st.expander(f"Card {i}: {card.get('front', '')[:60]}"):
                            st.markdown(f"**Q:** {card.get('front', '')}")
                            st.markdown(f"**A:** {card.get('back', '')}")
                else:
                    st.error("Could not generate flashcards.")

    # ── HISTORY ──────────────────────────────────────────────────────────────
    with tab_history:
        summaries = get_summaries(user_id)
        notes = get_notes(user_id)

        if not summaries:
            st.info("No summaries yet. Create your first summary above!")
            return

        st.markdown(f"**{len(summaries)} summaries saved**")

        for s in summaries:
            with st.expander(f"📄 {s['title']} — {s['created_at'][:10]}"):
                st.markdown("**Overview:**")
                st.write(s["summary_text"])
                try:
                    kp = json.loads(s["key_points"]) if s["key_points"] else []
                    if kp:
                        st.markdown("**Key Points:**")
                        for point in kp:
                            st.markdown(f"• {point}")
                except Exception:
                    pass

        st.markdown("---")
        st.markdown("### 📁 My Notes")
        if notes:
            for n in notes:
                c1, c2, c3 = st.columns([3, 1, 1])
                with c1:
                    st.write(f"📄 **{n['title']}** — {n['subject']}")
                with c2:
                    st.caption(n["created_at"][:10])
                with c3:
                    if st.button("🗑️", key=f"del_note_{n['id']}", help="Delete note"):
                        delete_note(n["id"], user_id)
                        st.rerun()