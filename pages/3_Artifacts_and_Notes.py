import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.schema import USER_INPUT_FEATURES, FEATURE_LABELS
from utils.scoring import load_model, THRESHOLD_HIGH, THRESHOLD_MEDIUM

st.set_page_config(
    page_title="Artifacts & Notes",
    layout="wide"
)

st.title("Artifacts & Notes")

# ── Model info ────────────────────────────────────────────────────────────────
st.subheader("Model Artifact")

col1, col2, col3 = st.columns(3)
col1.metric("Model", "XGBoost")
col2.metric("Jumlah Fitur", len(USER_INPUT_FEATURES))
col3.metric("Threshold High", f"{int(THRESHOLD_HIGH * 100)}%")

st.code("models/winner_model.joblib")
st.caption("Model XGBoost classifier hasil training dari notebook final.")

# ── Metrik evaluasi ───────────────────────────────────────────────────────────
st.subheader("Metrik Evaluasi Model")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("ROC-AUC",   "0.9999")
col2.metric("PR-AUC",    "0.9960")
col3.metric("F1-Score",  "0.9525")
col4.metric("Precision", "0.9139")
col5.metric("Recall",    "0.9945")

st.caption("Metrik dievaluasi pada test set (sumber: final_metrics.json dari notebook training).")

# ── Feature Importance ────────────────────────────────────────────────────────
st.subheader("Feature Importance Global")

model = load_model()

if hasattr(model, "feature_importances_"):
    feature_names = (
        list(model.feature_names_in_)
        if hasattr(model, "feature_names_in_")
        else USER_INPUT_FEATURES
    )
    importances = model.feature_importances_

    imp_df = pd.DataFrame({
        "Fitur":      [FEATURE_LABELS.get(f, f) for f in feature_names],
        "Kode":       feature_names,
        "Importance": importances,
    }).sort_values("Importance", ascending=True)

    fig = px.bar(
        imp_df,
        x="Importance",
        y="Fitur",
        orientation="h",
        text=imp_df["Importance"].apply(lambda v: f"{v:.1%}"),
        color="Importance",
        color_continuous_scale="Blues",
        title="Feature Importance — XGBoost (gain)",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        xaxis_title="Importance Score",
        yaxis_title="",
        height=400,
        margin=dict(l=0, r=60, t=40, b=0),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Top 3 highlight
    top3 = imp_df.sort_values("Importance", ascending=False).head(3)
    st.markdown("**Top 3 fitur paling berpengaruh:**")
    for i, row in enumerate(top3.itertuples(), 1):
        st.markdown(f"- **{i}. {row.Fitur}** (`{row.Kode}`) — {row.Importance:.1%}")
else:
    st.info("Feature importance tidak tersedia untuk model ini.")

# ── Threshold ─────────────────────────────────────────────────────────────────
st.subheader("Priority Threshold")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
| Kategori | Kondisi |
|---|---|
| 🔴 **High Priority** | skor risiko ≥ {int(THRESHOLD_HIGH * 100)}% |
| 🟡 **Medium Priority** | {int(THRESHOLD_MEDIUM * 100)}% ≤ skor < {int(THRESHOLD_HIGH * 100)}% |
| 🟢 **Low Priority** | skor risiko < {int(THRESHOLD_MEDIUM * 100)}% |
""")

with col2:
    st.info(
        "Threshold ditentukan berdasarkan kebutuhan operasional triage klaim. "
        "High Priority = prioritas verifikasi segera. "
        "Hasil tetap dibaca sebagai indikasi risiko, bukan keputusan fraud final."
    )

# ── Fitur input ───────────────────────────────────────────────────────────────
st.subheader("Input Features")

st.caption("10 fitur ini diisi pengguna melalui form (single claim) atau kolom CSV (batch).")

cols = st.columns(2)
for i, feature in enumerate(USER_INPUT_FEATURES):
    cols[i % 2].markdown(f"- **{FEATURE_LABELS.get(feature, feature)}** `{feature}`")

# ── Catatan preprocessing ─────────────────────────────────────────────────────
st.subheader("Catatan Preprocessing & Inference")

st.markdown("""
- Model menerima input **numerik langsung** tanpa scaling terpisah.
- XGBoost menangani variasi skala fitur secara internal (tree-based, tidak perlu normalisasi).
- Tidak ada `preprocessor.pkl` terpisah — konsistensi dijaga melalui tipe dan urutan fitur.
- Fitur bertipe biner (flag) diinput sebagai **0** atau **1**.
""")

# ── Disclaimer ────────────────────────────────────────────────────────────────
st.subheader("Disclaimer")

st.warning(
    "Output model adalah indikasi risiko untuk prioritas verifikasi, bukan keputusan fraud final."
)

st.info(
    "Dashboard ini merupakan prototype akademik. Prediksi berbasis pseudo-label, "
    "bukan label fraud yang terverifikasi secara hukum atau medis. "
    "Hasil scoring digunakan untuk mendukung prioritas verifikasi, bukan sebagai keputusan final."
)
