"""Utilities for loading and using the pre-trained Ridge AR model."""

from __future__ import annotations

import logging
from pathlib import Path

import joblib
import numpy as np


class RidgeARModel:
    """Wrapper around a pre-trained Ridge regression model or placeholder stub."""

    def __init__(self, model_path: str | None = None) -> None:
        if model_path is None:
            model_path = Path(__file__).with_name("ridge_ar_model.joblib")
        try:
            self.model = joblib.load(model_path)
        except (FileNotFoundError, Exception):
            logging.warning(
                f"Model file not found at '{model_path}'. Using placeholder model."
            )
            self.model = None

    def predict_future_points(self, features: np.ndarray) -> np.ndarray:
        """Predict future points for provided feature matrix.

        If model is missing, returns zeros for all samples.
        """
        features = np.asarray(features)
        if features.ndim != 2:
            raise ValueError("features must be a 2D array")
        if self.model is None:
            return np.zeros(features.shape[0], dtype=float)
        return self.model.predict(features)
