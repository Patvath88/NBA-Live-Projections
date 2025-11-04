import streamlit as st
import pandas as pd
from config import init_page, render_navbar

init_page("🟢 Live Projections")
render_navbar("Live")

st.title("🟢 Live Game Tracking")

try:
    data = pd.read_csv("saved_projections.csv")
    live = data[data["status"] == "live"]
    if live.empty:
        st.info("No games currently live.")
    else:
        st.dataframe(live)
except FileNotFoundError:
    st.warning("No saved projections yet.")
