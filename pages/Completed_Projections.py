import streamlit as st
import pandas as pd
from config import init_page, render_navbar
import os

init_page("🏁 Completed Projections")
render_navbar("Completed_Projections")

st.title("🏁 Completed Games — Projection Accuracy")

path = "saved_projections.csv"
if not os.path.exists(path):
    st.info("No projections found.")
    st.stop()

df = pd.read_csv(path)
if "status" not in df.columns:
    st.error("Missing 'status' column.")
    st.stop()

completed = df[df["status"] == "completed"]

if completed.empty:
    st.info("No completed projections yet.")
    st.stop()

# Calculate model accuracy
numeric_cols = ["PTS", "REB", "AST", "FG3M", "STL", "BLK", "TOV", "PRA"]
for col in numeric_cols:
    completed[f"{col}_Error"] = (completed[col + "_actual"] - completed[col]).abs()

st.metric("Average Error (PRA)", round(completed["PRA_Error"].mean(), 2))

for player_name, group in completed.groupby("player"):
    st.subheader(player_name)
    last = group.iloc[-1]
    cols = st.columns(4)
    for i, stat in enumerate(numeric_cols):
        with cols[i % 4]:
            st.metric(stat, f"{last[stat + '_actual']}", f"Pred: {last[stat]}")
    st.markdown("---")

