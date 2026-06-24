import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")

st.set_page_config(
    page_title="WC 2026 xG Dashboard",
    layout="wide"
)

import base64

def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

img = get_base64_image("assets/banner.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;600&display=swap');
    
    .banner {{
        background-image: url("data:image/png;base64,{img}");
        background-size: cover;
        background-position: center;
        height: 320px;
        border-radius: 16px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }}
    .banner::before {{
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(to bottom, rgba(0,0,0,0.15), rgba(0,0,0,0.6));
        border-radius: 16px;
    }}
    .banner-content {{
        position: relative;
        text-align: center;
        z-index: 1;
    }}
    .banner-content h1 {{
        font-family: 'Bebas Neue', sans-serif;
        color: white;
        font-size: 5rem;
        letter-spacing: 4px;
        margin: 0;
        line-height: 1;
        text-shadow: 0px 4px 12px rgba(0,0,0,0.5);
    }}
    .banner-content p {{
        font-family: 'Inter', sans-serif;
        color: rgba(255,255,255,0.9);
        font-size: 1rem;
        font-weight: 600;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin: 10px 0 0 0;
        text-shadow: 0px 2px 6px rgba(0,0,0,0.5);
    }}
    .banner-content .live-badge {{
        display: inline-block;
        background: #e63946;
        color: white;
        font-family: 'Inter', sans-serif;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 2px;
        padding: 3px 10px;
        border-radius: 20px;
        margin-top: 12px;
        text-transform: uppercase;
    }}
    </style>
    <div class="banner">
        <div class="banner-content">
            <h1>FIFA WORLD CUP 2026</h1>
            <p>Goals Analysis Dashboard</p>
            <span class="live-badge">⚡ Live Data</span>
        </div>
    </div>
""", unsafe_allow_html=True)
@st.cache_data(ttl=300)
def get_matches():
    url = "https://api.football-data.org/v4/competitions/WC/matches"
    headers = {"X-Auth-Token": API_KEY}
    response = requests.get(url, headers=headers)
    return response.json()

with st.spinner("Fetching live match data..."):
    data = get_matches()

if "matches" not in data:
    st.error("Could not fetch data. Check your API key in the .env file.")
    st.stop()

matches = data["matches"]
finished = [m for m in matches if m["status"] == "FINISHED"]

rows = []
for m in finished:
    rows.append({
        "Home": m["homeTeam"]["name"],
        "Away": m["awayTeam"]["name"],
        "Home Goals": m["score"]["fullTime"]["home"],
        "Away Goals": m["score"]["fullTime"]["away"],
        "Date": m["utcDate"][:10]
    })

df_matches = pd.DataFrame(rows)

# Build team goals table
teams = {}
for _, row in df_matches.iterrows():
    for team, goals, conceded in [
        (row["Home"], row["Home Goals"], row["Away Goals"]),
        (row["Away"], row["Away Goals"], row["Home Goals"])
    ]:
        if team not in teams:
            teams[team] = {"Goals Scored": 0, "Goals Conceded": 0, "Games": 0}
        teams[team]["Goals Scored"] += goals
        teams[team]["Goals Conceded"] += conceded
        teams[team]["Games"] += 1

df_teams = pd.DataFrame(teams).T.reset_index()
df_teams.columns = ["Team", "Goals Scored", "Goals Conceded", "Games"]
df_teams["Goals Per Game"] = (df_teams["Goals Scored"] / df_teams["Games"]).round(2)
df_teams = df_teams.sort_values("Goals Scored", ascending=False)

# Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Matches Played", len(df_matches))
col2.metric("Top Scorer", df_teams.iloc[0]["Team"])
col3.metric("Total Goals", int(df_teams["Goals Scored"].sum()))

st.divider()

# --- Team Filter ---
st.subheader("Filter by Team")
all_teams = sorted(df_teams["Team"].tolist())
selected_team = st.selectbox("Select a team to inspect", ["All Teams"] + all_teams)

if selected_team != "All Teams":
    team_matches = df_matches[
        (df_matches["Home"] == selected_team) | (df_matches["Away"] == selected_team)
    ]
    team_stats = df_teams[df_teams["Team"] == selected_team].iloc[0]
    
    st.markdown(f"### {selected_team} — Match History")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Games Played", int(team_stats["Games"]))
    col2.metric("Goals Scored", int(team_stats["Goals Scored"]))
    col3.metric("Goals Conceded", int(team_stats["Goals Conceded"]))
    col4.metric("Goals Per Game", team_stats["Goals Per Game"])
    
    st.dataframe(team_matches, use_container_width=True)

# Bar chart
st.subheader("Goals Scored by Team")
fig1 = px.bar(
    df_teams.head(20),
    x="Team", y="Goals Scored",
    color="Goals Scored",
    color_continuous_scale="reds"
)
fig1.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig1, use_container_width=True)

# Goals scored vs conceded
st.subheader("Goals Scored vs Conceded")
fig2 = px.scatter(
    df_teams,
    x="Goals Conceded", y="Goals Scored",
    text="Team", size="Games",
    color="Goals Per Game",
    color_continuous_scale="greens"
)
fig2.update_traces(textposition="top center")
st.plotly_chart(fig2, use_container_width=True)
# --- Group Standings ---
st.divider()
st.subheader("📊 Group Stage Standings")

@st.cache_data(ttl=300)
def get_standings():
    url = "https://api.football-data.org/v4/competitions/WC/standings"
    headers = {"X-Auth-Token": API_KEY}
    response = requests.get(url, headers=headers)
    return response.json()

standings_data = get_standings()

if "standings" in standings_data:
    groups = standings_data["standings"]
    
    # Let user pick a group
    group_names = [g["group"] for g in groups]
    selected_group = st.selectbox("Select a group", group_names)
    
    # Find the selected group
    group = next(g for g in groups if g["group"] == selected_group)
    
    rows = []
    for team in group["table"]:
        rows.append({
            "Position": team["position"],
            "Team": team["team"]["name"],
            "Played": team["playedGames"],
            "Won": team["won"],
            "Draw": team["draw"],
            "Lost": team["lost"],
            "Goals For": team["goalsFor"],
            "Goals Against": team["goalsAgainst"],
            "Goal Diff": team["goalDifference"],
            "Points": team["points"]
        })
    
    df_standing = pd.DataFrame(rows)
    
    # Color the top 2 rows green (qualify), rest normal
    def highlight_qualifiers(row):
        if row["Position"] <= 2:
            return ["background-color: #d4edda"] * len(row)
        return [""] * len(row)
    
    st.dataframe(
        df_standing.style.apply(highlight_qualifiers, axis=1),
        use_container_width=True
    )
else:
    st.warning("Standings data not available.")

# Match results table
st.subheader("All Match Results")
st.dataframe(df_matches, use_container_width=True)