"""Transfer suggestions logic"""

from __future__ import annotations

from collections import Counter
from typing import Iterable


def rank_transfers(
    current_squad: Iterable[dict],
    candidates: Iterable[dict],
    max_squad_value: float,
    max_per_team: int = 3,
) -> list[dict]:
    """Return ranked transfer candidates respecting squad constraints.

    Parameters
    ----------
    current_squad: iterable of player dicts
        Each dict requires ``team`` and ``cost`` keys.
    candidates: iterable of player dicts
        Each dict requires ``team``, ``cost`` and ``predicted_points`` keys.
    max_squad_value: float
        Maximum total cost allowed for the squad once the player is added.
    max_per_team: int, default 3
        Maximum number of players from the same team.
    """
    current_list = list(current_squad)
    candidates_list = list(candidates)
    current_value = sum(p["cost"] for p in current_list)
    team_counts = Counter(p["team"] for p in current_list)

    valid: list[dict] = []
    for player in candidates_list:
        if current_value + player["cost"] > max_squad_value:
            continue
        if team_counts[player["team"]] + 1 > max_per_team:
            continue
        valid.append(player)

    valid.sort(key=lambda p: p["predicted_points"], reverse=True)
    return valid