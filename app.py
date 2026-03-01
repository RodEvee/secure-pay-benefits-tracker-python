import streamlit as st
import os

from database.db_manager import init_db
from components.auth import render_auth
from components.dashboard import render_dashboard
from components.history import render_history
from components.settings import render_settings

st.set_page_config(page_title="Secure Pay & Benefits Tracker", layout="wide", page_icon="💼")

# Initialize Database
init_db()

# Custom CSS for better UI (similar to React's Tailwind structure)
st.markdown("""
    <style>
        .stButton>button { border-radius: 8px; font-weight: bold; }
        .metric-card { background-color: #f8fafc; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; }
        h1, h2, h3 { color: #1e293b; }
    </style>
""", unsafe_allow_html=True)

# Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def on_auth_success():
    st.session_state.authenticated = True
    st.rerun()

if not st.session_state.authenticated:
    render_auth(on_auth_success)
else:
    # Top Navigation / Sidebar
    st.sidebar.title("Secure Pay 💼")
    page = st.sidebar.radio("Navigation", ["Dashboard", "History", "Settings"])
    
    st.sidebar.markdown("---")
    st.sidebar.caption("🔒 End-to-End Encrypted")
    
    if st.sidebar.button("Log Out"):
        st.session_state.authenticated = False
        st.session_state.auth_step = 'BIO'
        st.rerun()

    if page == "Dashboard":
        render_dashboard()
    elif page == "History":
        render_history()
    elif page == "Settings":
        render_settings()
