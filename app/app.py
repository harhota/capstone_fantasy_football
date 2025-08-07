# app/app.py
import streamlit as st
import pandas as pd
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from suggestions import analyze_gw_data, show_analysis
# ...

# === Page Config ===
st.set_page_config(
    page_title="FPL Helper Demo",
    page_icon="⚽",
    layout="wide"
)

# === Sidebar ===
with st.sidebar:
    st.image(
        "https://www.merlinpcbgroup.com/wp-content/uploads/fpl-logo.jpg",
        width=200
    )
    st.header("Demo Settings")
    mode = st.radio("Load squad via", ["JSON (GW5)", "Manual entry"])
    manual_ids = ""
    if mode == "Manual entry":
        manual_ids = st.text_area(
            "Paste your 15 player IDs (comma-separated)",
            placeholder="e.g. 201,333,422,..."
        )
    top_n = st.number_input("Top N suggestions", min_value=1, max_value=10, value=5)
    run_btn = st.button("Show Analysis")

# === Main ===
if run_btn:
    if mode == "Manual entry":
        try:
            ids = [int(x.strip()) for x in manual_ids.split(",") if x.strip()]
            picks_override = [{"element": pid, "is_captain": False} for pid in ids]
        except ValueError:
            st.error("Invalid IDs; please enter integers separated by commas.")
            st.stop()
      # Pass only picks_override into show_analysis
        show_analysis(picks_override=picks_override)
    else:
        # JSON mode (GW5)
        show_analysis()

else:
    st.title("Fantasy Premier League Helper Demo")
    st.write("Select load mode and click 'Show Analysis' in the sidebar.")
