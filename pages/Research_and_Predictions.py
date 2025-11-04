import streamlit as st
import pandas as pd
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
from config import init_page, render_navbar

init_page("🧠 Research & Predictions")
render_navbar("Research")

st.title("🧠 Player Research & AI Predictions")

nba_players = players.get_active_players()
player_names = [p["full_name"] for p in nba_players]
selected_player = st.selectbox("Select a Player", player_names)

player_info = next((p for p in nba_players if p["full_name"] == selected_player), None)
pid = player_info["id"]

def fetch_games(pid, season):
    try:
        gl = playergamelog.PlayerGameLog(player_id=pid, season=season).get_data_frames()[0]
        return gl
    except:
        return pd.DataFrame()

current = fetch_games(pid, "2025-26")
preseason = fetch_games(pid, "2025-26 Preseason")
previous = fetch_games(pid, "2024-25")

df = pd.concat([current, preseason, previous], ignore_index=True)
if df.empty:
    st.warning("No data available yet for this player.")
else:
    st.write(f"Total games loaded: {len(df)}")
    st.dataframe(df.head())

    st.markdown("### Recent Performance (Last 5 Games)")
    st.dataframe(df.head(5)[["GAME_DATE", "MATCHUP", "PTS", "REB", "AST", "FG3M", "STL", "BLK"]])
