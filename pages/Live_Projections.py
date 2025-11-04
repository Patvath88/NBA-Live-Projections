import streamlit as st
import pandas as pd
import time
from config import init_page, render_navbar
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
import os

init_page("🟢 Live Projections")
render_navbar("Live_Projections")

st.title("🟢 Live Projection Tracker")

path = "saved_projections.csv"
if not os.path.exists(path):
    st.info("No projections file found.")
    st.stop()

df = pd.read_csv(path)
live = df[df["status"] == "live"]

if live.empty:
    st.info("No live projections found.")
    st.stop()

nba_players = players.get_active_players()
player_map = {p["full_name"]: p["id"] for p in nba_players}

REFRESH_INTERVAL = 30
st.caption("Auto-refresh every 30 seconds.")
time.sleep(1)

for player_name, group in live.groupby("player"):
    pid = player_map.get(player_name)
    if not pid:
        continue
    st.markdown(f"### {player_name}")
    try:
        gl = playergamelog.PlayerGameLog(player_id=pid, season="2025-26").get_data_frames()[0]
        gl = gl.sort_values("GAME_DATE", ascending=False).iloc[0]
        live_stats = {
            "PTS": gl["PTS"],
            "REB": gl["REB"],
            "AST": gl["AST"],
            "FG3M": gl["FG3M"],
            "STL": gl["STL"],
            "BLK": gl["BLK"],
            "TOV": gl["TOV"],
            "PRA": gl["PTS"] + gl["REB"] + gl["AST"],
        }
    except Exception:
        st.info("Live data unavailable.")
        continue

    latest_proj = group.iloc[-1].to_dict()
    cols = st.columns(4)
    i = 0
    for stat, proj_val in latest_proj.items():
        if stat in ["timestamp", "player", "status"]:
            continue
        live_val = live_stats.get(stat, 0)
        hit = "✅" if live_val >= proj_val else "❌"
        with cols[i % 4]:
            st.metric(f"{stat} {hit}", f"{live_val}", f"Proj: {proj_val}")
        i += 1
    st.markdown("---")
st.experimental_rerun()
