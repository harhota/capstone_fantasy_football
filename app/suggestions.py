# app/suggestions.py
"""Transfer suggestion and analysis logic for GW5 demo, with manual override support."""

from __future__ import annotations
from typing import Iterable, Dict, List, Tuple, Optional
from collections import defaultdict
import os
import json
import pandas as pd
import random
import streamlit as st

# Paths (relative to this file)
GW_JSON     = os.path.join(os.path.dirname(__file__), '..', 'manager_data_each_gw_24_25.json')
PLAYERS_CSV = os.path.join(os.path.dirname(__file__), '..', 'data', 'players_id_2024_2025.csv')
TARGET_GW   = 5


def generate_future_predictions(player_id: int) -> Dict[str, float]:
    """Generate placeholder predictions for the three GWs after TARGET_GW."""
    preds = {
        f'GW{TARGET_GW+1}': round(random.triangular(4, 13, 6), 2),
        f'GW{TARGET_GW+2}': round(random.triangular(4, 13, 6), 2),
        f'GW{TARGET_GW+3}': round(random.triangular(4, 13, 6), 2),
    }
    preds['total'] = round(sum(preds.values()), 2)
    return preds


def load_gw_data(
    picks_override: Optional[List[Dict]] = None
) -> Tuple[List[Dict], Dict[int, str], Dict[int, str]]:
    """Load picks for TARGET_GW (or override) and player mappings."""
    # Load the master player list
    df = pd.read_csv(PLAYERS_CSV)
    name_map = df.set_index('id')['fpl_Player'].to_dict()
    pos_map  = df.set_index('id')['Position'].to_dict()

    # If override provided, use it
    if picks_override is not None:
        st.info(f"🔄 Using manual override: {len(picks_override)} picks")
        picks = picks_override
    else:
        # Load and filter JSON for TARGET_GW
        data = json.load(open(GW_JSON, 'r', encoding='utf-8'))
        if isinstance(data, list):
            entry = next((d for d in data
                          if d.get('entry_history', {}).get('event') == TARGET_GW),
                         None)
        else:
            entry = data if data.get('entry_history', {}).get('event') == TARGET_GW else None
        picks = entry.get('picks', []) if entry else []
        st.write(f"🔍 Found {len(picks)} picks for GW{TARGET_GW}")
        if not picks:
            st.warning(f"No GW{TARGET_GW} data in JSON; switch to Manual entry if needed.")

    return picks, name_map, pos_map


def rank_transfers(
    current_squad: Iterable[Dict],
    candidates: Iterable[Dict],
    top_n: int = 5
) -> List[Dict]:
    """Pair weakest current vs strongest candidates by position; return top N."""
    curr_by_pos = defaultdict(list)
    cand_by_pos = defaultdict(list)

    for p in current_squad:
        curr_by_pos[p['position']].append(p)
    for p in candidates:
        cand_by_pos[p['position']].append(p)

    suggestions: List[Dict] = []
    for position, outs in curr_by_pos.items():
        ins = cand_by_pos.get(position, [])
        if not outs or not ins:
            continue

        outs_sorted = sorted(outs, key=lambda x: x['predicted_points'])
        ins_sorted = sorted(ins, key=lambda x: x['predicted_points'], reverse=True)

        for out_p, in_p in zip(outs_sorted, ins_sorted):
            delta = in_p['predicted_points'] - out_p['predicted_points']
            suggestions.append({
                'out_id': out_p['id'],
                'out_name': out_p['name'],
                'in_id': in_p['id'],
                'in_name': in_p['name'],
                'position': position,
                'predicted_out': round(out_p['predicted_points'], 2),
                'predicted_in': round(in_p['predicted_points'], 2),
                'delta_pts': round(delta, 2)
            })

    return sorted(suggestions, key=lambda x: x['delta_pts'], reverse=True)[:top_n]


def analyze_gw_data(
    picks_override: Optional[List[Dict]] = None
) -> Tuple[List[Dict], List[Dict]]:
    """Load (or override) picks, generate predictions, and rank transfers."""
    picks, name_map, pos_map = load_gw_data(picks_override)
    squad_ids = [p['element'] for p in picks]

    # Build the current squad list
    current_squad: List[Dict] = []
    for pick in picks:
        pid = pick['element']
        if pid in name_map:
            preds = generate_future_predictions(pid)
            current_squad.append({
                'id': pid,
                'name': name_map[pid],
                'position': pos_map.get(pid, ''),
                'predicted_points': preds['total'],
                'predictions': preds,
                'is_captain': pick.get('is_captain', False)
            })

    # Build the candidate pool
    candidates: List[Dict] = []
    for pid, pname in name_map.items():
        if pid not in squad_ids:
            preds = generate_future_predictions(pid)
            candidates.append({
                'id': pid,
                'name': pname,
                'position': pos_map.get(pid, ''),
                'predicted_points': preds['total'],
                'predictions': preds
            })

    suggestions = rank_transfers(current_squad, candidates)
    return current_squad, suggestions


def show_analysis(picks_override: Optional[List[Dict]] = None) -> None:
    st.header(f'GW{TARGET_GW} Squad & Transfer Suggestions')
    squad, suggestions = analyze_gw_data(picks_override)

    # If squad is empty, bail out immediately
    if not squad:
        st.error("No squad data available. Check your picks override or JSON.")
        return

    # Build DataFrame with explicit column names
    squad_df = pd.DataFrame([{
        'Player': p['name'],
        'Position': p['position'],
        'Predicted Points': p['predicted_points'],
        'Captain': '©' if p['is_captain'] else ''
    } for p in squad])

    # Now it's safe to style
    min_pts = squad_df['Predicted Points'].min()
    max_pts = squad_df['Predicted Points'].max()
    squad_styled = (
        squad_df
        .style
        .background_gradient(
            subset=['Predicted Points'],
            cmap='RdYlGn',
            vmin=min_pts,
            vmax=max_pts
        )
        .format({'Predicted Points': '{:.2f}'})
    )

    st.subheader(f'Current Squad (GW{TARGET_GW})')
    st.dataframe(squad_styled, use_container_width=True)

    # Suggestions
    if not suggestions:
        st.warning("No transfer suggestions available.")
        return

    sugg_df = pd.DataFrame([{
        'Transfer Out': s['out_name'],
        'Transfer In': s['in_name'],
        'Position': s['position'],
        'Points Gain': s['delta_pts']
    } for s in suggestions])

    min_gain = sugg_df['Points Gain'].min()
    max_gain = sugg_df['Points Gain'].max()
    sugg_styled = (
        sugg_df
        .style
        .background_gradient(
            subset=['Points Gain'],
            cmap='RdYlGn',
            vmin=min_gain,
            vmax=max_gain
        )
        .format({'Points Gain': '{:.2f}'})
    )

    st.subheader(f'Top Transfer Suggestions (GW{TARGET_GW} → GW{TARGET_GW+1}-{TARGET_GW+3})')
    st.dataframe(sugg_styled, use_container_width=True)





# If run directly, show analysis without override
if __name__ == '__main__':
    show_analysis()
