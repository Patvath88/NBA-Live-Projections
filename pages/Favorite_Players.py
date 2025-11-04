import streamlit as st
import pandas as pd
import os
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime
from config import init_page, render_navbar

init_page("⭐ Favorite Players")
render_navbar("Favorite_Players")

st.title("⭐ Favorite Player Projections")

fav_file = "favorites.csv"
proj_file = "saved_projections.csv"

# Load favorites
if not os.path.exists(fav_file):
    st.warning("No favorites saved yet.")
    favorites = []
else:
    favorites = pd.read_csv(fav_file)["player"].tolist()

all_players = [p["full_name"] for p in players.get_active_players()]
selection = st.multiselect("Add / Remove Favorite Players:", all_players, favorites)

# Save favorites
if st.button("💾 Save Favorites"):
    pd.DataFrame({"player": selection}).to_csv(fav_file, index=False)
    st.success("Favorites updated!")

# Generate projections
if st.button("⚡ Generate Today's Projections"):
    results = []
    for name in selection:
        pid = next((p["id"] for p in players.get_active_players() if p["full_name"] == name), None)
        if not pid:
            continue
        try:
            gl = playergamelog.PlayerGameLog(player_id=pid, season="2025-26").get_data_frames()[0]
            stats = gl.tail(10)[["PTS", "REB", "AST", "FG3M", "STL", "BLK", "TOV"]].mean().to_dict()
            stats["PRA"] = stats["PTS"] + stats["REB"] + stats["AST"]
            stats["player"] = name
            stats["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            stats["status"] = "upcoming"
            results.append(stats)
        except:
            continue

    if results:
        df = pd.DataFrame(results)
        if os.path.exists(proj_file):
            existing = pd.read_csv(proj_file)
            df = pd.concat([existing, df], ignore_index=True)
        df.to_csv(proj_file, index=False)
        st.success("Favorite player projections saved to Upcoming Projections.")

