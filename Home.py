import streamlit as st
import requests
import pandas as pd
import datetime as dt
import os
import difflib

import streamlit as st
from config import init_page, render_navbar

# ✅ Initialize first
init_page("🏠 NBA AI Dashboard")

# ✅ Then render navbar
render_navbar()

# Continue with your logic...
# (no other st.set_page_config() calls below this line!)


# ---------------------- STYLES ----------------------
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
    border: 2px solid #E50914;
    border-radius: 10px;
    padding: 12px;
    background-color: #111;
    box-shadow: 0px 0px 10px #E50914;
    text-align: center;
    color: white;
}
h1, h2, h3 { color: #00FFFF; }
</style>
""", unsafe_allow_html=True)

# ---------------------- NAVIGATION ----------------------
st.title("🏀 NBA AI Projection Dashboard")

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

# ---------------------- HELPERS ----------------------
@st.cache_data(ttl=60)
def get_today_games():
    """Fetch today's NBA games from ESPN API."""
    try:
        url = "https://site.web.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
        r = requests.get(url, timeout=10)
        data = r.json()
        games = data.get("events", [])
        results = []
        for g in games:
            comp = g.get("competitions", [{}])[0]
            teams = comp.get("competitors", [])
            home = next((t for t in teams if t.get("homeAway") == "home"), {})
            away = next((t for t in teams if t.get("homeAway") == "away"), {})
            results.append({
                "home": home.get("team", {}).get("abbreviation", ""),
                "home_name": home.get("team", {}).get("displayName", ""),
                "away": away.get("team", {}).get("abbreviation", ""),
                "away_name": away.get("team", {}).get("displayName", ""),
                "home_logo": home.get("team", {}).get("logo", ""),
                "away_logo": away.get("team", {}).get("logo", ""),
                "status": g.get("status", {}).get("type", {}).get("description", ""),
                "time": g.get("status", {}).get("type", {}).get("shortDetail", ""),
            })
        return results
    except Exception:
        return []

import streamlit as st
import requests
import pandas as pd
import datetime as dt
import os
import difflib

st.set_page_config(page_title="🏠 NBA AI Dashboard", layout="wide")

# ---------------------- STYLES ----------------------
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
    border: 2px solid #E50914;
    border-radius: 10px;
    padding: 12px;
    background-color: #111;
    box-shadow: 0px 0px 10px #E50914;
    text-align: center;
    color: white;
}
h1, h2, h3 { color: #00FFFF; }
</style>
""", unsafe_allow_html=True)

# ---------------------- NAVIGATION ----------------------
st.title("🏀 NBA AI Projection Dashboard")

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

# ---------------------- HELPERS ----------------------
@st.cache_data(ttl=60)
def get_today_games():
    """Fetch today's NBA games from ESPN API."""
    try:
        url = "https://site.web.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
        r = requests.get(url, timeout=10)
        data = r.json()
        games = data.get("events", [])
        results = []
        for g in games:
            comp = g.get("competitions", [{}])[0]
            teams = comp.get("competitors", [])
            home = next((t for t in teams if t.get("homeAway") == "home"), {})
            away = next((t for t in teams if t.get("homeAway") == "away"), {})
            results.append({
                "home": home.get("team", {}).get("abbreviation", ""),
                "home_name": home.get("team", {}).get("displayName", ""),
                "away": away.get("team", {}).get("abbreviation", ""),
                "away_name": away.get("team", {}).get("displayName", ""),
                "home_logo": home.get("team", {}).get("logo", ""),
                "away_logo": away.get("team", {}).get("logo", ""),
                "status": g.get("status", {}).get("type", {}).get("description", ""),
                "time": g.get("status", {}).get("type", {}).get("shortDetail", ""),
            })
        return results
    except Exception:
        return []

@st.cache_data(ttl=600)
def get_injuries():
    """Fetch NBA injuries from ESPN API and normalize."""
    try:
        url = "https://site.web.api.espn.com/apis/site/v2/sports/basketball/nba/injuries"
        r = requests.get(url, timeout=10)
        data = r.json().get("injuries", [])
        injuries = []
        for team in data:
            team_code = team.get("team", {}).get("abbreviation", "")
            team_name = team.get("team", {}).get("displayName", "")
            for p in team.get("injuries", []):
                injuries.append({
                    "team": team_code,
                    "team_name": team_name,
                    "player": p.get("athlete", {}).get("displayName", ""),
                    "status": p.get("status", ""),
                    "desc": p.get("shortComment") or p.get("longComment") or p.get("details", "")
                })
        return pd.DataFrame(injuries)
    except Exception:
        return pd.DataFrame()

# ---------------------- TODAY'S GAMES ----------------------
today_str = dt.datetime.now().strftime("%A, %B %d, %Y")
st.header(f"📅 Today's NBA Games — {today_str}")

today_games = get_today_games()
inj_df = get_injuries()

if not today_games:
    st.info("No games found or ESPN feed unavailable.")
else:
    for g in today_games:
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            if g["away_logo"]:
                st.image(g["away_logo"], width=60)
            st.markdown(f"<div class='card'>{g['away']}</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"### 🕓 {g['time']} — {g['status']}")
        with col3:
            if g["home_logo"]:
                st.image(g["home_logo"], width=60)
            st.markdown(f"<div class='card'>{g['home']}</div>", unsafe_allow_html=True)

        # Embed injuries under this game
        if not inj_df.empty:
            # Match injuries to either team by code or name similarity
            all_team_codes = inj_df["team"].dropna().unique().tolist()
            home_match = difflib.get_close_matches(g["home"], all_team_codes, n=1)
            away_match = difflib.get_close_matches(g["away"], all_team_codes, n=1)
            home_inj = inj_df[inj_df["team"].isin(home_match)]
            away_inj = inj_df[inj_df["team"].isin(away_match)]

            with st.expander(f"💉 Injury Report: {g['away_name']} vs {g['home_name']}"):
                if home_inj.empty and away_inj.empty:
                    st.caption("No reported injuries for this matchup.")
                else:
                    if not away_inj.empty:
                        st.markdown(f"**{g['away_name']}**:")
                        for _, row in away_inj.iterrows():
                            st.markdown(
                                f"- {row['player']} — {row['status']}<br><small>{row['desc']}</small>",
                                unsafe_allow_html=True
                            )
                    if not home_inj.empty:
                        st.markdown(f"**{g['home_name']}**:")
                        for _, row in home_inj.iterrows():
                            st.markdown(
                                f"- {row['player']} — {row['status']}<br><small>{row['desc']}</small>",
                                unsafe_allow_html=True
                            )
        st.markdown("---")

# ---------------------- MODEL SUMMARY ----------------------
st.header("📊 Model Summary Overview")

path = "saved_projections.csv"
if os.path.exists(path):
    data = pd.read_csv(path)
    if "status" in data.columns:
        summary = data["status"].value_counts().to_dict()
        upcoming = summary.get("upcoming", 0)
        live = summary.get("live", 0)
        completed = summary.get("completed", 0)
        cols = st.columns(3)
        with cols[0]:
            st.metric("📅 Upcoming", upcoming)
        with cols[1]:
            st.metric("🟢 Live", live)
        with cols[2]:
            st.metric("🏁 Completed", completed)
    else:
        st.info("Projection file missing 'status' column.")
else:
    st.info("No projections saved yet.")

st.markdown("---")
st.caption(f"🕒 Data last updated: {dt.datetime.now().strftime('%I:%M %p')}")


# ---------------------- TODAY'S GAMES ----------------------
today_str = dt.datetime.now().strftime("%A, %B %d, %Y")
st.header(f"📅 Today's NBA Games — {today_str}")

today_games = get_today_games()
inj_df = get_injuries()

if not today_games:
    st.info("No games found or ESPN feed unavailable.")
else:
    for g in today_games:
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            if g["away_logo"]:
                st.image(g["away_logo"], width=60)
            st.markdown(f"<div class='card'>{g['away']}</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"### 🕓 {g['time']} — {g['status']}")
        with col3:
            if g["home_logo"]:
                st.image(g["home_logo"], width=60)
            st.markdown(f"<div class='card'>{g['home']}</div>", unsafe_allow_html=True)

        # Embed injuries under this game
        if not inj_df.empty:
            # Match injuries to either team by code or name similarity
            all_team_codes = inj_df["team"].dropna().unique().tolist()
            home_match = difflib.get_close_matches(g["home"], all_team_codes, n=1)
            away_match = difflib.get_close_matches(g["away"], all_team_codes, n=1)
            home_inj = inj_df[inj_df["team"].isin(home_match)]
            away_inj = inj_df[inj_df["team"].isin(away_match)]

            with st.expander(f"💉 Injury Report: {g['away_name']} vs {g['home_name']}"):
                if home_inj.empty and away_inj.empty:
                    st.caption("No reported injuries for this matchup.")
                else:
                    if not away_inj.empty:
                        st.markdown(f"**{g['away_name']}**:")
                        for _, row in away_inj.iterrows():
                            st.markdown(
                                f"- {row['player']} — {row['status']}<br><small>{row['desc']}</small>",
                                unsafe_allow_html=True
                            )
                    if not home_inj.empty:
                        st.markdown(f"**{g['home_name']}**:")
                        for _, row in home_inj.iterrows():
                            st.markdown(
                                f"- {row['player']} — {row['status']}<br><small>{row['desc']}</small>",
                                unsafe_allow_html=True
                            )
        st.markdown("---")

# ---------------------- MODEL SUMMARY ----------------------
st.header("📊 Model Summary Overview")

path = "saved_projections.csv"
if os.path.exists(path):
    data = pd.read_csv(path)
    if "status" in data.columns:
        summary = data["status"].value_counts().to_dict()
        upcoming = summary.get("upcoming", 0)
        live = summary.get("live", 0)
        completed = summary.get("completed", 0)
        cols = st.columns(3)
        with cols[0]:
            st.metric("📅 Upcoming", upcoming)
        with cols[1]:
            st.metric("🟢 Live", live)
        with cols[2]:
            st.metric("🏁 Completed", completed)
    else:
        st.info("Projection file missing 'status' column.")
else:
    st.info("No projections saved yet.")

st.markdown("---")
st.caption(f"🕒 Data last updated: {dt.datetime.now().strftime('%I:%M %p')}")
