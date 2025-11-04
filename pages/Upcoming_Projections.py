import streamlit as st
import pandas as pd
from config import init_page, render_navbar
import os

init_page("📅 Upcoming Projections")
render_navbar("Upcoming_Projections")

st.title("📅 Upcoming Game Projections")

path = "saved_projections.csv"
if not os.path.exists(path):
    st.info("No projections saved yet.")
    st.stop()

df = pd.read_csv(path)

if "status" not in df.columns:
    st.error("Missing 'status' column in saved projections file.")
    st.stop()

upcoming = df[df["status"] == "upcoming"]

if upcoming.empty:
    st.info("No upcoming projections found.")
else:
    for player_name, group in upcoming.groupby("player"):
        st.subheader(player_name)
        cols = st.columns(4)
        for i, (stat, val) in enumerate(group.iloc[-1].items()):
            if stat in ["player", "timestamp", "status"]:
                continue
            with cols[i % 4]:
                st.metric(stat, val)
        st.markdown("---")
