"""Transfer suggestion logic for FPL squad swaps."""

from __future__ import annotations
from typing import Iterable, Dict, List
from collections import defaultdict


def rank_transfers(
    current_squad: Iterable[Dict],
    candidates: Iterable[Dict],
    top_n: int = 5
) -> List[Dict]:
    """Return top N transfer suggestions based on predicted point differences.

    Parameters
    ----------
    current_squad : iterable of dicts
        Each dict must have keys: ``id``, ``name``, ``position``, ``predicted_points``.
    candidates : iterable of dicts
        Each dict must have keys: ``id``, ``name``, ``position``, ``predicted_points``.
    top_n : int, optional
        Maximum number of suggestions to return (default is 5).

    Returns
    -------
    List of dicts with keys:
        - out_id: ID of the player to transfer out
        - out_name: Name of the player to transfer out
        - in_id: ID of the player to transfer in
        - in_name: Name of the player to transfer in
        - position: Positional group (e.g., "GK", "DEF", "MID", "FWD")
        - predicted_out: Predicted points for the outgoing player
        - predicted_in: Predicted points for the incoming player
        - delta_pts: predicted_in - predicted_out
    """
    # Organize players by position
    curr_by_pos = defaultdict(list)
    cand_by_pos = defaultdict(list)
    for p in current_squad:
        curr_by_pos[p["position"]].append(p)
    for p in candidates:
        cand_by_pos[p["position"]].append(p)

    suggestions: List[Dict] = []
    # For each position, pair weakest current with strongest candidates
    for position, outs in curr_by_pos.items():
        ins = cand_by_pos.get(position, [])
        if not ins or not outs:
            continue
        # Sort outgoing players by ascending predicted points
        outs_sorted = sorted(outs, key=lambda x: x["predicted_points"])
        # Sort candidates by descending predicted points
        ins_sorted = sorted(ins, key=lambda x: x["predicted_points"], reverse=True)
        # Pair one-to-one
        for out_player, in_player in zip(outs_sorted, ins_sorted):
            delta = in_player["predicted_points"] - out_player["predicted_points"]
            suggestions.append({
                "out_id": out_player["id"],
                "out_name": out_player["name"],
                "in_id": in_player["id"],
                "in_name": in_player["name"],
                "position": position,
                "predicted_out": out_player["predicted_points"],
                "predicted_in": in_player["predicted_points"],
                "delta_pts": delta,
            })

    # Return top-N by delta
    suggestions_sorted = sorted(suggestions, key=lambda x: x["delta_pts"], reverse=True)
    return suggestions_sorted[:top_n]
