"""FPL API client for fetching team and player data."""
from __future__ import annotations

import requests
import logging
from typing import List, Dict


class FPLClient:
    """Client to interact with the Fantasy Premier League API."""
    BASE_URL = "https://fantasy.premierleague.com/api"
    LOGIN_URL = "https://users.premierleague.com/accounts/login/"

    def __init__(self) -> None:
        self.session = requests.Session()

    def login(self, email: str, password: str) -> bool:
        """Login to FPL with credentials."""
        payload = {
            'login': email,
            'password': password,
            'redirect_uri': 'https://fantasy.premierleague.com/',
            'app': 'plfpl-web'
        }
        try:
            res = self.session.post(self.LOGIN_URL, data=payload)
            res.raise_for_status()
            return 'sessionid' in self.session.cookies
        except Exception as e:
            logging.error(f"Login failed: {e}")
            return False

    def get_all_players(self) -> List[Dict]:
        """Fetch all players from the Bootstrap static endpoint."""
        url = f"{self.BASE_URL}/bootstrap-static/"
        try:
            res = self.session.get(url)
            res.raise_for_status()
            data = res.json()
            players = data.get("elements", [])
            # Normalize to only required keys: id, name, position, now_cost
            normalized = []
            for p in players:
                normalized.append({
                    "id": p.get("id"),
                    "name": p.get("web_name"),
                    "position": self._element_type(p.get("element_type")),
                    "cost": p.get("now_cost") / 10.0,
                })
            return normalized
        except Exception as e:
            logging.error(f"Error fetching all players: {e}")
            return []

    def get_team(self, team_id: int) -> List[Dict]:
        """Fetch a user's current team using the public picks endpoint."""
        try:
            # Get current gameweek from bootstrap-static
            url = f"{self.BASE_URL}/bootstrap-static/"
            res = self.session.get(url)
            res.raise_for_status()
            static = res.json()
            current_gw = static.get("events", [{}])[0].get("id")

            # Get all players for reference
            all_players = {p["id"]: p for p in self.get_all_players()}

            # Fetch picks for current gameweek
            url = f"{self.BASE_URL}/entry/{team_id}/event/{current_gw}/picks/"
            res = self.session.get(url)
            res.raise_for_status()
            data = res.json()
            picks = data.get("picks", [])

            # Build squad list
            normalized = []
            for pick in picks:
                element_id = pick.get("element")
                player = all_players.get(element_id, {})

                normalized.append({
                    "id": element_id,
                    "name": player.get("name", "Unknown"),
                    "position": player.get("position", ""),
                    "cost": player.get("cost", 0),
                })

            return normalized

        except Exception as e:
            logging.error(f"Error fetching team {team_id}: {e}")
            return []

    def _element_type(self, et_id: int) -> str:
        """Map element_type ID to position string."""
        mapping = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}
        return mapping.get(et_id, "")

    def get_player_details(self, player_id: int) -> dict:
        """Fetch detailed stats for a specific player."""
        url = f"{self.BASE_URL}/element-summary/{player_id}/"
        try:
            res = self.session.get(url)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logging.error(f"Error fetching player details: {e}")
            return {}

    def get_fixtures(self) -> list:
        """Fetch all fixtures."""
        url = f"{self.BASE_URL}/fixtures/"
        try:
            res = self.session.get(url)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logging.error(f"Error fetching fixtures: {e}")
            return []
