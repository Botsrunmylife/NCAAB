import pandas as pd

games = pd.read_csv("season_games.csv")
teams = pd.read_csv("model_teams.csv")["team"].astype(str).str.strip()
teamset = set(teams)

mask = games["team_a"].astype(str).str.strip().isin(teamset) & games["team_b"].astype(str).str.strip().isin(teamset)

games_in = games[mask].copy()
games_out = games[~mask].copy()

games_in.to_csv("season_games_model_only.csv", index=False)
games_out.to_csv("games_not_in_model.csv", index=False)

print("Kept:", len(games_in))
print("Dropped:", len(games_out))