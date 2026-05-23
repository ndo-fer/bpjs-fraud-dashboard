"""
scoring.py
----------
Scoring klaim menggunakan artifact multidomain/reguler:
- prep_label.pkl
- prep_predict.pkl
- isolation_forest.pkl
- winner_model.pkl
"""

from __future__ import annotations

import json
import pickle
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from catboost import Pool

from utils.schema import (
    DEFAULT_INPUT_VALUES,
    NUMERIC_INPUT_FEATURES,
    USER_INPUT_FEATURES,
)

APP_ROOT = Path(__file__).resolve().parents[1]

# Artifacts disimpan di dalam repo di folder models/reguler/
# sehingga ikut ter-deploy ke Railway/Render
ARTIFACT_DIR = APP_ROOT / "models" / "reguler"

# Fallback ke lokasi lama jika folder models/ tidak ada (local dev lama)
if not ARTIFACT_DIR.exists():
    ARTIFACT_DIR = APP_ROOT.parent / "output_multidomain" / "reguler"

WINNER_INFO_PATH     = ARTIFACT_DIR / "winner_info.json"
MODEL_PATH           = ARTIFACT_DIR / "winner_model.pkl"
PREP_PREDICT_PATH    = ARTIFACT_DIR / "prep_predict.pkl"
PREP_LABEL_PATH      = ARTIFACT_DIR / "prep_label.pkl"
ISOLATION_FOREST_PATH = ARTIFACT_DIR / "isolation_forest.pkl"


def _load_pickle(path: Path):
    with open(path, "rb") as fh:
        return pickle.load(fh)


@lru_cache(maxsize=1)
def load_artifacts() -> dict[str, Any]:
    if not WINNER_INFO_PATH.exists():
        raise FileNotFoundError(
            f"Model artifacts tidak ditemukan di: {ARTIFACT_DIR}\n"
            f"Pastikan folder models/reguler/ ada di dalam repo dashboard-v2 "
            f"dan berisi: winner_model.pkl, prep_predict.pkl, prep_label.pkl, "
            f"isolation_forest.pkl, winner_info.json"
        )
    return {
        "winner_info": json.loads(WINNER_INFO_PATH.read_text(encoding="utf-8")),
        "clf":   _load_pickle(MODEL_PATH),
        "prep_P": _load_pickle(PREP_PREDICT_PATH),
        "prep_L": _load_pickle(PREP_LABEL_PATH),
        "iso":   _load_pickle(ISOLATION_FOREST_PATH),
    }


def load_model():
    return load_artifacts()["clf"]


def load_model_metadata() -> dict[str, Any]:
    return load_artifacts()["winner_info"]


# Load threshold di module level — tapi safely dengan try/except
# agar import tidak crash jika artifact belum ada
try:
    _winner_info = json.loads(WINNER_INFO_PATH.read_text(encoding="utf-8"))
    THRESHOLD_HIGH = float(_winner_info.get("threshold", 0.48))
except FileNotFoundError:
    _winner_info = {}
    THRESHOLD_HIGH = 0.48

THRESHOLD_MEDIUM = min(
    THRESHOLD_HIGH - 0.05,
    max(0.30, round(THRESHOLD_HIGH * 0.625, 2)),
)


def assign_priority(score: float) -> str:
    if score >= THRESHOLD_HIGH:
        return "High Priority"
    if score >= THRESHOLD_MEDIUM:
        return "Medium Priority"
    return "Low Priority"


def _to_numeric(series: pd.Series, default: float = 0.0) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(default)


def _coerce_input_frame(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for feature in USER_INPUT_FEATURES:
        if feature not in out.columns:
            out[feature] = DEFAULT_INPUT_VALUES.get(feature)

    for feature in USER_INPUT_FEATURES:
        if feature in NUMERIC_INPUT_FEATURES:
            out[feature] = _to_numeric(out[feature], DEFAULT_INPUT_VALUES.get(feature, 0.0))
        else:
            out[feature] = out[feature].fillna(DEFAULT_INPUT_VALUES.get(feature, "")).astype(str)

    return out


def build_full_feature_df(df: pd.DataFrame) -> pd.DataFrame:
    out = _coerce_input_frame(df)

    out["severity_level_num"] = _to_numeric(out["severity_level_num"], 1.0)
    out["tarif_disetujui"] = _to_numeric(out["tarif_disetujui"])
    out["tarif_inacbg_dasar"] = _to_numeric(out["tarif_inacbg_dasar"])
    out["tarif_grouping"] = _to_numeric(out["tarif_grouping"])
    out["total_special_cmg"] = _to_numeric(out["total_special_cmg"])
    out["jumlah_special_cmg_aktif"] = _to_numeric(out["jumlah_special_cmg_aktif"])
    out["lama_rawat_hari"] = _to_numeric(out["lama_rawat_hari"], 1.0).clip(lower=0)
    out["jumlah_diagnosis_sekunder"] = _to_numeric(out["jumlah_diagnosis_sekunder"])
    out["jumlah_grup_diagnosis_sekunder"] = _to_numeric(
        out["jumlah_grup_diagnosis_sekunder"],
        out["jumlah_diagnosis_sekunder"],
    )
    out["fktp_hist_count_before"] = _to_numeric(out["fktp_hist_count_before"])
    out["nonkap_hist_count_before"] = _to_numeric(out["nonkap_hist_count_before"])
    out["nonkap_hist_total_before"] = _to_numeric(out["nonkap_hist_total_before"])
    out["nonkap_hist_mean_before"] = _to_numeric(out["nonkap_hist_mean_before"])
    out["regional_tarif_num"] = _to_numeric(out["regional_tarif_num"])

    zero_mean_mask = (
        out["nonkap_hist_mean_before"].eq(0) & out["nonkap_hist_count_before"].gt(0)
    )
    out.loc[zero_mean_mask, "nonkap_hist_mean_before"] = (
        out.loc[zero_mean_mask, "nonkap_hist_total_before"]
        / out.loc[zero_mean_mask, "nonkap_hist_count_before"].replace(0, np.nan)
    ).fillna(0)

    zero_total_mask = (
        out["nonkap_hist_total_before"].eq(0) & out["nonkap_hist_mean_before"].gt(0)
    )
    out.loc[zero_total_mask, "nonkap_hist_total_before"] = (
        out.loc[zero_total_mask, "nonkap_hist_mean_before"]
        * out.loc[zero_total_mask, "nonkap_hist_count_before"]
    )

    zero_special_mask = out["jumlah_special_cmg_aktif"].eq(0) & out["total_special_cmg"].gt(0)
    out.loc[zero_special_mask, "jumlah_special_cmg_aktif"] = 1

    out["rasio_tarif_setuju_vs_dasar"] = np.where(
        out["tarif_inacbg_dasar"] > 0,
        out["tarif_disetujui"] / out["tarif_inacbg_dasar"],
        0.0,
    )
    out["rasio_tarif_grouping_vs_setuju"] = np.where(
        out["tarif_disetujui"] > 0,
        out["tarif_grouping"] / out["tarif_disetujui"],
        0.0,
    )
    out["biaya_per_hari"] = np.where(
        out["lama_rawat_hari"] > 0,
        out["tarif_disetujui"] / out["lama_rawat_hari"],
        out["tarif_disetujui"],
    )
    out["intensitas_diag_sekunder"] = np.where(
        out["lama_rawat_hari"] > 0,
        out["jumlah_diagnosis_sekunder"] / out["lama_rawat_hari"],
        out["jumlah_diagnosis_sekunder"],
    )
    out["beban_histori"] = (
        out["fktp_hist_count_before"] + out["nonkap_hist_count_before"]
    )

    for flag in [
        "flag_rawat_inap",
        "flag_status_nonaktif",
        "flag_kelas_upgrade",
        "flag_meninggal",
        "flag_rujukan_missing",
        "flag_special_cmg",
    ]:
        out[flag] = _to_numeric(out[flag]).clip(lower=0, upper=1).astype(int)

    return out.replace([np.inf, -np.inf], 0).fillna(0)


def prepare_prediction_frame(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, dict[str, Any]]:
    artifacts = load_artifacts()
    info = artifacts["winner_info"]

    feat_L = info["feat_L_order"]
    feat_P = info["feat_P_order"]

    full_df = build_full_feature_df(df)
    XL = artifacts["prep_L"].transform(full_df[feat_L])
    XP = pd.DataFrame(
        artifacts["prep_P"].transform(full_df[feat_P]),
        columns=feat_P,
        index=full_df.index,
    )
    return full_df, XP, XL, info


def explain_single_claim(input_data: dict[str, Any], top_n: int = 4) -> dict[str, Any]:
    artifacts = load_artifacts()
    full_df, XP, _XL, info = prepare_prediction_frame(pd.DataFrame([input_data]))
    winner_features = info["winner_features"]

    feature_frame = XP[winner_features]
    shap_values = artifacts["clf"].get_feature_importance(
        data=Pool(feature_frame),
        type="ShapValues",
    )
    feature_contribs = shap_values[0, :-1]
    base_value = float(shap_values[0, -1])

    rows: list[dict[str, Any]] = []
    for feature_name, contribution in zip(winner_features, feature_contribs):
        actual_value = full_df.iloc[0][feature_name] if feature_name in full_df.columns else feature_frame.iloc[0][feature_name]
        rows.append(
            {
                "feature": feature_name,
                "feature_value": actual_value,
                "contribution": float(contribution),
                "abs_contribution": float(abs(contribution)),
                "direction": "up" if contribution > 0 else "down" if contribution < 0 else "neutral",
            }
        )

    explanation_df = pd.DataFrame(rows).sort_values("abs_contribution", ascending=False).reset_index(drop=True)
    drivers_up = explanation_df[explanation_df["contribution"] > 0].head(top_n).to_dict(orient="records")
    drivers_down = explanation_df[explanation_df["contribution"] < 0].head(top_n).to_dict(orient="records")

    return {
        "base_value": base_value,
        "top_drivers_up": drivers_up,
        "top_drivers_down": drivers_down,
        "explanation_df": explanation_df,
    }


def score_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    artifacts = load_artifacts()
    info = artifacts["winner_info"]
    winner_features = info["winner_features"]
    threshold = float(info["threshold"])

    full_df, XP, XL, _ = prepare_prediction_frame(df)

    risk_scores = artifacts["clf"].predict_proba(XP[winner_features])[:, 1]
    iforest_scores = -artifacts["iso"].score_samples(XL)

    result = full_df.copy()
    result["risk_score"] = risk_scores
    result["risk_percent"] = (risk_scores * 100).round(2)
    result["priority"] = [assign_priority(score) for score in risk_scores]
    result["threshold_used"] = threshold
    result["iforest_score"] = iforest_scores
    result["model_domain"] = info.get("domain", "reguler")

    return result.sort_values("risk_score", ascending=False).reset_index(drop=True)
