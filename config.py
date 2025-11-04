import streamlit as st

def init_page(title, icon="🏀"):
    st.set_page_config(page_title=title, page_icon=icon, layout="wide")
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
    pages = {
        "🏠 Home": "Home",
        "🧠 Research": "Research_and_Predictions",
        "📅 Upcoming": "Upcoming_Projections",
        "🟢 Live": "Live_Projections",
        "🏁 Completed": "Completed_Projections",
        "⭐ Favorites": "Favorite_Players",
    }
    cols = st.columns(len(pages))
    for i, (label, page) in enumerate(pages.items()):
        cls = "active-link" if page == current else "nav-link"
        with cols[i]:
            st.page_link(f"pages/{page}.py", label=label, use_container_width=True)
    st.markdown("---")
