import streamlit as st
import requests
import pandas as pd
import datetime as dt
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="🏠 NBA AI Dashboard", layout="wide")

# ---------------------- STYLES ----------------------
st.markdown("""
<style>
body { background-color: black; color: white; }
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
}
a.nav-link:hover {
    background-color:#E50914;
}
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
        st.markdown(f"<a class='nav-link' href='/pages/{page}' target='_self'>{label}</a>", unsafe_allow_html=True)

st.markdown("---")

# ---------------------- HELPERS ----------------------
def get_team_logo(team_code):
    return f"https://cdn.nba.com/logos/nba/{team_code}_logo.svg"

@st.cache_data(ttl=60)
def get_today_schedule(date=None):
    """Fetch today's scoreboard data."""
    try:
        url = "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard.json"
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return []
        games = r.json().get("scoreboard", {}).get("games", [])
        return games
    except Exception:
        return []

@st.cache_data(ttl=3600)
def get_injuries():
    """Fetch and normalize injury report."""
    try:
        url = "https://cdn.nba.com/static/json/injury/injuryReport.json"
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return []
        data = r.json()
        teams = data.get("teams", [])
        injuries = []
        for team in teams:
            tcode = team.get("teamTricode", "")
            for p in team.get("players", []):
                injuries.append({
                    "teamTricode": tcode,
                    "playerName": p.get("firstName", "") + " " + p.get("lastName", ""),
                    "status": p.get("injuryStatus", ""),
                    "desc": p.get("injuryDesc", "")
                })
        return injuries
    except Exception:
        return []

# ---------------------- TODAY'S GAMES ----------------------
today_str = dt.datetime.now().strftime("%Y-%m-%d")
games = get_today_schedule(today_str)

st.header(f"📅 Today's NBA Games — {today_str}")
if not games:
    st.info("No games scheduled or feed unavailable.")
else:
    for g in games:
        home, away = g["homeTeam"], g["awayTeam"]
        status = g.get("gameStatusText", "TBD")
        home_logo = get_team_logo(home["teamTricode"])
        away_logo = get_team_logo(away["teamTricode"])
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            st.image(away_logo, width=60)
            st.markdown(f"<div class='card'>{away['teamTricode']}</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"### 🕓 {g['gameTimeEastern']} — {status}")
            if status.lower() not in ["upcoming", "scheduled"]:
                st.markdown(f"**{away['score']} - {home['score']}**")
        with col3:
            st.image(home_logo, width=60)
            st.markdown(f"<div class='card'>{home['teamTricode']}</div>", unsafe_allow_html=True)
        st.markdown("---")

# ---------------------- NEXT 3 DAYS ----------------------
with st.expander("📆 Next 3 Days Schedule"):
    for i in range(1, 4):
        date_check = (dt.datetime.now() + dt.timedelta(days=i)).strftime("%Y-%m-%d")
        url = f"https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_{date_check}.json"
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            st.caption(f"{date_check}: feed unavailable")
            continue
        games = r.json().get("scoreboard", {}).get("games", [])
        if not games:
            st.caption(f"{date_check}: no games")
            continue
        st.subheader(f"{date_check}")
        for g in games:
            st.markdown(f"🏀 **{g['awayTeam']['teamTricode']} @ {g['homeTeam']['teamTricode']}** — {g['gameTimeEastern']}")

# ---------------------- INJURY REPORT ----------------------
st.header("💉 Injury Report — Teams Playing Today")
injuries = get_injuries()

if not injuries:
    st.info("No injuries or feed unavailable.")
else:
    today_teams = {g["homeTeam"]["teamTricode"] for g in get_today_schedule()} | {
        g["awayTeam"]["teamTricode"] for g in get_today_schedule()
    }
    df = pd.DataFrame(injuries)
    df_today = df[df["teamTricode"].isin(today_teams)]
    if df_today.empty:
        st.info("No reported injuries for today's teams.")
    else:
        for team in sorted(today_teams):
            team_inj = df_today[df_today["teamTricode"] == team]
            if team_inj.empty:
                continue
            st.markdown(f"### {team}")
            for _, row in team_inj.iterrows():
                st.markdown(
                    f"**{row['playerName']}** — {row['status']}<br><small>{row['desc']}</small>",
                    unsafe_allow_html=True
                )

with st.expander("💉 View Injuries Affecting Next 3 Days"):
    for i in range(1, 4):
        date_check = (dt.datetime.now() + dt.timedelta(days=i)).strftime("%Y-%m-%d")
        url = f"https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_{date_check}.json"
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            continue
        games = r.json().get("scoreboard", {}).get("games", [])
        next_teams = {g["homeTeam"]["teamTricode"] for g in games} | {g["awayTeam"]["teamTricode"] for g in games}
        df_next = df[df["teamTricode"].isin(next_teams)]
        if df_next.empty:
            continue
        st.subheader(f"{date_check}")
        for team in sorted(next_teams):
            team_inj = df_next[df_next["teamTricode"] == team]
            if team_inj.empty:
                continue
            st.markdown(f"#### {team}")
            for _, row in team_inj.iterrows():
                st.markdown(
                    f"**{row['playerName']}** — {row['status']}<br><small>{row['desc']}</small>",
                    unsafe_allow_html=True
                )
