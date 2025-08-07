import streamlit as st
import pandas as pd
from api_client import FPLClient
from model import RidgeARModel
from suggestions import rank_transfers

# === Sidebar ===

st.set_page_config(page_title="FPL Helper", layout="wide")
with st.sidebar:
    st.image(
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQBjyJ7uEgj4l3N3J7phe9ArC02V8eLLOZXJ7a6dcNELK6-700CQxIac_0ndCvnokwDO-I&usqp=CAU",
        width=100
    )
    st.header("Squad Settings")
    team_id = st.number_input("Team ID", min_value=1, value=1)
    top_n = st.number_input("Top N suggestions", min_value=1, max_value=10, value=5)
    run_btn = st.button("Fetch Data")

# Rest of the app.py remains the same

# === Main ===
if run_btn:
    client = FPLClient()
    model = RidgeARModel()

    try:
        all_players = client.get_all_players()
        if all_players:
            squad = client.get_team(team_id)
            if squad:
                df_squad = pd.DataFrame(squad)
                st.subheader(f"Current Squad ({len(df_squad)} players)")
                st.dataframe(df_squad, use_container_width=True)

                for p in squad:
                    p["predicted_points"] = 0.0
                for p in all_players:
                    p["predicted_points"] = 0.0

                suggestions = rank_transfers(squad, all_players, top_n=top_n)
                if suggestions:
                    df_sugg = pd.DataFrame(suggestions)
                    st.subheader("Suggested Transfers")
                    st.dataframe(df_sugg, use_container_width=True)
                else:
                    st.info("No suggestions available.")
            else:
                st.error(f"Failed to fetch team {team_id}")
        else:
            st.error("Failed to fetch player data")

    except Exception as e:
        st.error(f"Error fetching data: {e}")
else:
    st.title("Fantasy Premier League Helper")
    st.write("Enter your Team ID and click 'Fetch Data' to start.")