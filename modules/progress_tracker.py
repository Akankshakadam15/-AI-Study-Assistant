"""
modules/progress_tracker.py
Track topics, completion status, confidence levels and view progress charts
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.database import (
    add_topic, get_topics, update_topic_status, delete_topic,
    get_quiz_history, get_summaries, get_doubts
)

SUBJECTS = [
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

STATUS_OPTIONS = ["pending", "in_progress", "completed", "needs_revision"]
STATUS_ICONS = {"pending": "⏳", "in_progress": "📖", "completed": "✅", "needs_revision": "🔄"}
STATUS_COLORS = {"pending": "#6b7280", "in_progress": "#7c6af7", "completed": "#5ddba8", "needs_revision": "#f7a26a"}


def show_progress_tracker():
    user_id = st.session_state.user["id"]

    st.markdown("## 📊 Progress Tracker")
    st.caption("Track your topics, confidence levels, and overall study progress.")

    tab_overview, tab_topics, tab_add = st.tabs(["📈 Overview", "📋 My Topics", "➕ Add Topics"])

    with tab_overview:
        _show_overview(user_id)

    with tab_topics:
        _show_topics(user_id)

    with tab_add:
        _show_add_topics(user_id)


def _show_overview(user_id):
    topics = get_topics(user_id)
    quiz_history = get_quiz_history(user_id)
    summaries = get_summaries(user_id)
    doubts = get_doubts(user_id, limit=100)

    total = len(topics)
    completed = sum(1 for t in topics if t["status"] == "completed")
    in_progress = sum(1 for t in topics if t["status"] == "in_progress")
    pending = sum(1 for t in topics if t["status"] == "pending")
    needs_revision = sum(1 for t in topics if t["status"] == "needs_revision")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("📚 Total Topics", total)
    col2.metric("✅ Completed", completed)
    col3.metric("📖 In Progress", in_progress)
    col4.metric("⏳ Pending", pending)
    col5.metric("🔄 Revision", needs_revision)

    if total > 0:
        pct = round((completed / total) * 100)
        st.markdown(f"**Overall Progress: {pct}%**")
        st.progress(pct / 100)
    else:
        st.info("No topics added yet. Go to 'Add Topics' tab to get started!")

    st.markdown("---")

    if topics:
        col_a, col_b = st.columns(2)

        with col_a:
            status_counts = {s: sum(1 for t in topics if t["status"] == s) for s in STATUS_OPTIONS}
            status_counts = {k: v for k, v in status_counts.items() if v > 0}
            if status_counts:
                fig = px.pie(
                    names=[f"{STATUS_ICONS[k]} {k.replace('_', ' ').title()}" for k in status_counts.keys()],
                    values=list(status_counts.values()),
                    title="Topics by Status",
                    color_discrete_sequence=["#6b7280", "#7c6af7", "#5ddba8", "#f7a26a"]
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#e8eaf0",
                    title_font_size=14
                )
                st.plotly_chart(fig, use_container_width=True)

        with col_b:
            subjects_data = {}
            for t in topics:
                sub = t["subject"]
                if sub not in subjects_data:
                    subjects_data[sub] = {"total": 0, "done": 0}
                subjects_data[sub]["total"] += 1
                if t["status"] == "completed":
                    subjects_data[sub]["done"] += 1

            if subjects_data:
                subs = list(subjects_data.keys())
                pcts = [round(subjects_data[s]["done"] / subjects_data[s]["total"] * 100) for s in subs]
                fig2 = px.bar(
                    x=pcts, y=subs, orientation="h",
                    title="Completion by Subject (%)",
                    color=pcts,
                    color_continuous_scale=["#f87171", "#f7a26a", "#5ddba8"],
                    range_color=[0, 100]
                )
                fig2.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#e8eaf0",
                    title_font_size=14,
                    showlegend=False,
                    coloraxis_showscale=False
                )
                st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.markdown("### 📋 Activity Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("📝 Notes Summarized", len(summaries))
    col2.metric("🎯 Quizzes Taken", len(quiz_history))
    col3.metric("❓ Doubts Solved", len(doubts))

    if quiz_history:
        st.markdown("### 📈 Quiz Performance")
        rows = [{"Date": h["attempted_at"][:10], "Score %": round(h["score"] / h["total"] * 100) if h["total"] else 0, "Subject": h["subject"]} for h in quiz_history]
        df = pd.DataFrame(rows)
        fig3 = px.line(df, x="Date", y="Score %", color="Subject", markers=True,
                       title="Quiz Scores Over Time")
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e8eaf0",
            yaxis_range=[0, 100]
        )
        st.plotly_chart(fig3, use_container_width=True)


def _show_topics(user_id):
    topics = get_topics(user_id)

    if not topics:
        st.info("No topics added yet. Go to 'Add Topics' tab.")
        return

    col1, col2 = st.columns(2)
    with col1:
        all_subjects = ["All"] + list(set(t["subject"] for t in topics))
        filter_sub = st.selectbox("Filter by subject", all_subjects)
    with col2:
        filter_status = st.selectbox("Filter by status", ["All"] + STATUS_OPTIONS)

    filtered = topics
    if filter_sub != "All":
        filtered = [t for t in filtered if t["subject"] == filter_sub]
    if filter_status != "All":
        filtered = [t for t in filtered if t["status"] == filter_status]

    st.markdown(f"**Showing {len(filtered)} topics**")

    for t in filtered:
        icon = STATUS_ICONS.get(t["status"], "⏳")
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

        with col1:
            st.markdown(f"{icon} **{t['topic_name']}** &nbsp; <span style='color:#888;font-size:12px;'>{t['subject']}</span>", unsafe_allow_html=True)
        with col2:
            new_status = st.selectbox(
                "Status",
                STATUS_OPTIONS,
                index=STATUS_OPTIONS.index(t["status"]),
                key=f"status_{t['id']}",
                label_visibility="collapsed"
            )
        with col3:
            confidence = st.slider(
                "Confidence",
                0, 100, t.get("confidence", 0),
                key=f"conf_{t['id']}",
                label_visibility="collapsed",
                help="Your confidence level (0-100%)"
            )
        with col4:
            if st.button("💾", key=f"save_{t['id']}", help="Save changes"):
                update_topic_status(t["id"], new_status, confidence)
                st.success("Saved!")
                st.rerun()

        col_del1, col_del2, col_del3 = st.columns([6, 1, 1])
        with col_del3:
            if st.button("🗑️", key=f"del_{t['id']}", help="Delete topic"):
                delete_topic(t["id"])
                st.rerun()

        st.divider()


def _show_add_topics(user_id):
    st.markdown("### ➕ Add Topics to Track")

    col1, col2 = st.columns(2)
    with col1:
        subject = st.selectbox("Subject", SUBJECTS, key="add_subject")
    with col2:
        topic_name = st.text_input("Topic Name", placeholder="e.g. Transformer Architecture", key="add_topic")

    if st.button("➕ Add Topic", type="primary"):
        if not topic_name.strip():
            st.warning("Please enter a topic name.")
        else:
            add_topic(user_id, subject, topic_name.strip())
            st.success(f"✅ '{topic_name}' added to {subject}!")
            st.rerun()

    st.markdown("---")
    st.markdown("### 📦 Bulk Add Topics")
    st.caption("Add multiple topics at once — one per line")

    bulk_subject = st.selectbox("Subject for bulk add", SUBJECTS, key="bulk_subject")
    bulk_topics = st.text_area(
        "Topics (one per line)",
        placeholder="Introduction to LLMs\nPrompt Engineering\nRAG Pipeline\nFine-tuning",
        height=150,
        key="bulk_topics"
    )

    if st.button("📦 Add All Topics", use_container_width=True):
        lines = [l.strip() for l in bulk_topics.strip().splitlines() if l.strip()]
        if not lines:
            st.warning("Please enter at least one topic.")
        else:
            for topic in lines:
                add_topic(user_id, bulk_subject, topic)
            st.success(f"✅ Added {len(lines)} topics to {bulk_subject}!")
            st.rerun()