import streamlit as st
import pandas as pd
from config import init_page, render_navbar

init_page("📅 Upcoming Projections")
render_navbar("Upcoming")

st.title("📅 Upcoming Game Projections")

try:
    data = pd.read_csv("saved_projections.csv")
    upcoming = data[data["status"] == "upcoming"]
    if upcoming.empty:
        st.info("No upcoming projections available.")
    else:
        st.dataframe(upcoming)
except FileNotFoundError:
    st.warning("No saved projections yet.")

