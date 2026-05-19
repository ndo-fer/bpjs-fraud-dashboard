"""
scoring.py
----------
Modul scoring klaim untuk dashboard prioritas verifikasi.

Model winner_model.joblib dilatih dengan 10 fitur utama.
Tidak ada preprocessing terpisah — model menerima raw numeric input langsung.
"""

from __future__ import annotations

from pathlib import Path

import joblib
import streamlit as st
import pandas as pd

from utils.schema import USER_INPUT_FEATURES

MODEL_PATH = Path("models/winner_model.joblib")

# ── Threshold ────────────────────────────────────────────────────────────────
# Threshold 3-tier untuk prioritas verifikasi
THRESHOLD_HIGH   = 0.7   # High Priority
THRESHOLD_MEDIUM = 0.4   # Medium Priority


# ── Load model (di-cache agar tidak reload setiap klik) ──────────────────────
@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


# ── Assign priority label ─────────────────────────────────────────────────────
def assign_priority(score: float) -> str:
    if score >= THRESHOLD_HIGH:
        return "High Priority"
    elif score >= THRESHOLD_MEDIUM:
        return "Medium Priority"
    return "Low Priority"


# ── Fungsi scoring utama ──────────────────────────────────────────────────────
def score_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Menerima DataFrame dengan USER_INPUT_FEATURES (10 kolom),
    mengembalikan DataFrame dengan kolom tambahan:
    risk_score, risk_percent, priority.
    """
    model = load_model()

    X = df[USER_INPUT_FEATURES].copy()

    scores = model.predict_proba(X)[:, 1]

    result = df.copy()
    result["risk_score"]   = scores
    result["risk_percent"] = (scores * 100).round(2)
    result["priority"]     = [assign_priority(s) for s in scores]

    result = result.sort_values("risk_score", ascending=False).reset_index(drop=True)

    return result
