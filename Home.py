import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date
from config import init_page, render_navbar

# ==========================
#  PAGE INITIALIZATION
# ==========================
init_page("🏠 NBA AI Dashboard")
render_navbar("Home")

st.title("🏀 NBA Live Projections Dashboard")
st.markdown("### Today's Games & Injury Updates")

# ==========================
#  DATA SOURCES
# ==========================
NBA_API = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
INJURY_API = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/injuries"

# ==========================
#  FUNCTIONS
# ==========================
@st.cache_data(ttl=300)
def get_today_games():
    """Fetch today's NBA games with matchup and status."""
    try:
        resp = requests.get(NBA_API, timeout=10)
        data = resp.json()
        games = []
        for ev in data.get("events", []):
            teams = ev["competitions"][0]["competitors"]
            home = next(t for t in teams if t["homeAway"] == "home")
            away = next(t for t in teams if t["homeAway"] == "away")
            games.append({
                "home_team": home["team"]["displayName"],
                "away_team": away["team"]["displayName"],
                "home_logo": home["team"]["logo"],
                "away_logo": away["team"]["logo"],
                "status": ev["status"]["type"]["description"],
                "game_time": ev["date"],
                "id": ev["id"],
            })
        return pd.DataFrame(games)
    except Exception as e:
        st.error(f"⚠️ Failed to load games: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=600)
def get_injuries():
    """Fetch currently reported injuries."""
    try:
        resp = requests.get(INJURY_API, timeout=10)
        data = resp.json()
        injuries = []
        for team in data.get("teams", []):
            team_name = team["team"]["displayName"]
            for player in team.get("injuries", []):
                injuries.append({
                    "team": team_name,
                    "player": player["athlete"]["displayName"],
                    "status": player.get("status", "N/A"),
                    "description": player.get("description", "N/A"),
                })
        return pd.DataFrame(injuries)
    except Exception as e:
        st.error(f"⚠️ Failed to load injuries: {e}")
        return pd.DataFrame()

# ==========================
#  DISPLAY GAMES
# ==========================
games_df = get_today_games()
injuries_df = get_injuries()

if games_df.empty:
    st.warning("No games scheduled today.")
else:
    for _, g in games_df.iterrows():
        with st.container():
            st.markdown(
                f"""
                <div style="background-color:#111;padding:15px;border-radius:12px;
                            box-shadow:0 0 15px #E50914;margin-bottom:15px;">
                    <div style="display:flex;align-items:center;justify-content:space-between;">
                        <div style="text-align:center;">
                            <img src="{g['away_logo']}" width="60"><br>
                            <b>{g['away_team']}</b>
                        </div>
                        <div style="font-size:22px;font-weight:bold;color:#00FFFF;">
                            VS
                        </div>
                        <div style="text-align:center;">
                            <img src="{g['home_logo']}" width="60"><br>
                            <b>{g['home_team']}</b>
                        </div>
                    </div>
                    <div style="text-align:center;margin-top:10px;color:#AAA;">
                        🕒 {datetime.fromisoformat(g['game_time'][:-1]).strftime('%I:%M %p')} |
                        {g['status']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Inline injuries affecting this game
            affected = injuries_df[
                injuries_df["team"].isin([g["home_team"], g["away_team"]])
            ]
            if not affected.empty:
                with st.expander(f"🩹 Injuries impacting this matchup ({len(affected)})"):
                    for _, row in affected.iterrows():
                        st.markdown(
                            f"- **{row['player']}** ({row['team']}): {row['status']} — _{row['description']}_"
                        )

# Footer
st.markdown("<br><hr><center>🔁 Auto-refreshes every 5 minutes</center>", unsafe_allow_html=True)
