import streamlit as st
import pandas as pd
import json
import os
import datetime as dt
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
from sklearn.ensemble import RandomForestRegressor
import numpy as np
import requests

st.set_page_config(page_title="⭐ Favorite Players", layout="wide")
st.markdown("<style>body{background-color:black;color:white;}</style>", unsafe_allow_html=True)
TEAM_COLOR = "#E50914"
CONTRAST = "#00FFFF"

# ---------------------- FILE PATHS ----------------------
FAV_PATH = "favorite_players.json"
PROJ_PATH = "saved_projections.csv"

# ---------------------- UTILITIES ----------------------
def load_favorites():
    if os.path.exists(FAV_PATH):
        with open(FAV_PATH, "r") as f:
            return json.load(f)
    return []

def save_favorites(favs):
    with open(FAV_PATH, "w") as f:
        json.dump(favs, f)

def get_next_game_info(team_code):
    """Fetch next game for team."""
    try:
        today = dt.datetime.now().date()
        for offset in range(0, 7):
            date_check = today + dt.timedelta(days=offset)
            date_str = date_check.strftime("%Y-%m-%d")
            url = f"https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_{date_str}.json"
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                continue
            games = resp.json().get("scoreboard", {}).get("games", [])
            for game in games:
                home = game["homeTeam"]["teamTricode"]
                away = game["awayTeam"]["teamTricode"]
                if home == team_code or away == team_code:
                    matchup = f"{away} @ {home}" if home == team_code else f"{home} @ {away}"
                    home_game = (home == team_code)
                    return date_str, matchup, home_game
        return "", "", None
    except Exception:
        return "", "", None

def get_games(pid, season):
    try:
        gl = playergamelog.PlayerGameLog(player_id=pid, season=season).get_data_frames()[0]
        gl["GAME_DATE"] = pd.to_datetime(gl["GAME_DATE"])
        gl = gl.sort_values("GAME_DATE")
        return gl
    except Exception:
        return pd.DataFrame()

def enrich(df):
    if df.empty:
        return df
    df["PRA"] = df["PTS"] + df["REB"] + df["AST"]
    return df

def predict_next(df):
    if df is None or len(df) < 3:
        return 0
    X = np.arange(len(df)).reshape(-1, 1)
    y = df.values
    m = RandomForestRegressor(n_estimators=100, random_state=42)
    m.fit(X, y)
    X_pred = np.array([[len(df)]])
    return round(float(m.predict(X_pred)), 1)

def auto_save_projection(player_name, pid):
    CURRENT_SEASON = "2025-26"
    gl = enrich(get_games(pid, CURRENT_SEASON))
    if gl.empty:
        return
    pred = {s: predict_next(gl[s]) for s in ["PTS", "REB", "AST", "PRA"] if s in gl.columns}
    team_code = gl.iloc[-1]["MATCHUP"].split(" ")[0]
    game_date, opponent, home_game = get_next_game_info(team_code)
    if not game_date:
        return
    df = pd.DataFrame([{
        "timestamp": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "player": player_name,
        "game_date": game_date,
        "opponent": opponent,
        "home_away": "Home" if home_game else "Away",
        "status": "upcoming",
        **pred
    }])
    if os.path.exists(PROJ_PATH):
        existing = pd.read_csv(PROJ_PATH)
        # avoid duplicate game
        if ((existing["player"] == player_name) & (existing["game_date"] == game_date)).any():
            return
        existing = pd.concat([existing, df], ignore_index=True)
        existing.to_csv(PROJ_PATH, index=False)
    else:
        df.to_csv(PROJ_PATH, index=False)

# ---------------------- MAIN APP ----------------------
st.title("⭐ Favorite Players Manager")

favorites = load_favorites()
nba_players = players.get_active_players()
names = sorted([p["full_name"] for p in nba_players])

new_player = st.selectbox("Add a player to favorites", [""] + names)
if st.button("➕ Add to Favorites") and new_player:
    if new_player not in favorites:
        favorites.append(new_player)
        save_favorites(favorites)
        st.success(f"{new_player} added to favorites.")
    else:
        st.info(f"{new_player} is already in your favorites list.")

if favorites:
    st.markdown("### Your Favorite Players")
    for fav in favorites:
        st.markdown(f"- {fav}")
else:
    st.info("No favorite players yet.")

if st.button("🧠 Generate & Save Projections for Favorites"):
    for fav in favorites:
        pid = next((p["id"] for p in nba_players if p["full_name"] == fav), None)
        if pid:
            auto_save_projection(fav, pid)
    st.success("Daily projections generated for all favorite players!")
