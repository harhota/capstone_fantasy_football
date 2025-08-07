"""FPL API client for fetching team and player data."""
from __future__ import annotations

import requests
import logging
from typing import List, Dict


class FPLClient:
    """Client to interact with the Fantasy Premier League API."""
    BASE_URL = "https://fantasy.premierleague.com/api"

    def __init__(self) -> None:
        self.session = requests.Session()

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
        """Fetch a user's current team by ID."""
        url = f"{self.BASE_URL}/my-team/{team_id}/"
        try:
            res = self.session.get(url)
            res.raise_for_status()
            data = res.json()
            picks = data.get("picks", [])
            normalized = []
            for pick in picks:
                element = pick.get("element")
                # Additional fetch to get player details could be done here
                normalized.append({
                    "id": element,
                    "name": data.get("players", []).get(str(element), {}).get("web_name", ""),
                    "position": "",  # placeholder, fill from bootstrap data
                    "cost": pick.get("selling_price", 0) / 10.0,
                })
            return normalized
        except Exception as e:
            logging.error(f"Error fetching team {team_id}: {e}")
            return []

    def _element_type(self, et_id: int) -> str:
        """Map element_type ID to position string."""
        mapping = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}
        return mapping.get(et_id, "")
