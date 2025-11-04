import streamlit as st

def init_page(title: str, icon: str = "🏀", layout: str = "wide"):
    """
    Sets page configuration and applies global theme.
    Must be called as the first Streamlit command on each page.
    """
    st.set_page_config(page_title=title, page_icon=icon, layout=layout)
    apply_theme()
    return

def apply_theme():
    """Inject global dark neon style."""
    st.markdown("""
    <style>
    body { background-color: black; color: white; }
    a.nav-link {
        text-decoration:none;
        color:white;
        display:block;
        text-align:center;
        border:2px solid #E50914;
        padding:8px;
        border-radius:10px;
        background-color:#111;
        box-shadow:0px 0px 10px #E50914;
        font-weight:bold;
    }
    a.nav-link:hover {
        background-color:#E50914;
    }
    .card {
        border:2px solid #E50914;
        border-radius:10px;
        background-color:#111;
        padding:12px;
        text-align:center;
        color:#00FFFF;
        box-shadow:0px 0px 10px #E50914;
    }
    h1, h2, h3, h4 { color: #00FFFF; }
    </style>
    """, unsafe_allow_html=True)

def render_navbar():
    """Draws the global navigation bar with consistent styling."""
    col1, col2, col3, col4, col5 = st.columns(5)
    pages = {
        "🧠 Research": "Research_and_Predictions",
        "📅 Upcoming": "Upcoming_Projections",
        "🟢 Live": "Live_Projections",
        "🏁 Completed": "Completed_Projections",
        "⭐ Favorites": "Favorite_Players"
    }
    for i, (label, page) in enumerate(pages.items()):
        with [col1, col2, col3, col4, col5][i]:
            st.markdown(
                f"<a class='nav-link' href='/pages/{page}' target='_self'>{label}</a>",
                unsafe_allow_html=True
            )
    st.markdown("---")
