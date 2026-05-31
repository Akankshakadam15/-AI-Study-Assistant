"""
modules/study_planner.py
AI-generated study timetable based on exam date and subjects
"""

import streamlit as st
import json
import pandas as pd
from datetime import date, datetime
from utils.database import save_study_plan, get_study_plans
from utils.ai_helper import generate_study_plan

ALL_SUBJECTS = [
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


def show_study_planner():
    user_id = st.session_state.user["id"]

    st.markdown("## 📅 AI Study Planner")
    st.caption("Enter your exam details — AI will create a personalized day-by-day timetable.")

    tab_new, tab_saved = st.tabs(["➕ Create Plan", "📋 Saved Plans"])

    with tab_new:
        col1, col2 = st.columns(2)
        with col1:
            exam_name = st.text_input("Exam Name", placeholder="e.g. ML Unit Test, Final Semester Exam")
            exam_date = st.date_input("Exam Date", min_value=date.today())

        with col2:
            hours_per_day = st.slider("Study hours per day", 2, 12, 6)
            subjects = st.multiselect("Subjects to cover", ALL_SUBJECTS,
                                      default=["Machine Learning", "Deep Learning"])

        weak_subjects = st.multiselect("Weak subjects (will get more time)", subjects)

        days_left = (exam_date - date.today()).days
        if days_left >= 0:
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Days Left", days_left)
            col_b.metric("Study Hours/Day", hours_per_day)
            col_c.metric("Subjects", len(subjects))

        st.markdown("---")
        plan_btn = st.button("🚀 Generate Study Plan", type="primary", use_container_width=True)

        if plan_btn:
            if not exam_name.strip():
                st.warning("Please enter exam name.")
            elif not subjects:
                st.warning("Please select at least one subject.")
            elif days_left < 1:
                st.warning("Exam date must be in the future.")
            else:
                with st.spinner("🤖 AI is creating your personalized study plan..."):
                    result = generate_study_plan(
                        exam_name=exam_name,
                        exam_date=exam_date.strftime("%d-%m-%Y"),
                        subjects=subjects,
                        hours_per_day=hours_per_day,
                        weak_subjects=weak_subjects
                    )

                save_study_plan(
                    user_id=user_id,
                    exam_name=exam_name,
                    exam_date=str(exam_date),
                    subjects=", ".join(subjects),
                    plan_data=json.dumps(result)
                )

                _display_plan(result, exam_name)
                st.success("✅ Plan saved!")

    with tab_saved:
        plans = get_study_plans(user_id)
        if not plans:
            st.info("No study plans created yet. Create one above!")
            return

        st.markdown(f"**{len(plans)} plans saved**")
        for p in plans:
            label = f"📅 {p['exam_name']} — Exam: {p['exam_date']} | Subjects: {p['subjects']}"
            with st.expander(label):
                try:
                    data = json.loads(p["plan_data"])
                    _display_plan(data, p["exam_name"])
                except Exception:
                    st.write(p["plan_data"])


def _display_plan(result: dict, exam_name: str):
    plan = result.get("plan", [])
    tips = result.get("tips", [])
    targets = result.get("weekly_targets", {})

    st.markdown(f"### 📆 Study Plan: {exam_name}")

    if tips:
        with st.expander("💡 AI Study Tips"):
            for t in tips:
                st.markdown(f"• {t}")

    if targets:
        st.markdown("**📊 Weekly Targets**")
        cols = st.columns(min(len(targets), 4))
        for i, (sub, target) in enumerate(targets.items()):
            with cols[i % len(cols)]:
                st.info(f"**{sub}**\n{target}")

    if plan:
        st.markdown("**📅 Day-by-Day Schedule**")
        for day_data in plan:
            day_num = day_data.get("day", "")
            day_date = day_data.get("date", "")
            schedule = day_data.get("schedule", [])

            with st.expander(f"Day {day_num} — {day_date}", expanded=(day_num == 1)):
                if schedule:
                    rows = []
                    for slot in schedule:
                        rows.append({
                            "Time": slot.get("time", ""),
                            "Subject": slot.get("subject", ""),
                            "Topic": slot.get("topic", ""),
                            "Type": slot.get("type", "Study")
                        })
                    df = pd.DataFrame(rows)
                    st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("Plan data is empty. Please try generating again.")