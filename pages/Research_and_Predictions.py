
import streamlit as st
import pandas as pd
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
from config import init_page, render_navbar

init_page("🧠 Research & Predictions")
render_navbar("Research_and_Predictions")

st.title("🧠 Research & Player Projections")

player_name = st.text_input("Enter a player name:", "LeBron James")
season = "2025-26"

if player_name:
    player = players.find_players_by_full_name(player_name)
    if not player:
        st.error("Player not found.")
    else:
        pid = player[0]["id"]
        try:
            gamelog = playergamelog.PlayerGameLog(player_id=pid, season=season)
            df = gamelog.get_data_frames()[0]
            st.write(f"Recent {len(df)} games for {player_name}")
            st.dataframe(df[["GAME_DATE", "PTS", "REB", "AST", "FG_PCT"]])
        except Exception as e:
            st.warning(f"No data for 2025–26. Trying 2024–25 and preseason...")
            try:
                gamelog = playergamelog.PlayerGameLog(player_id=pid, season="2024-25")
                df = gamelog.get_data_frames()[0]
                st.dataframe(df[["GAME_DATE", "PTS", "REB", "AST", "FG_PCT"]])
            except Exception as e2:
                st.error(f"Could not retrieve data: {e2}")
