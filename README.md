# 🧠 Fantasy Football Points Prediction

> A machine learning-based system to forecast [Fantasy Premier League (FPL)](https://fantasy.premierleague.com/)
 player points and optimize team selection decisions.

🎓 **Master's thesis /  capstone project**

---

## Project Overview

This project aims to predict FPL player points for upcoming gameweeks using multiple machine learning approaches. It integrates player statistics, form tracking, fixture difficulty, and ensemble modeling to support smarter decisions for fantasy managers.

Key outcomes include:
- Accurate **player points forecasts**
- Rolling **form-based features**
- A **Streamlit app** for team optimization and transfer suggestions

---

## Problem Statement

FPL managers must make weekly choices (transfers, captaincy, bench order) with uncertain outcomes. This project uses historical data and ML techniques to build a predictive model for fantasy points and deploys an interactive assistant to improve weekly decision-making.

---

## Dataset

- Source: Internal dataset `dataset_ver3.2.5.csv` (derived from `fbref.com` mainly)
- Structure: ~80,000 rows, each = one player per gameweek
- Includes:
  - Performance stats (xG, goals, assists, bonus, etc.)
  - Contextual features (team, opposition, home/away)
  - Aggregates (last `n` gameweeks, opponent xG, etc.)

> Note: Dataset is private. If needed, please request supervisor access.

---

## 🛠 Methods

### Baseline
- Linear Regression using simple past-performance features (`GlsPrev`, `Min`, `CSPrev`, etc.)

### Approach 1: Moving Average Features
- Rolling window (e.g. GWs 1–5 → predict GW 6)
- Aggregates: average xG, assists, points, etc.

### Approach 2: Ensemble Model
- VotingRegressor (Linear + LightGBM + MLP)
- Uses full feature set without aggregation

### Optional: Time-Series Modeling
- LSTM 

---

## Evaluation

- **Test window**: Gameweeks 31–38
- **Metrics**:
  - MAE (Mean Absolute Error)
  - RMSE
  - R² Score (optional)
  - Top-N prediction accuracy (e.g. top 5 point scorers)

## Time-Series Modeling & Evaluation 

Time-series models like LSTM or Temporal Convolutional Networks (TCNs) require sequential inputs and cannot rely on shuffled rows or arbitrary gameweek splits. Their evaluation logic differs from traditional ML models.

### Key Constraints

- Must respect temporal ordering (no mixing GWs)
- Needs fixed-length input sequences (e.g., last 5 GWs per player)
- Each player’s history must be complete and continuous


| Phase       | Gameweeks Used                  | Description                                   |
|------------|----------------------------------|-----------------------------------------------|
| Training    | GWs 6–25 (with lookback from GW 1) | Sliding sequences per player (e.g., GWs 1–5 → GW 6) |
| Validation  | GWs 26–30                        | Used for hyperparameter tuning and early stopping |
| Testing     | GWs 31–38                        | Final evaluation of model performance         |

Each player sequence might look like:[ GW_26, GW_27, GW_28, GW_29, GW_30 ] → Predict GW_31
---

## 🧱 Project Structure


---

## Streamlit App (hopefully)

- Upload team or use demo mode
- View player projections for next 4 GWs
- See recommended transfers and captain picks
- Visual insights: projected points, top performers, fixture difficulty

---

## References

- [Sasank's FPL ML Video](https://www.youtube.com/watch?v=wcOJbDAQ-JE)
- [GavinJP’s Kaggle Notebook](https://www.kaggle.com/code/gavinjpng/fpl-prediction-and-selection/notebook)
- [Vaastav’s FPL GitHub](https://github.com/vaastav/Fantasy-Premier-League)

---

## Licensing & Access

This project is for academic use. Please request permission before using the dataset or internal model code.

---


