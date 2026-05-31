"""
modules/quiz_mode.py
Interactive quiz with scoring, timer and results
"""

import streamlit as st
import time
from utils.database import save_quiz_result, get_quiz_history
from utils.ai_helper import generate_quiz

TOPICS = {
    # ── Core Sciences ──────────────────────────────────────────────────────
    "Mathematics": ["Algebra", "Geometry", "Trigonometry", "Statistics", "Calculus", "Number Theory"],
    "Science": ["Physics Basics", "Chemistry Basics", "Biology Basics", "Earth Science"],
    "Physics": ["Motion", "Force & Laws", "Energy & Work", "Waves & Sound", "Electricity", "Magnetism", "Optics"],
    "Chemistry": ["Atoms & Molecules", "Periodic Table", "Chemical Reactions", "Acids & Bases", "Organic Chemistry"],
    "Biology": ["Cell Biology", "Genetics", "Evolution", "Human Body", "Ecology", "Photosynthesis"],

    # ── Computer Science ───────────────────────────────────────────────────
    "Computer Science": ["Data Structures", "Algorithms", "OOP Concepts", "OS Basics", "Networking", "Software Engineering"],
    "Data Structures & Algorithms (DSA)": [
        "Arrays & Strings", "Linked Lists", "Stacks & Queues",
        "Trees & Graphs", "Sorting Algorithms", "Searching Algorithms",
        "Dynamic Programming", "Recursion", "Hashing",
    ],
    "Web Programming": [
        "HTML & CSS Basics", "JavaScript Fundamentals", "React Basics",
        "REST APIs", "Node.js", "Databases in Web", "HTTP & Web Protocols",
    ],
    "Blockchain": [
        "Blockchain Basics", "Cryptography in Blockchain", "Smart Contracts",
        "Ethereum & Solidity", "DeFi & NFTs", "Consensus Mechanisms",
    ],
    "Cyber Security Basics": [
        "Network Security", "Encryption & Decryption", "Phishing & Social Engineering",
        "Firewalls & IDS", "Vulnerability Assessment", "Ethical Hacking Basics",
    ],
    "Security & Risk Management": [
        "Risk Assessment", "CIA Triad", "ISO 27001", "Incident Response",
        "Business Continuity", "Compliance & Governance",
    ],

    # ── Data & Analytics ───────────────────────────────────────────────────
    "Introduction to Data Science": [
        "What is Data Science", "Data Science Lifecycle", "Types of Data",
        "Statistics for Data Science", "Data Cleaning", "EDA (Exploratory Data Analysis)",
    ],
    "Data Science with Python": [
        "NumPy Basics", "Pandas DataFrames", "Matplotlib & Seaborn",
        "Scikit-learn Intro", "Data Preprocessing", "Model Building in Python",
    ],
    "Data Analytics": [
        "Descriptive Analytics", "Predictive Analytics", "Data Visualization",
        "Excel for Analytics", "SQL for Analytics", "Business Intelligence",
    ],
    "Big Data Analytics": [
        "Introduction to Big Data", "Hadoop & HDFS", "MapReduce",
        "Apache Spark", "Kafka & Streaming", "Data Warehousing",
        "Hive & Pig", "NoSQL Databases", "ETL Pipelines",
    ],
    "Power BI": [
        "Power BI Interface", "Connecting Data Sources", "DAX Basics",
        "Creating Dashboards", "Charts & Visuals", "Power Query",
        "Publishing & Sharing Reports",
    ],

    # ── AI / ML / DL ───────────────────────────────────────────────────────
    "Artificial Intelligence": [
        "Introduction to AI", "Search Algorithms (BFS, DFS, A*)",
        "Knowledge Representation", "Expert Systems",
        "Planning & Problem Solving", "AI Ethics",
    ],
    "Machine Learning": [
        "Supervised Learning", "Unsupervised Learning", "Reinforcement Learning",
        "Linear & Logistic Regression", "Decision Trees & Random Forest",
        "SVM", "K-Means Clustering", "Model Evaluation & Metrics",
        "Feature Engineering", "Overfitting & Regularization", "Cross Validation",
    ],
    "Deep Learning": [
        "Neural Networks Basics", "Activation Functions", "Backpropagation",
        "CNN (Convolutional Neural Networks)", "RNN & LSTM",
        "Transfer Learning", "Autoencoders", "GANs", "Optimizers (Adam, SGD)",
        "Batch Normalization", "Dropout",
    ],
    "Neural Networks": [
        "Perceptron & MLP", "Feedforward Networks", "Backpropagation",
        "Vanishing Gradient Problem", "Weight Initialization",
        "Hyperparameter Tuning", "Loss Functions",
    ],
    "Computer Vision": [
        "Image Processing Basics", "CNN for Image Classification",
        "Object Detection (YOLO, SSD)", "Image Segmentation",
        "Face Recognition", "OpenCV Basics", "Transfer Learning in CV",
    ],
    "Natural Language Processing": [
        "Tokenization & Text Preprocessing", "Bag of Words & TF-IDF",
        "Word Embeddings (Word2Vec, GloVe)", "Sentiment Analysis",
        "Named Entity Recognition", "Text Classification",
        "Seq2Seq Models", "Attention Mechanism", "BERT & GPT Basics",
    ],

    # ── Generative AI & LLMs ──────────────────────────────────────────────
    "Generative AI": [
        "Introduction to GenAI", "Large Language Models (LLMs)",
        "Diffusion Models", "GANs vs Diffusion", "GPT Architecture",
        "Fine-tuning LLMs", "AI Ethics in GenAI", "Multimodal AI",
    ],
    "Generative AI Frameworks": [
        "LangChain Basics", "LlamaIndex", "Hugging Face Transformers",
        "OpenAI API Usage", "Streamlit + AI Apps", "Vector Databases",
    ],
    "Transformers Architecture": [
        "Attention Mechanism", "Self-Attention & Multi-Head Attention",
        "Positional Encoding", "Encoder-Decoder Architecture",
        "BERT Architecture", "GPT Architecture", "Vision Transformers (ViT)",
        "T5 & BART", "Scaling Laws",
    ],
    "Prompt Engineering": [
        "What is Prompt Engineering", "Zero-Shot Prompting",
        "Few-Shot Prompting", "Chain-of-Thought (CoT)",
        "ReAct Prompting", "Prompt Templates",
        "System Prompts", "Prompt Injection & Safety",
    ],
    "Retrieval-Augmented Generation (RAG)": [
        "What is RAG", "RAG Architecture", "Document Chunking",
        "Embedding Models", "Vector Stores (FAISS, Pinecone, Chroma)",
        "Retrieval Strategies", "RAG Evaluation", "Advanced RAG Techniques",
    ],
    "LangChain / LlamaIndex": [
        "LangChain Chains & Agents", "LangChain Memory",
        "LangChain Tools & Toolkits", "LlamaIndex Data Connectors",
        "LlamaIndex Query Engines", "Building RAG with LangChain",
        "Building RAG with LlamaIndex",
    ],
    "Agentic AI": [
        "What are AI Agents", "ReAct Framework", "Tool Use in Agents",
        "Multi-Agent Systems", "Agent Memory & Planning",
        "LangGraph", "AutoGen Basics", "Agent Evaluation",
    ],
    "AI Agents": [
        "Agent Architecture", "Planning & Reasoning", "Tool Calling",
        "Function Calling (OpenAI)", "Autonomous Agents",
        "Human-in-the-Loop", "Agent Safety",
    ],

    # ── IoT & DB ───────────────────────────────────────────────────────────
    "Internet of Things (IoT)": [
        "IoT Architecture & Layers", "Sensors & Actuators",
        "Communication Protocols (MQTT, HTTP, CoAP)",
        "Arduino & Raspberry Pi", "IoT Security",
        "Edge Computing", "Smart Home Applications",
        "IoT with Cloud (AWS, Azure)", "Real-time Data Processing",
    ],
    "Database Management System": [
        "ER Diagrams & Data Modeling", "Relational Model & Keys",
        "SQL Basics (DDL, DML, DCL)", "Joins & Subqueries",
        "Normalization (1NF-BCNF)", "Transactions & ACID",
        "Indexing & Query Optimization", "NoSQL vs SQL",
        "Stored Procedures & Triggers", "Concurrency Control",
    ],

    # ── Research ───────────────────────────────────────────────────────────
    "Research Methodology": [
        "Types of Research", "Research Design", "Literature Review",
        "Hypothesis Formulation", "Data Collection Methods",
        "Qualitative vs Quantitative", "Research Ethics",
        "Writing a Research Paper", "Citation & References",
    ],

    # ── Humanities ─────────────────────────────────────────────────────────
    "History": ["Ancient History", "Medieval Period", "Modern History", "World Wars", "Indian History"],
    "English": ["Grammar", "Vocabulary", "Literature", "Writing Skills"],
    "Economics": ["Microeconomics", "Macroeconomics", "Supply & Demand", "GDP & Growth"],
    "General Knowledge": ["Science & Tech", "Current Affairs", "Geography", "Sports"],
}

DIFFICULTY_COLORS = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}


def show_quiz_mode():
    user_id = st.session_state.user["id"]

    st.markdown("## 🎯 Quiz Mode")
    st.caption("Test your knowledge with AI-generated quizzes. Get instant results!")

    tab_quiz, tab_history = st.tabs(["🎮 Take Quiz", "📊 Quiz History"])

    with tab_quiz:
        if "quiz_questions" not in st.session_state or not st.session_state.get("quiz_active"):
            _show_quiz_setup(user_id)
        else:
            _run_quiz(user_id)

    with tab_history:
        _show_quiz_history(user_id)


def _show_quiz_setup(user_id):
    st.markdown("### Choose Your Quiz")

    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox("Category", list(TOPICS.keys()))

        # ── Topic: Dropdown + Custom Input ───────────────────────────────
        topic_mode = st.radio(
            "Topic Selection",
            ["📋 Choose from list", "✏️ Type my own topic"],
            horizontal=True,
            key="topic_mode"
        )

        if topic_mode == "📋 Choose from list":
            topic = st.selectbox("Topic", TOPICS[category], key="topic_select")
        else:
            topic = st.text_input(
                "Enter your own topic",
                placeholder="e.g. Transformer Architecture, RAG Pipeline, Sorting Algorithms...",
                key="topic_custom"
            )
            if topic.strip():
                st.success(f"✅ Custom topic: **{topic}**")
            else:
                st.info("💡 Type any topic — AI will generate questions on it!")

    with col2:
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
        q_count = st.slider("Number of Questions", 5, 20, 10)

    st.markdown("---")

    # Final topic to use
    final_topic = topic.strip() if topic_mode == "✏️ Type my own topic" else topic

    if st.button("🚀 Start Quiz!", type="primary", use_container_width=True):
        if not final_topic:
            st.warning("⚠️ Please enter a topic name first.")
            return

        with st.spinner(f"🤖 Generating {q_count} {difficulty} questions on **{final_topic}**..."):
            questions = generate_quiz(final_topic, difficulty, q_count)

        if not questions:
            st.error("Could not generate quiz. Please try again.")
            return

        st.session_state.quiz_questions = questions
        st.session_state.quiz_topic = final_topic
        st.session_state.quiz_subject = category
        st.session_state.quiz_difficulty = difficulty
        st.session_state.quiz_answers = {}
        st.session_state.quiz_active = True
        st.session_state.quiz_submitted = False
        st.session_state.quiz_start_time = time.time()
        st.rerun()


def _run_quiz(user_id):
    questions = st.session_state.quiz_questions
    topic = st.session_state.quiz_topic
    difficulty = st.session_state.quiz_difficulty
    submitted = st.session_state.get("quiz_submitted", False)

    elapsed = int(time.time() - st.session_state.get("quiz_start_time", time.time()))
    mins, secs = divmod(elapsed, 60)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Topic", topic[:20])
    col2.metric("Questions", len(questions))
    col3.metric("Difficulty", f"{DIFFICULTY_COLORS.get(difficulty, '')} {difficulty}")
    col4.metric("⏱️ Time", f"{mins:02d}:{secs:02d}")

    st.markdown("---")

    if not submitted:
        answers = {}
        for i, q in enumerate(questions):
            st.markdown(f"**Q{i+1}.** {q.get('question', '')}")
            opts = q.get("options", [])
            opt_letters = [o.split(")")[0].strip() if ")" in o else o[0] for o in opts]

            selected = st.radio(
                f"Select answer for Q{i+1}",
                opts,
                key=f"q_{i}",
                label_visibility="collapsed"
            )
            if selected:
                answers[i] = opt_letters[opts.index(selected)] if selected in opts else selected[0]
            st.markdown("---")

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("✅ Submit Quiz", type="primary", use_container_width=True):
                st.session_state.quiz_answers = answers
                st.session_state.quiz_submitted = True
                st.rerun()
        with col_b:
            if st.button("❌ Cancel Quiz", use_container_width=True):
                _reset_quiz()
                st.rerun()

    else:
        answers = st.session_state.quiz_answers
        score = sum(
            1 for i, q in enumerate(questions)
            if str(answers.get(i, "")).upper() == str(q.get("answer", "")).upper()
        )
        total = len(questions)
        pct = round((score / total) * 100) if total > 0 else 0

        if not st.session_state.get("quiz_result_saved"):
            save_quiz_result(user_id, st.session_state.quiz_subject, score, total)
            st.session_state.quiz_result_saved = True

        if pct >= 80:
            st.balloons()
            grade_msg = "🏆 Excellent!"
            grade_color = "#5ddba8"
        elif pct >= 60:
            grade_msg = "👍 Good job!"
            grade_color = "#7c6af7"
        elif pct >= 40:
            grade_msg = "📚 Keep practicing!"
            grade_color = "#f7a26a"
        else:
            grade_msg = "💪 More revision needed"
            grade_color = "#f87171"

        st.markdown(
            f"""<div style='text-align:center; padding:20px; background:#1e1e2e;
            border-radius:12px; border:2px solid {grade_color};'>
            <h2 style='color:{grade_color};'>{grade_msg}</h2>
            <h1 style='font-size:3rem; color:{grade_color};'>{score}/{total}</h1>
            <p style='color:#aaa;'>Score: {pct}%</p>
            </div>""",
            unsafe_allow_html=True
        )

        st.markdown("---")
        st.markdown("### 📝 Review Answers")
        for i, q in enumerate(questions):
            correct = str(q.get("answer", "")).upper()
            user_ans = str(answers.get(i, "")).upper()
            is_correct = user_ans == correct
            icon = "✅" if is_correct else "❌"

            with st.expander(f"{icon} Q{i+1}: {q.get('question', '')[:70]}..."):
                for opt in q.get("options", []):
                    letter = opt.split(")")[0].strip() if ")" in opt else opt[0]
                    if letter == correct:
                        st.markdown(f"✅ **{opt}** ← Correct Answer")
                    elif letter == user_ans and not is_correct:
                        st.markdown(f"❌ ~~{opt}~~ ← Your Answer")
                    else:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;{opt}")

                explanation = q.get("explanation", "")
                if explanation:
                    st.info(f"💡 {explanation}")

        if st.button("🔄 Take Another Quiz", type="primary", use_container_width=True):
            _reset_quiz()
            st.rerun()


def _reset_quiz():
    for key in ["quiz_questions", "quiz_topic", "quiz_subject", "quiz_difficulty",
                "quiz_answers", "quiz_active", "quiz_submitted",
                "quiz_start_time", "quiz_result_saved"]:
        if key in st.session_state:
            del st.session_state[key]


def _show_quiz_history(user_id):
    history = get_quiz_history(user_id)
    if not history:
        st.info("No quiz attempts yet. Take your first quiz!")
        return

    st.markdown(f"**{len(history)} quiz attempts**")

    total_quizzes = len(history)
    avg_score = sum(h["score"] / h["total"] * 100 for h in history if h["total"] > 0) / total_quizzes

    col1, col2 = st.columns(2)
    col1.metric("Total Quizzes", total_quizzes)
    col2.metric("Average Score", f"{avg_score:.1f}%")

    import pandas as pd
    rows = []
    for h in history:
        pct = round(h["score"] / h["total"] * 100) if h["total"] > 0 else 0
        rows.append({
            "Date": h["attempted_at"][:10],
            "Subject": h["subject"],
            "Score": f"{h['score']}/{h['total']}",
            "Percentage": f"{pct}%",
            "Grade": "🏆 Excellent" if pct >= 80 else "👍 Good" if pct >= 60 else "📚 Average" if pct >= 40 else "💪 Needs Work"
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)