import streamlit as st
import os

def init_page(title, icon="🏀"):
    """Initialize Streamlit page safely (only once)."""
    if not getattr(st, "_page_configured", False):
        st.set_page_config(page_title=title, page_icon=icon, layout="wide")
        st._page_configured = True
    apply_theme()

def apply_theme():
    st.markdown("""
        <style>
        body { background-color: black; color: white; }
        .nav-link {
            text-decoration:none;
            color:white;
            border:2px solid #E50914;
            padding:8px 16px;
            border-radius:10px;
            background-color:#111;
            box-shadow:0px 0px 10px #E50914;
            font-weight:bold;
            transition:0.3s;
        }
        .nav-link:hover { background-color:#E50914; }
        .active-link {
            color:#00FFFF !important;
            border-color:#00FFFF !important;
            box-shadow:0px 0px 10px #00FFFF !important;
        }
        h1, h2, h3, h4 { color: #00FFFF; }
        </style>
    """, unsafe_allow_html=True)

def render_navbar(current):
    """Dynamic navbar that detects which pages exist."""
    pages = {
        "🏠 Home": "./Home.py",
        "🧠 Research": "pages/Research_and_Predictions.py",
        "📅 Upcoming": "pages/Upcoming_Projections.py",
        "🟢 Live": "pages/Live_Projections.py",
        "🏁 Completed": "pages/Completed_Projections.py",
        "⭐ Favorites": "pages/Favorite_Players.py",
    }

    cols = st.columns(len(pages))
    for i, (label, path) in enumerate(pages.items()):
        if not os.path.exists(path):
            continue
        is_active = current.lower() in label.lower()
        with cols[i]:
            st.page_link(path, label=label, use_container_width=True)
    st.markdown("---")
