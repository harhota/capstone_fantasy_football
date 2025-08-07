"""Streamlit application for FPL suggestions."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from .api_client import FPLClient
from .model import RidgeARModel
from .suggestions import rank_transfers


def main() -> None:
    st.title("Fantasy Premier League Helper")

    client = FPLClient()
    data = client.get_bootstrap_static()
    players = pd.DataFrame(data["elements"])

    st.sidebar.header("Squad Settings")
    max_value = st.sidebar.number_input("Max squad value", value=100.0)

    st.subheader("Current Squad (first 15 players)")
    squad = players.head(15)[["id", "web_name", "team", "now_cost"]]
    st.dataframe(squad)

    st.subheader("Transfer Suggestions")
    model = RidgeARModel()
    candidates = []
    for _, row in players.head(30).iterrows():
        features = [[row["now_cost"] / 10, row["value_form"]]]
        predicted = model.predict_future_points(features)[0]
        candidates.append(
            {
                "id": row["id"],
                "team": row["team"],
                "cost": row["now_cost"] / 10,
                "predicted_points": float(predicted),
            }
        )

    suggestions = rank_transfers([], candidates, max_value)
    if suggestions:
        st.dataframe(pd.DataFrame(suggestions))
        csv = pd.DataFrame(suggestions).to_csv(index=False).encode("utf-8")
        st.sidebar.download_button("Download CSV", csv, "suggestions.csv", "text/csv")
    else:
        st.write("No valid suggestions under the current constraints")


if __name__ == "__main__":
    main()