import streamlit as st
import pandas as pd
import numpy as np
import requests
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime
from io import BytesIO
from PIL import Image
import plotly.graph_objects as go
import os

# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(page_title="🧠 Research & Predictions", layout="wide")

# ---------------------- STYLE ----------------------
st.markdown("""
<style>
body { background-color: black; color: white; }
.card {
    border:2px solid #E50914;
    border-radius:10px;
    background-color:#111;
    padding:12px;
    text-align:center;
    color:#00FFFF;
    box-shadow:0px 0px 10px #E50914;
}
h1, h2, h3, h4 { color: #00FFFF; }
</style>
""", unsafe_allow_html=True)

# ---------------------- SIDEBAR TOGGLE ----------------------
mode = st.sidebar.radio("Mode:", ["🧠 AI Predictions", "📈 Historical Trends"])

# ---------------------- UTILITIES ----------------------
@st.cache_data(show_spinner=False)
def get_games(player_id, season, season_type="Regular Season"):
    """Fetch player gamelog for given season and type."""
    try:
        gl = playergamelog.PlayerGameLog(
            player_id=player_id, season=season, season_type_all_star=season_type
        ).get_data_frames()[0]
        gl["GAME_DATE"] = pd.to_datetime(gl["GAME_DATE"])
        return gl.sort_values("GAME_DATE")
    except Exception:
        return pd.DataFrame()

def get_player_photo(player_id):
    urls = [
        f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png",
        f"https://stats.nba.com/media/players/headshot/{player_id}.png"
    ]
    for url in urls:
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                return Image.open(BytesIO(resp.content))
        except:
            continue
    return None

def enrich(df):
    if df.empty:
        return df
    df["PRA"] = df["PTS"] + df["REB"] + df["AST"]
    df["P+R"] = df["PTS"] + df["REB"]
    df["P+A"] = df["PTS"] + df["AST"]
    df["R+A"] = df["REB"] + df["AST"]
    return df

def train_model(series):
    X = np.arange(len(series)).reshape(-1, 1)
    y = series.values
    m = RandomForestRegressor(n_estimators=200, random_state=42)
    m.fit(X, y)
    return m

def predict_next(series):
    if len(series) < 3:
        return float(series.mean()) if len(series) > 0 else 0.0
    m = train_model(series)
    return round(float(m.predict([[len(series)]])), 1)

# ---------------------- PLAYER SELECTION ----------------------
st.title("🧠 Player Research & AI Predictions")

nba_players = players.get_active_players()
player_list = sorted([p["full_name"] for p in nba_players])
player_name = st.selectbox("Search or Select Player:", [""] + player_list)

if not player_name:
    st.stop()

player_id = next(p["id"] for p in nba_players if p["full_name"] == player_name)

# ---------------------- SEASON DATA LOADING ----------------------
CURRENT_SEASON = "2025-26"
PREVIOUS_SEASON = "2024-25"
PRESEASON = "Pre Season"

regular = enrich(get_games(player_id, CURRENT_SEASON, "Regular Season"))
preseason = enrich(get_games(player_id, CURRENT_SEASON, "Pre Season"))
previous = enrich(get_games(player_id, PREVIOUS_SEASON, "Regular Season"))

# Combine & blend based on weights
frames = []
if not regular.empty:
    regular["weight"] = 0.6
    frames.append(regular)
if not preseason.empty:
    preseason["weight"] = 0.25
    frames.append(preseason)
if not previous.empty:
    previous["weight"] = 0.15
    frames.append(previous)

if not frames:
    st.error("No available data found for this player.")
    st.stop()

blended = pd.concat(frames, ignore_index=True)
blended = blended.sort_values("GAME_DATE")

# ---------------------- NEXT GAME INFO ----------------------
def get_next_game_info(pid):
    try:
        url = f"https://site.web.api.espn.com/apis/site/v2/sports/basketball/nba/players/{pid}"
        r = requests.get(url, timeout=10)
        data = r.json().get("team", {})
        team = data.get("abbreviation", "")
        return team
    except:
        return None

# ---------------------- PLAYER HEADER ----------------------
photo = get_player_photo(player_id)
col1, col2 = st.columns([1, 3])
with col1:
    if photo:
        st.image(photo, width=180)
with col2:
    st.markdown(f"## **{player_name}**")

# ---------------------- PREDICTION CALCULATION ----------------------
if mode == "🧠 AI Predictions":
    st.markdown("### 🧮 AI Projected Next Game Stats")

    stats = ["PTS", "REB", "AST", "FG3M", "STL", "BLK", "TOV", "PRA", "P+R", "P+A", "R+A"]
    predictions = {}
    for stat in stats:
        valid = blended[stat].dropna()
        predictions[stat] = predict_next(valid)

    # Display metrics
    cols = st.columns(4)
    for i, (key, val) in enumerate(predictions.items()):
        with cols[i % 4]:
            st.markdown(
                f"""
                <div class='card'>
                    <div style='font-size:22px;margin-bottom:5px;'>{key}</div>
                    <div style='font-size:32px;margin-top:5px;'>{val}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # Save projections
    if st.button("💾 Save Projection"):
        df_save = pd.DataFrame([{
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "player": player_name,
            **predictions,
            "status": "upcoming"
        }])
        path = "saved_projections.csv"
        if os.path.exists(path):
            existing = pd.read_csv(path)
            df_save = pd.concat([existing, df_save], ignore_index=True)
        df_save.to_csv(path, index=False)
        st.success("✅ Projection saved to Upcoming Projections")

# ---------------------- HISTORICAL TREND MODE ----------------------
elif mode == "📈 Historical Trends":
    st.markdown("### 📊 Player Performance Over Time")

    metric = st.selectbox("Select Stat:", ["PTS", "REB", "AST", "PRA", "FG3M"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=blended["GAME_DATE"],
        y=blended[metric],
        mode="lines+markers",
        name=metric,
        line=dict(width=2)
    ))
    fig.update_layout(
        template="plotly_dark",
        title=f"{player_name} — {metric} Over Time",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------------- HISTORICAL EXPANDER ----------------------
with st.expander("📜 View Historical Performance Averages"):
    recent = blended.tail(10).mean(numeric_only=True).round(1)
    st.metric("Last 10 Avg PTS", recent["PTS"])
    st.metric("Last 10 Avg REB", recent["REB"])
    st.metric("Last 10 Avg AST", recent["AST"])


# ---------------------- SIDEBAR TOGGLE ----------------------
mode = st.sidebar.radio("Mode:", ["🧠 AI Predictions", "📈 Historical Trends"])

# ---------------------- UTILITIES ----------------------
@st.cache_data(show_spinner=False)
def get_games(player_id, season, season_type="Regular Season"):
    """Fetch player gamelog for given season and type."""
    try:
        gl = playergamelog.PlayerGameLog(
            player_id=player_id, season=season, season_type_all_star=season_type
        ).get_data_frames()[0]
        gl["GAME_DATE"] = pd.to_datetime(gl["GAME_DATE"])
        return gl.sort_values("GAME_DATE")
    except Exception:
        return pd.DataFrame()

def get_player_photo(player_id):
    urls = [
        f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png",
        f"https://stats.nba.com/media/players/headshot/{player_id}.png"
    ]
    for url in urls:
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                return Image.open(BytesIO(resp.content))
        except:
            continue
    return None

def enrich(df):
    if df.empty:
        return df
    df["PRA"] = df["PTS"] + df["REB"] + df["AST"]
    df["P+R"] = df["PTS"] + df["REB"]
    df["P+A"] = df["PTS"] + df["AST"]
    df["R+A"] = df["REB"] + df["AST"]
    return df

def train_model(series):
    X = np.arange(len(series)).reshape(-1, 1)
    y = series.values
    m = RandomForestRegressor(n_estimators=200, random_state=42)
    m.fit(X, y)
    return m

def predict_next(series):
    if len(series) < 3:
        return float(series.mean()) if len(series) > 0 else 0.0
    m = train_model(series)
    return round(float(m.predict([[len(series)]])), 1)

# ---------------------- PLAYER SELECTION ----------------------
st.title("🧠 Player Research & AI Predictions")

nba_players = players.get_active_players()
player_list = sorted([p["full_name"] for p in nba_players])
player_name = st.selectbox("Search or Select Player:", [""] + player_list)

if not player_name:
    st.stop()

player_id = next(p["id"] for p in nba_players if p["full_name"] == player_name)

# ---------------------- SEASON DATA LOADING ----------------------
CURRENT_SEASON = "2025-26"
PREVIOUS_SEASON = "2024-25"
PRESEASON = "Pre Season"

regular = enrich(get_games(player_id, CURRENT_SEASON, "Regular Season"))
preseason = enrich(get_games(player_id, CURRENT_SEASON, "Pre Season"))
previous = enrich(get_games(player_id, PREVIOUS_SEASON, "Regular Season"))

# Combine & blend based on weights
frames = []
if not regular.empty:
    regular["weight"] = 0.6
    frames.append(regular)
if not preseason.empty:
    preseason["weight"] = 0.25
    frames.append(preseason)
if not previous.empty:
    previous["weight"] = 0.15
    frames.append(previous)

if not frames:
    st.error("No available data found for this player.")
    st.stop()

blended = pd.concat(frames, ignore_index=True)
blended = blended.sort_values("GAME_DATE")

# ---------------------- NEXT GAME INFO ----------------------
def get_next_game_info(pid):
    try:
        url = f"https://site.web.api.espn.com/apis/site/v2/sports/basketball/nba/players/{pid}"
        r = requests.get(url, timeout=10)
        data = r.json().get("team", {})
        team = data.get("abbreviation", "")
        return team
    except:
        return None

# ---------------------- PLAYER HEADER ----------------------
photo = get_player_photo(player_id)
col1, col2 = st.columns([1, 3])
with col1:
    if photo:
        st.image(photo, width=180)
with col2:
    st.markdown(f"## **{player_name}**")

# ---------------------- PREDICTION CALCULATION ----------------------
if mode == "🧠 AI Predictions":
    st.markdown("### 🧮 AI Projected Next Game Stats")

    stats = ["PTS", "REB", "AST", "FG3M", "STL", "BLK", "TOV", "PRA", "P+R", "P+A", "R+A"]
    predictions = {}
    for stat in stats:
        valid = blended[stat].dropna()
        predictions[stat] = predict_next(valid)

    # Display metrics
    cols = st.columns(4)
    for i, (key, val) in enumerate(predictions.items()):
        with cols[i % 4]:
            st.markdown(
                f"""
                <div class='card'>
                    <div style='font-size:22px;margin-bottom:5px;'>{key}</div>
                    <div style='font-size:32px;margin-top:5px;'>{val}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # Save projections
    if st.button("💾 Save Projection"):
        df_save = pd.DataFrame([{
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "player": player_name,
            **predictions,
            "status": "upcoming"
        }])
        path = "saved_projections.csv"
        if os.path.exists(path):
            existing = pd.read_csv(path)
            df_save = pd.concat([existing, df_save], ignore_index=True)
        df_save.to_csv(path, index=False)
        st.success("✅ Projection saved to Upcoming Projections")

# ---------------------- HISTORICAL TREND MODE ----------------------
elif mode == "📈 Historical Trends":
    st.markdown("### 📊 Player Performance Over Time")

    metric = st.selectbox("Select Stat:", ["PTS", "REB", "AST", "PRA", "FG3M"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=blended["GAME_DATE"],
        y=blended[metric],
        mode="lines+markers",
        name=metric,
        line=dict(width=2)
    ))
    fig.update_layout(
        template="plotly_dark",
        title=f"{player_name} — {metric} Over Time",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------------- HISTORICAL EXPANDER ----------------------
with st.expander("📜 View Historical Performance Averages"):
    recent = blended.tail(10).mean(numeric_only=True).round(1)
    st.metric("Last 10 Avg PTS", recent["PTS"])
    st.metric("Last 10 Avg REB", recent["REB"])
    st.metric("Last 10 Avg AST", recent["AST"])
