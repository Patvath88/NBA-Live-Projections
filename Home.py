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
</style>
""", unsafe_allow_html=True)

# ---------------------- NAVIGATION ----------------------
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
            f"<a href='/pages/{page}' target='_self' "
            f"style='text-decoration:none; color:white; "
            f"display:block; text-align:center; border:2px solid #E50914; "
            f"padding:8px; border-radius:10px; background-color:#111; "
            f"box-shadow:0px 0px 10px #E50914;'>{label}</a>",
            unsafe_allow_html=True
        )

# ---------------------- HELPERS ----------------------
def get_today_schedule(date):
    """Fetch scoreboard data for given date"""
    try:
        url = f"https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_{date}.json"
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return []
        data = r.json().get("scoreboard", {}).get("games", [])
        return data
    except Exception:
        return []

def get_team_logo(team_code):
    return f"https://cdn.nba.com/logos/nba/{team_code}_logo.svg"

def get_injuries():
    """Fetch injury report"""
    try:
        url = "https://cdn.nba.com/static/json/injury/injuryReport.json"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json().get("league", {}).get("standard", [])
        return []
    except Exception:
        return []

# ---------------------- TODAY'S GAMES ----------------------
today = dt.datetime.now().strftime("%Y-%m-%d")
games = get_today_schedule(today)

st.header(f"📅 Today's Games — {today}")
if not games:
    st.info("No games scheduled for today.")
else:
    for g in games:
        home, away = g["homeTeam"], g["awayTeam"]
        status = g.get("gameStatusText", "TBD")
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            st.image(get_team_logo(away["teamTricode"]), width=60)
            st.markdown(f"<div class='card'>{away['teamTricode']}</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"### 🕓 {g['gameTimeEastern']} — {status}")
            if status != "Upcoming":
                st.markdown(f"**{away['score']} - {home['score']}**")
        with col3:
            st.image(get_team_logo(home["teamTricode"]), width=60)
            st.markdown(f"<div class='card'>{home['teamTricode']}</div>", unsafe_allow_html=True)
        st.markdown("---")

# ---------------------- NEXT 3 DAYS ----------------------
with st.expander("📆 View Next 3 Days Schedule"):
    for i in range(1, 4):
        date_check = (dt.datetime.now() + dt.timedelta(days=i)).strftime("%Y-%m-%d")
        games = get_today_schedule(date_check)
        st.subheader(f"{date_check}")
        if not games:
            st.caption("No games scheduled.")
            continue
        for g in games:
            home, away = g["homeTeam"], g["awayTeam"]
            st.markdown(f"🏀 **{away['teamTricode']} @ {home['teamTricode']}** — {g['gameTimeEastern']}")

# ---------------------- INJURY REPORT ----------------------
st.header("💉 Injury Report — Teams Playing Today")
injuries = get_injuries()

if not injuries:
    st.info("No injury data available.")
else:
    # Filter to today's teams
    today_teams = {t["homeTeam"]["teamTricode"] for t in games} | {t["awayTeam"]["teamTricode"] for t in games}
    df = pd.DataFrame(injuries)
    df_today = df[df["teamTricode"].isin(today_teams)]

    for team in today_teams:
        team_inj = df_today[df_today["teamTricode"] == team]
        if team_inj.empty:
            continue
        st.markdown(f"### {team}")
        for _, row in team_inj.iterrows():
            st.markdown(
                f"**{row['playerName']}** — {row['injuryStatus']}<br><small>{row.get('description','')}</small>",
                unsafe_allow_html=True
            )

with st.expander("💉 View Injuries for Next 3 Days"):
    for i in range(1, 4):
        date_check = (dt.datetime.now() + dt.timedelta(days=i)).strftime("%Y-%m-%d")
        games = get_today_schedule(date_check)
        st.subheader(f"{date_check}")
        if not games:
            st.caption("No games scheduled.")
            continue
        next_teams = {t["homeTeam"]["teamTricode"] for t in games} | {t["awayTeam"]["teamTricode"] for t in games}
        df_next = df[df["teamTricode"].isin(next_teams)]
        for team in next_teams:
            team_inj = df_next[df_next["teamTricode"] == team]
            if team_inj.empty:
                continue
            st.markdown(f"#### {team}")
            for _, row in team_inj.iterrows():
                st.markdown(
                    f"**{row['playerName']}** — {row['injuryStatus']}<br><small>{row.get('description','')}</small>",
                    unsafe_allow_html=True
                )
