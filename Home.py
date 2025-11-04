import streamlit as st
import requests
import pandas as pd
import datetime as dt

# ---------------------- PAGE CONFIG ----------------------
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
</style>
""", unsafe_allow_html=True)

# ---------------------- NAVIGATION ----------------------
st.title("🏀 NBA AI Projection Dashboard")

# Clean Streamlit-compatible internal routing (no HTML hrefs)
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
        if st.button(label):
            st.switch_page(f"pages/{page}.py")

st.markdown("---")

# ---------------------- DATA HELPERS ----------------------
def get_today_games():
    """Fetch today's NBA games from ESPN API."""
    try:
        url = "https://site.web.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
        r = requests.get(url, timeout=10)
        data = r.json()
        games = data.get("events", [])
        today_games = []
        for g in games:
            comp = g.get("competitions", [{}])[0]
            teams = comp.get("competitors", [])
            home = next((t for t in teams if t.get("homeAway") == "home"), {})
            away = next((t for t in teams if t.get("homeAway") == "away"), {})
            game_data = {
                "home": home.get("team", {}).get("abbreviation", ""),
                "away": away.get("team", {}).get("abbreviation", ""),
                "home_logo": home.get("team", {}).get("logo", ""),
                "away_logo": away.get("team", {}).get("logo", ""),
                "status": g.get("status", {}).get("type", {}).get("description", ""),
                "time": g.get("status", {}).get("type", {}).get("shortDetail", ""),
            }
            today_games.append(game_data)
        return today_games
    except Exception:
        return []

def get_upcoming_games(days=3):
    """Fetch next few days' NBA games."""
    try:
        url = f"https://site.web.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
        r = requests.get(url, timeout=10)
        data = r.json().get("events", [])
        upcoming = []
        for g in data:
            comp = g.get("competitions", [{}])[0]
            date = comp.get("date", "")
            game_date = dt.datetime.fromisoformat(date.replace("Z", "+00:00")).date()
            if game_date > dt.datetime.now().date() and game_date <= (dt.datetime.now().date() + dt.timedelta(days=days)):
                teams = comp.get("competitors", [])
                home = next((t for t in teams if t.get("homeAway") == "home"), {})
                away = next((t for t in teams if t.get("homeAway") == "away"), {})
                upcoming.append({
                    "date": game_date,
                    "home": home.get("team", {}).get("abbreviation", ""),
                    "away": away.get("team", {}).get("abbreviation", ""),
                    "time": g.get("status", {}).get("type", {}).get("shortDetail", "")
                })
        return upcoming
    except Exception:
        return []

def get_injuries():
    """Fetch active NBA injuries from ESPN API."""
    try:
        url = "https://site.web.api.espn.com/apis/site/v2/sports/basketball/nba/injuries"
        r = requests.get(url, timeout=10)
        data = r.json().get("injuries", [])
        injuries = []
        for team in data:
            team_name = team.get("team", {}).get("abbreviation", "")
            for player in team.get("injuries", []):
                injuries.append({
                    "team": team_name,
                    "player": player.get("athlete", {}).get("displayName", ""),
                    "status": player.get("status", ""),
                    "desc": player.get("details", "")
                })
        return injuries
    except Exception:
        return []

# ---------------------- TODAY'S GAMES ----------------------
today_str = dt.datetime.now().strftime("%A, %B %d, %Y")
st.header(f"📅 Today's NBA Games — {today_str}")

games = get_today_games()
if not games:
    st.info("No games found or ESPN feed unavailable.")
else:
    for g in games:
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
        st.markdown("---")

# ---------------------- UPCOMING ----------------------
with st.expander("📆 View Next 3 Days Schedule"):
    upcoming = get_upcoming_games(3)
    if not upcoming:
        st.caption("No upcoming games found.")
    else:
        for g in upcoming:
            st.markdown(f"🏀 **{g['away']} @ {g['home']}** — {g['time']} ({g['date']})")

# ---------------------- INJURY REPORT ----------------------
st.header("💉 Injury Report — Teams Playing Today")

injuries = get_injuries()
if not injuries:
    st.info("No injury data available.")
else:
    df = pd.DataFrame(injuries)
    today_teams = {g["home"] for g in games} | {g["away"] for g in games}
    df_today = df[df["team"].isin(today_teams)]
    if df_today.empty:
        st.info("No reported injuries for today's teams.")
    else:
        for team in sorted(today_teams):
            team_inj = df_today[df_today["team"] == team]
            if team_inj.empty:
                continue
            st.markdown(f"### {team}")
            for _, row in team_inj.iterrows():
                st.markdown(
                    f"**{row['player']}** — {row['status']}<br><small>{row['desc']}</small>",
                    unsafe_allow_html=True
                )

# ---------------------- FUTURE INJURIES ----------------------
with st.expander("💉 View Injuries for Next 3 Days"):
    if not injuries:
        st.caption("No injuries listed.")
    else:
        upcoming_teams = {g["home"] for g in upcoming} | {g["away"] for g in upcoming}
        df_next = df[df["team"].isin(upcoming_teams)]
        for team in sorted(upcoming_teams):
            team_inj = df_next[df_next["team"] == team]
            if team_inj.empty:
                continue
            st.markdown(f"#### {team}")
            for _, row in team_inj.iterrows():
                st.markdown(
                    f"**{row['player']}** — {row['status']}<br><small>{row['desc']}</small>",
                    unsafe_allow_html=True
                )
