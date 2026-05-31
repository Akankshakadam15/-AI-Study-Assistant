"""
modules/auth.py
User Login and Registration page
"""

import streamlit as st
from utils.database import create_user, verify_user


def show_auth_page():
    """Display login/register UI. Sets st.session_state.user on success."""

    st.markdown("""
    <div style='text-align:center; padding: 20px 0 10px;'>
        <h1 style='font-size:2.8rem; color:#7c6af7;'>📚 StudyAI</h1>
        <p style='color:#888; font-size:1.05rem;'>AI-Powered Study Assistant for Students</p>
    </div>
    """, unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["🔐 Login", "✨ Register"])

    with tab_login:
        st.markdown("### Welcome back!")
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Login →", use_container_width=True, type="primary")

        if submitted:
            if not username or not password:
                st.error("Please fill in all fields.")
            else:
                ok, user = verify_user(username, password)
                if ok:
                    st.session_state.user = user
                    st.session_state.logged_in = True
                    st.success(f"Welcome back, {username}! 🎉")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    with tab_register:
        st.markdown("### Create your account")
        with st.form("register_form"):
            new_username = st.text_input("Username", placeholder="Choose a username", key="reg_user")
            new_email = st.text_input("Email (optional)", placeholder="your@email.com", key="reg_email")
            new_password = st.text_input("Password", type="password", placeholder="Choose a password", key="reg_pass")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Repeat password", key="reg_conf")
            reg_submitted = st.form_submit_button("Create Account →", use_container_width=True, type="primary")

        if reg_submitted:
            if not new_username or not new_password:
                st.error("Username and password are required.")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                ok, msg = create_user(new_username, new_password, new_email)
                if ok:
                    st.success(msg + " Please login now.")
                else:
                    st.error(msg)
