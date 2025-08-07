import logging
import os
import pandas as pd
from api_client import FPLClient

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_api():
    client = FPLClient()
    logging.info("Testing FPL API access...")

    # Test getting all players
    try:
        players = client.get_all_players()
        logging.info(f"Fetched {len(players)} players")
        logging.debug(f"Sample player data: {players[0]}")
    except Exception as e:
        logging.error(f"Error fetching players: {e}")
        return

    # Test getting specific player details
    try:
        player_id = players[0]['id']
        logging.info(f"Fetching details for player {player_id}")
        details = client.get_player_details(player_id)
        logging.debug(f"Player details: {details}")
    except Exception as e:
        logging.error(f"Error fetching player details: {e}")

    # Test getting fixtures
    try:
        fixtures = client.get_fixtures()
        logging.info(f"Fetched {len(fixtures)} fixtures")
        logging.debug(f"Sample fixture: {fixtures[0]}")
    except Exception as e:
        logging.error(f"Error fetching fixtures: {e}")

def fetch_and_save_players():
    client = FPLClient()
    logging.info("Fetching all players...")

    try:
        # Get bootstrap-static data
        url = f"{client.BASE_URL}/bootstrap-static/"
        res = client.session.get(url)
        res.raise_for_status()
        data = res.json()
        players = data.get("elements", [])

        # Convert to DataFrame
        df = pd.DataFrame(players)

        # Select columns and create a new DataFrame (instead of a view)
        columns = [
            'id', 'web_name', 'first_name', 'second_name', 'element_type',
            'team', 'now_cost', 'form', 'total_points', 'minutes',
            'goals_scored', 'assists', 'clean_sheets', 'saves',
            'selected_by_percent', 'influence', 'creativity', 'threat'
        ]
        df_filtered = df[columns].copy()  # Create explicit copy

        # Add new columns using loc
        position_map = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}
        df_filtered.loc[:, 'position'] = df_filtered['element_type'].map(position_map)
        df_filtered.loc[:, 'cost'] = df_filtered['now_cost'] / 10.0

        # Save to CSV
        output_file = 'fpl_players_data.csv'
        df_filtered.to_csv(output_file, index=False)
        logging.info(f"Saved {len(df_filtered)} players to '{output_file}'")
        logging.debug(f"\nFirst few players:\n{df_filtered.head()}")

    except Exception as e:
        logging.error(f"Error saving player data: {e}")

if __name__ == "__main__":
    logging.info("Starting data fetch...")
    test_api()
    fetch_and_save_players()