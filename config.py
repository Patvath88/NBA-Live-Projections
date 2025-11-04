import streamlit as st
import os

# ==========================
#  PAGE INITIALIZATION
# ==========================
def init_page(title, icon="🏀"):
    """Initialize Streamlit page safely (only once per page)."""
    if not getattr(st, "_page_configured", False):
        st.set_page_config(page_title=title, page_icon=icon, layout="wide")
        st._page_configured = True
    apply_theme()

# ==========================
#  THEME & STYLING
# ==========================
def apply_theme():
    """Apply dark futuristic UI theme."""
    st.markdown("""
        <style>
        body {
            background-color: #000000;
            color: #FFFFFF;
        }
        .nav-link {
            text-decoration: none;
            color: white;
            border: 2px solid #E50914;
            padding: 8px 16px;
            border-radius: 10px;
            background-color: #111;
            box-shadow: 0px 0px 10px #E50914;
            font-weight: bold;
            transition: 0.3s;
        }
        .nav-link:hover {
            background-color: #E50914;
        }
        .active-link {
            color: #00FFFF !important;
            border-color: #00FFFF !important;
            box-shadow: 0px 0px 10px #00FFFF !important;
        }
        h1, h2, h3, h4 {
            color: #00FFFF;
        }
        </style>
    """, unsafe_allow_html=True)

# ==========================
#  NAVIGATION BAR
# ==========================
def render_navbar(current: str):
    """
    Futuristic top navigation bar using Streamlit's page_link system.
    Automatically detects missing pages and shows clean links.
    """
    pages = {
        "🏠 Home": "Home",
        "🧠 Research": "pages/Research_and_Projections",
        "📅 Upcoming": "pages/Upcoming_Projections",
        "🟢 Live": "pages/Live_Projections",
        "🏁 Completed": "pages/Completed_Projections",
        "⭐ Favorites": "pages/Favorite_Players",
    }

    cols = st.columns(len(pages))
    for i, (label, route) in enumerate(pages.items()):
        is_active = current.lower() in label.lower()
        with cols[i]:
            try:
                # No `.py` extension — Streamlit handles this internally
                st.page_link(route, label=label, use_container_width=True)
            except Exception as e:
                # If a page is missing, show a warning so we can catch it
                st.markdown(
                    f"<div style='color:red;font-size:12px;'>⚠️ Missing: {route}.py</div>",
                    unsafe_allow_html=True
                )

    st.markdown("---")
