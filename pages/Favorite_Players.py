import streamlit as st
import pandas as pd
from config import init_page, render_navbar

init_page("⭐ Favorite Players")
render_navbar("Favorites")

st.title("⭐ My Favorite Players")

if "favorites" not in st.session_state:
    st.session_state["favorites"] = []

new_player = st.text_input("Add a Player to Favorites:")
if st.button("Add"):
    if new_player and new_player not in st.session_state["favorites"]:
        st.session_state["favorites"].append(new_player)

if st.session_state["favorites"]:
    st.write("### Favorite Players List")
    st.write(st.session_state["favorites"])
else:
    st.info("You haven't added any players yet.")
