import streamlit as st
import pandas as pd
import requests
from PIL import Image

from api_client import FPLClient
from model import RidgeARModel
from suggestions import rank_transfers

# === Sidebar ===
st.set_page_config(page_title="FPL Helper", layout="wide")
with st.sidebar:
    # 1) FPL icon at top
    st.image(
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQBjyJ7uEgj4l3N3J7phe9ArC02V8eLLOZXJ7a6dcNELK6-700CQxIac_0ndCvnokwDO-I&usqp=CAU", width=100
    )
    st.header("Squad Settings")
    team_id = st.text_input("Enter your FPL Team ID:", value="", help="Numeric team ID from FPL API.")
    top_n = st.number_input("Top N suggestions", min_value=1, max_value=10, value=5)
    run_btn = st.button("Fetch and Suggest")

# === Main ===
if run_btn and team_id.isdigit():
    # Initialize
    client = FPLClient()
    model = RidgeARModel()
    
    # Fetch current squad
    try:
        squad = client.get_team(int(team_id))  # returns list of dicts with id,name,position,cost
        df_squad = pd.DataFrame(squad)
        st.subheader(f"Current Squad ({len(df_squad)} players)")
        # 2) Fit table width
        st.dataframe(df_squad, use_container_width=True)

        # Build feature matrix for squad and all players
        all_players = client.get_all_players()  # list of dicts
        # Prepare features for prediction (stub or real)
        # For demo, placeholders: predicted_points = model.predict_future_points(...)
        for p in squad:
            p["predicted_points"] = 0.0  # replace with model.predict_future_points
        for p in all_players:
            p["predicted_points"] = 0.0

        # 3) Generate suggestions and display
        suggestions = rank_transfers(squad, all_players, top_n=top_n)
        if suggestions:
            df_sugg = pd.DataFrame(suggestions)
            st.subheader("Suggested Transfers")
            st.dataframe(df_sugg, use_container_width=True)
        else:
            st.info("No suggestions available.")

    except Exception as e:
        st.error(f"Error fetching data: {e}")
else:
    st.title("Fantasy Premier League Helper")
    st.write("Please enter your Team ID in the sidebar and click 'Fetch and Suggest'.")
