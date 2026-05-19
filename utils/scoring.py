import joblib
import pandas as pd
from utils.schema import FEATURES

MODEL_PATH = "models/winner_model.joblib"

def load_model():
    return joblib.load(MODEL_PATH)

def score_dataframe(df):
    model = load_model()

    X = df[FEATURES].copy()

    scores = model.predict_proba(X)[:, 1]

    result = df.copy()
    result["risk_score"] = scores
    result["risk_percent"] = (scores * 100).round(2)

    def assign_priority(score):
        if score >= 0.7:
            return "High Priority"
        elif score >= 0.4:
            return "Medium Priority"
        else:
            return "Low Priority"

    result["priority"] = result["risk_score"].apply(assign_priority)

    result = result.sort_values("risk_score", ascending=False)

    return result
