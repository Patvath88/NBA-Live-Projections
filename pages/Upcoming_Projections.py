import streamlit as st
import pandas as pd
import requests
import datetime as dt
from PIL import Image
from io import BytesIO
import os

st.set_page_config(page_title="📅 Upcoming Projections", layout="wide")
st.markdown("<style>body{background-color:black;color:white;}</style>", unsafe_allow_html=True)
TEAM_COLOR = "#E50914"
CONTRAST = "#00FFFF"

# ---------------------- HELPERS ----------------------
def get_team_logo(team_code):
    return f"https://cdn.nba.com/logos/nba/{team_code}_logo.svg"

def get_player_photo(pid):
    urls = [
        f"https://cdn.nba.com/headshots/nba/latest/1040x760/{pid}.png",
        f"https://stats.nba.com/media/players/headshot/{pid}.png"
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200 and "image" in r.headers.get("Content-Type", ""):
                return Image.open(BytesIO(r.content))
        except Exception:
            continue
    return None

def get_live_game_data(team_code):
    """Returns game status and details from NBA’s liveData feed."""
    try:
        today = dt.datetime.now().strftime("%Y-%m-%d")
        url = f"https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_{today}.json"
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return None
        games = resp.json().get("scoreboard", {}).get("games", [])
        for game in games:
            home = game["homeTeam"]["teamTricode"]
            away = game["awayTeam"]["teamTricode"]
            if home == team_code or away == team_code:
                return {
                    "status": game["gameStatusText"],
                    "home": home,
                    "away": away,
                    "home_score": game["homeTeam"]["score"],
                    "away_score": game["awayTeam"]["score"],
                    "gameId": game["gameId"]
                }
        return None
    except Exception:
        return None

# ---------------------- LOAD DATA ----------------------
path = "saved_projections.csv"
if not os.path.exists(path):
    st.info("No projections saved yet.")
    st.stop()

data = pd.read_csv(path)
if "status" not in data.columns:
    st.warning("Legacy projection file missing 'status' column. Please re-save projections.")
    st.stop()

upcoming = data[data["status"] == "upcoming"].copy()
if upcoming.empty:
    st.info("No upcoming projections available.")
    st.stop()

st.title("📅 Upcoming Game Projections")
st.caption("Automatically updates when games start (moves to Live Projections).")

# ---------------------- DISPLAY ----------------------
nba_players = requests.get("https://cdn.nba.com/headshots/nba/latest/1040x760/").text
grouped = upcoming.groupby("player")

for player_name, group in grouped:
    row = group.iloc[-1]
    opponent = row.get("opponent", "TBD")
    game_date = row.get("game_date", "TBD")
    home_away = row.get("home_away", "")
    status_info = get_live_game_data(opponent.split(" ")[-1]) if isinstance(opponent, str) else None

    # check if game has started
    if status_info and status_info["status"] in ["In Progress", "Halftime", "1st Qtr", "2nd Qtr", "3rd Qtr", "4th Qtr"]:
        # promote to live
        data.loc[data["player"] == player_name, "status"] = "live"
        data.to_csv(path, index=False)
        continue

    col1, col2 = st.columns([1, 3])
    with col1:
        pid = None
        try:
            from nba_api.stats.static import players
            pid = next((p["id"] for p in players.get_active_players() if p["full_name"] == player_name), None)
        except Exception:
            pass
        img = get_player_photo(pid) if pid else None
        if img:
            st.image(img, width=140)
        st.markdown(f"**{player_name}**")
        st.caption(f"📅 {game_date}<br>🆚 {opponent}<br>{home_away}", unsafe_allow_html=True)

    with col2:
        cols = st.columns(4)
        i = 0
        for stat, val in row.items():
            if stat in ["timestamp", "player", "status", "opponent", "game_date", "home_away"]:
                continue
            with cols[i % 4]:
                st.metric(stat, f"{val}")
            i += 1
    st.markdown("---")

# ---------------------- SAVE UPDATED STATUS ----------------------
data.to_csv(path, index=False)
