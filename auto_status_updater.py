import pandas as pd
import requests
from datetime import datetime, timedelta
import os

def get_today_games():
    try:
        url = "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"
        data = requests.get(url).json()
        return data.get("scoreboard", {}).get("games", [])
    except:
        return []

def update_projection_status():
    path = "saved_projections.csv"
    if not os.path.exists(path):
        return
    df = pd.read_csv(path)
    if "status" not in df.columns:
        df["status"] = "upcoming"

    games = get_today_games()
    now = datetime.utcnow()

    for g in games:
        home = g["homeTeam"]["teamTricode"]
        away = g["awayTeam"]["teamTricode"]
        status_text = g.get("gameStatusText", "").lower()
        start_time = datetime.strptime(g["gameTimeUTC"], "%Y-%m-%dT%H:%M:%SZ")

        if "final" in status_text:
            new_status = "completed"
        elif start_time <= now <= start_time + timedelta(hours=3):
            new_status = "live"
        else:
            new_status = "upcoming"

        df.loc[df["opponent"] == home, "status"] = new_status
        df.loc[df["opponent"] == away, "status"] = new_status

    df.to_csv(path, index=False)
