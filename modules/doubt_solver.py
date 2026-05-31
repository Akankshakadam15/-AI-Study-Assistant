"""
modules/doubt_solver.py
AI-powered doubt solver — students can ask any question and get clear explanations
"""

import streamlit as st
from utils.database import save_doubt, get_doubts
from utils.ai_helper import solve_doubt

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
    "Computer Vision",
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
    # ── IoT & Emerging Tech ────────────────────────────────────────────────
    "Internet of Things (IoT)",
    "Database Management System",
    # ── Research & Others ──────────────────────────────────────────────────
    "Research Methodology",
    # ── Humanities & Commerce ─────────────────────────────────────────────
    "History", "Geography", "English",
    "Economics", "Political Science",
    "Other",
]


def show_doubt_solver():
    user_id = st.session_state.user["id"]

    st.markdown("## 🤔 AI Doubt Solver")
    st.caption("Ask any study question — AI will explain it clearly with examples.")

    tab_ask, tab_history = st.tabs(["💬 Ask a Doubt", "📜 Doubt History"])

    with tab_ask:
        col1, col2 = st.columns([3, 1])
        with col1:
            question = st.text_area(
                "What's your doubt?",
                placeholder="e.g. What is the difference between mitosis and meiosis?\nOr: How does Newton's second law work?\nOr: Explain recursion with an example",
                height=130
            )
        with col2:
            subject = st.selectbox("Subject", SUBJECTS)
            st.markdown("&nbsp;")
            use_context = st.checkbox("Use my notes as context")

        context_text = ""
        if use_context:
            from utils.database import get_notes
            notes = get_notes(user_id)
            if notes:
                note_options = {n["title"]: n["content"] for n in notes}
                selected_note = st.selectbox("Select relevant note", list(note_options.keys()))
                context_text = note_options.get(selected_note, "")[:800]
            else:
                st.info("No notes saved. Add notes in the Summarizer first.")

        ask_btn = st.button("🧠 Solve My Doubt", type="primary", use_container_width=True)

        if ask_btn:
            if not question.strip():
                st.warning("Please type your doubt first.")
            else:
                with st.spinner("🤖 AI is thinking..."):
                    answer = solve_doubt(question, subject, context_text)

                save_doubt(user_id, question, answer, subject)

                st.markdown("---")
                st.markdown("### 💡 AI Explanation")

                st.markdown(
                    f"""<div style='background:#1e1e2e; border-left:4px solid #7c6af7;
                    padding:16px 20px; border-radius:8px; line-height:1.7;'>
                    {answer.replace(chr(10), '<br>')}
                    </div>""",
                    unsafe_allow_html=True
                )

                st.success("✅ Saved to your doubt history!")

                st.markdown("---")
                st.markdown("**Ask a follow-up:**")
                follow_up = st.text_input("Follow-up question", key="follow_up_q")
                if st.button("Ask Follow-up", key="follow_up_btn"):
                    with st.spinner("Thinking..."):
                        fu_answer = solve_doubt(follow_up, subject, answer[:500])
                    st.info(fu_answer)

    with tab_history:
        doubts = get_doubts(user_id, limit=30)
        if not doubts:
            st.info("No doubts asked yet. Ask your first question above!")
            return

        st.markdown(f"**{len(doubts)} doubts solved**")

        all_subjects = list(set(d["subject"] for d in doubts))
        filter_sub = st.selectbox("Filter by subject", ["All"] + all_subjects)

        filtered = doubts if filter_sub == "All" else [d for d in doubts if d["subject"] == filter_sub]

        for d in filtered:
            with st.expander(f"❓ {d['question'][:80]}... | {d['subject']} | {d['asked_at'][:10]}"):
                st.markdown("**Your question:**")
                st.write(d["question"])
                st.markdown("**AI Answer:**")
                st.write(d["answer"])