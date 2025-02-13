# python-ml-service/app.py

import io
import base64
import pandas as pd
import numpy as np
from scipy.stats import poisson
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import statsmodels.formula.api as smf
from flask_cors import CORS

from flask import Flask, request, jsonify

# Set seaborn style
sns.set(style="whitegrid")

app = Flask(__name__)

def read_uploaded_file(file_storage, default_encoding='ISO-8859-1'):
    """
    Helper function to read an uploaded file (CSV or XLSX) into a DataFrame.
    """
    filename = file_storage.filename.lower()
    try:
        if filename.endswith('.csv'):
            return pd.read_csv(file_storage, encoding=default_encoding)
        elif filename.endswith('.xlsx'):
            return pd.read_excel(file_storage)
        else:
            raise ValueError("Unsupported file format. Please upload CSV or XLSX.")
    except Exception as e:
        raise ValueError(f"Error reading file {filename}: {str(e)}")

@app.route('/train', methods=['POST'])
def train():
    try:
        # Expecting three files:
        # file1: historical matches (results data, CSV)
        # file2: current standings (Excel)
        # file3: remaining fixtures (Excel or CSV)
        file1 = request.files.get('file1')
        file2 = request.files.get('file2')
        file3 = request.files.get('file3')

        if not (file1 and file2 and file3):
            return jsonify({"error": "All three files (file1, file2, file3) are required."}), 400

        # Load the files into DataFrames
        matches = read_uploaded_file(file1)  # Historical match data
        standings = read_uploaded_file(file2)  # Current standings data
        fixtures = read_uploaded_file(file3)  # Remaining fixtures data

        print("Historical matches loaded:", matches.shape)
        print("Current standings loaded:", standings.shape)
        print("Remaining fixtures loaded:", fixtures.shape)

        # -------------------------------
        # Standardize team names
        # -------------------------------
        name_mapping = {
            'AFC Bournemouth': 'Bournemouth',
            # Add more mappings if needed
        }

        # Standardize names in historical matches
        matches['HomeTeam'] = matches['HomeTeam'].replace(name_mapping)
        matches['AwayTeam'] = matches['AwayTeam'].replace(name_mapping)

        # Standardize names in fixtures
        fixtures['HomeTeam'] = fixtures['HomeTeam'].replace(name_mapping)
        fixtures['AwayTeam'] = fixtures['AwayTeam'].replace(name_mapping)

        # Standardize current standings if necessary
        if 'Team' in standings.columns:
            standings['Team'] = standings['Team'].replace(name_mapping)
        else:
            return jsonify({"error": "Standings file must contain a 'Team' column."}), 400

        # -------------------------------
        # Build Poisson regression models
        # -------------------------------
        # For home goals
        formula_home = 'FTHG ~ C(HomeTeam) + C(AwayTeam)'
        poisson_model_home = smf.glm(formula=formula_home, data=matches,
                                     family=sm.families.Poisson()).fit()
        print("Home Goals Model Summary:")
        print(poisson_model_home.summary())

        # For away goals
        formula_away = 'FTAG ~ C(HomeTeam) + C(AwayTeam)'
        poisson_model_away = smf.glm(formula=formula_away, data=matches,
                                     family=sm.families.Poisson()).fit()
        print("\nAway Goals Model Summary:")
        print(poisson_model_away.summary())

        # Create a sorted list of teams used in training
        teams_train = sorted(set(matches['HomeTeam'].unique()).union(set(matches['AwayTeam'].unique())))
        print("Teams in training data:")
        print(teams_train)

        # -------------------------------
        # Define match simulation and standings update functions
        # -------------------------------
        def simulate_match_model(home_team, away_team, model_home, model_away, teams_train,
                                 league_avg_home_goals, league_avg_away_goals):
            """
            Simulate a match using Poisson regression models.
            """
            # Create a DataFrame for prediction
            new_data = pd.DataFrame({'HomeTeam': [home_team], 'AwayTeam': [away_team]})
            # Set the categorical levels to match those used in training
            new_data['HomeTeam'] = pd.Categorical(new_data['HomeTeam'], categories=teams_train)
            new_data['AwayTeam'] = pd.Categorical(new_data['AwayTeam'], categories=teams_train)

            # Predict expected goals for the home team
            try:
                lambda_home = model_home.predict(new_data)[0]
                if np.isnan(lambda_home):
                    raise ValueError
            except Exception:
                print(f"Warning: '{home_team}' not found in training data. Using league average for home goals.")
                lambda_home = league_avg_home_goals

            # Predict expected goals for the away team
            try:
                lambda_away = model_away.predict(new_data)[0]
                if np.isnan(lambda_away):
                    raise ValueError
            except Exception:
                print(f"Warning: '{away_team}' not found in training data. Using league average for away goals.")
                lambda_away = league_avg_away_goals

            # Simulate match outcome using Poisson random draws
            home_goals = poisson.rvs(mu=lambda_home)
            away_goals = poisson.rvs(mu=lambda_away)
            return home_goals, away_goals

        league_avg_home_goals = matches['FTHG'].mean()
        league_avg_away_goals = matches['FTAG'].mean()
        print("League Average Home Goals:", league_avg_home_goals)
        print("League Average Away Goals:", league_avg_away_goals)

        # Convert current standings DataFrame to a dictionary keyed by team name
        standings_dict = {}
        for _, row in standings.iterrows():
            team = row['Team']
            standings_dict[team] = {
                'P': int(row['P']),
                'W': int(row['W']),
                'D': int(row['D']),
                'L': int(row['L']),
                'F': int(row['F']),
                'A': int(row['A']),
                'GD': int(row['GD']),
                'Points': int(row['Points'])
            }

        def update_standings(standings_dict, home_team, away_team, home_goals, away_goals):
            """
            Update the standings dictionary with the result of one match.
            """
            standings_dict[home_team]['P'] += 1
            standings_dict[away_team]['P'] += 1

            standings_dict[home_team]['F'] += home_goals
            standings_dict[home_team]['A'] += away_goals
            standings_dict[away_team]['F'] += away_goals
            standings_dict[away_team]['A'] += home_goals

            standings_dict[home_team]['GD'] = standings_dict[home_team]['F'] - standings_dict[home_team]['A']
            standings_dict[away_team]['GD'] = standings_dict[away_team]['F'] - standings_dict[away_team]['A']

            if home_goals > away_goals:
                standings_dict[home_team]['W'] += 1
                standings_dict[away_team]['L'] += 1
                standings_dict[home_team]['Points'] += 3
            elif home_goals < away_goals:
                standings_dict[away_team]['W'] += 1
                standings_dict[home_team]['L'] += 1
                standings_dict[away_team]['Points'] += 3
            else:
                standings_dict[home_team]['D'] += 1
                standings_dict[away_team]['D'] += 1
                standings_dict[home_team]['Points'] += 1
                standings_dict[away_team]['Points'] += 1

            return standings_dict

        # -------------------------------
        # Simulate the remaining fixtures
        # -------------------------------
        simulation_results_model = []

        for idx, match in fixtures.iterrows():
            home_team = match['HomeTeam']
            away_team = match['AwayTeam']

            # Simulate match result
            home_goals, away_goals = simulate_match_model(
                home_team, away_team,
                poisson_model_home, poisson_model_away,
                teams_train, league_avg_home_goals, league_avg_away_goals
            )

            simulation_results_model.append({
                'HomeTeam': home_team,
                'AwayTeam': away_team,
                'HomeGoals': home_goals,
                'AwayGoals': away_goals
            })

            if home_team in standings_dict and away_team in standings_dict:
                standings_dict = update_standings(standings_dict, home_team, away_team, home_goals, away_goals)
            else:
                print(f"Warning: One of the teams ({home_team} or {away_team}) not found in standings.")

        results_df_model = pd.DataFrame(simulation_results_model)
        print("Simulated Match Results Using the Poisson Regression Model:")
        print(results_df_model)

        # Convert standings dictionary back to DataFrame and sort
        predicted_standings_model = pd.DataFrame.from_dict(standings_dict, orient='index') \
            .reset_index().rename(columns={'index': 'Team'})
        predicted_standings_model = predicted_standings_model.sort_values(
            by=['Points', 'GD', 'F'], ascending=False).reset_index(drop=True)
        predicted_standings_model.index += 1  # Ranking starts at 1
        predicted_standings_model.insert(0, 'Rank', predicted_standings_model.index)
        print("\nPredicted League Standings (Model-Based Simulation):")
        print(predicted_standings_model)

        # -------------------------------
        # Generate a plot for predicted points by team
        # -------------------------------
        plt.figure(figsize=(10, 6))
        sns.barplot(x='Points', y='Team', data=predicted_standings_model, palette='viridis')
        plt.title("Predicted League Points by Team (Using Poisson Regression Model)")
        plt.xlabel("Points")
        plt.ylabel("Team")
        plt.tight_layout()

        # Save the plot to a bytes buffer and encode as base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plot_data = "data:image/png;base64," + img_base64

        # -------------------------------
        # Build the response JSON
        # -------------------------------
        response = {
            "simulatedResults": simulation_results_model,
            "predictedStandings": predicted_standings_model.to_dict(orient='records'),
            "plot": plot_data,
            "message": "Simulation completed successfully."
        }
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the Flask service on port 5000
    app.run(host="0.0.0.0", port=5000, debug=True)
