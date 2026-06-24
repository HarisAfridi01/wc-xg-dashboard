# FIFA World Cup 2026 — Goals Dashboard

I built this during the World Cup because I wanted to actually see the data behind what was happening in the tournament, not just check scores. Started as a quick weekend project, ended up being a full dashboard with live API data, interactive charts, and real group standings.

It pulls match results directly from football-data.org every 5 minutes so it stays current throughout the tournament. No static CSVs, no manual updates.

---

## What it does

The main question I was trying to answer: which teams are actually good, and which ones are just running hot? The goals scored vs conceded scatter plot makes that pretty obvious at a glance — you can immediately see who's dominant on both ends versus who's squeaking through.

Beyond that:

- Live goals breakdown by team ranked by total scored
- Attack vs defense scatter plot with goals per game as color scale  
- Team inspector — pick any team and see their full match history and stats
- Group standings with the top 2 qualifier spots highlighted
- Refreshes every 5 minutes automatically

---

## Stack

Python, Streamlit, Pandas, Plotly, football-data.org API. Nothing exotic — kept it simple on purpose since the goal was to ship something real, not over-engineer it.

---

## Running it locally

You'll need a free API key from [football-data.org](https://www.football-data.org) first.

```bash
git clone https://github.com/HarisAfridi01/wc-xg-dashboard.git
cd wc-xg-dashboard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the root: