import streamlit as st
import pandas as pd
import plotly.express as px

from utils.scoring import score_dataframe, load_model, THRESHOLD_HIGH, THRESHOLD_MEDIUM
from utils.schema import USER_INPUT_FEATURES, FEATURE_LABELS

st.set_page_config(
    page_title="Single Claim Scoring",
    layout="wide"
)

st.title("Single Claim Scoring")
st.write("Input data satu klaim untuk mendapatkan skor risiko.")

st.warning(
    "Output model adalah indikasi risiko untuk prioritas verifikasi, bukan keputusan fraud final."
)

# ── Form input ─────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    fktp_hist_count_before    = st.number_input("Riwayat Kunjungan FKTP", min_value=0, value=0)
    flag_kelas_upgrade        = st.selectbox("Upgrade Kelas", [0, 1],
                                             format_func=lambda x: "Ya" if x == 1 else "Tidak")
    flag_status_nonaktif      = st.selectbox("Status Kepesertaan Nonaktif", [0, 1],
                                             format_func=lambda x: "Ya" if x == 1 else "Tidak")
    jumlah_diagnosis_sekunder = st.number_input("Jumlah Diagnosis Sekunder", min_value=0, value=0)
    lama_rawat_hari           = st.number_input("Lama Rawat (Hari)", min_value=0, value=0)

with col2:
    nonkap_hist_count_before  = st.number_input("Riwayat Non-Kapitasi", min_value=0, value=0)
    severity_level            = st.selectbox("Severity Level", [1, 2, 3])
    tarif_disetujui           = st.number_input("Tarif Disetujui", min_value=0, value=0, step=100_000)
    total_special_cmg         = st.number_input("Total Special CMG", min_value=0, value=0)
    usia                      = st.number_input("Usia", min_value=0, max_value=120, value=30)

input_data = {
    "fktp_hist_count_before":    fktp_hist_count_before,
    "flag_kelas_upgrade":        flag_kelas_upgrade,
    "flag_status_nonaktif":      flag_status_nonaktif,
    "jumlah_diagnosis_sekunder": jumlah_diagnosis_sekunder,
    "lama_rawat_hari":           lama_rawat_hari,
    "nonkap_hist_count_before":  nonkap_hist_count_before,
    "severity_level":            severity_level,
    "tarif_disetujui":           tarif_disetujui,
    "total_special_cmg":         total_special_cmg,
    "usia":                      usia,
}

# ── Scoring ────────────────────────────────────────────────────────────────────
if st.button("Hitung Skor Risiko", type="primary"):
    df     = pd.DataFrame([input_data])
    result = score_dataframe(df)

    priority    = result.iloc[0]["priority"]
    risk_percent = result.iloc[0]["risk_percent"]
    risk_score   = result.iloc[0]["risk_score"]

    st.subheader("Hasil Scoring")

    # ── Warna priority ────────────────────────────────────────────────────────
    PRIORITY_STYLE = {
        "High Priority":   ("🔴", "#c0392b", "#fdf3f2", "🔴 Klaim ini masuk prioritas verifikasi segera."),
        "Medium Priority": ("🟡", "#d68910", "#fef9e7", "🟡 Klaim ini perlu perhatian lebih lanjut."),
        "Low Priority":    ("🟢", "#1e8449", "#eafaf1", "🟢 Klaim ini memiliki risiko rendah."),
    }

    icon, border_color, bg_color, message = PRIORITY_STYLE.get(
        priority,
        ("⚪", "#888", "#f5f5f5", priority)
    )

    st.markdown(f"""
<div style="background-color:{bg_color}; border-left:6px solid {border_color};
            padding:16px 20px; border-radius:8px; margin-bottom:12px;">
    <div style="font-size:22px; font-weight:700; color:{border_color};">
        {icon} {priority}
    </div>
    <div style="font-size:28px; font-weight:800; color:{border_color}; margin:4px 0;">
        {risk_percent}%
    </div>
    <div style="color:#555; font-size:14px;">{message}</div>
</div>
""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    c1.metric("Prioritas Verifikasi", priority)
    c2.metric("Persentase Risiko",    f"{risk_percent}%")

    # ── Top 3 Faktor Dominan ──────────────────────────────────────────────────
    model = load_model()

    if hasattr(model, "feature_importances_"):
        feature_names = (
            list(model.feature_names_in_)
            if hasattr(model, "feature_names_in_")
            else USER_INPUT_FEATURES
        )
        importances = model.feature_importances_

        feat_imp = sorted(
            zip(feature_names, importances),
            key=lambda x: x[1],
            reverse=True,
        )

        st.subheader("Top 3 Faktor Dominan")
        st.caption(
            "Berdasarkan feature importance global model XGBoost. "
            "Menunjukkan fitur yang paling berpengaruh pada prediksi."
        )

        imp_df = pd.DataFrame({
            "Fitur":     [FEATURE_LABELS.get(f, f) for f, _ in feat_imp[:3]],
            "Importance": [imp for _, imp in feat_imp[:3]],
            "Nilai Input": [input_data.get(f, "-") for f, _ in feat_imp[:3]],
        })

        # Bar chart horizontal
        fig = px.bar(
            imp_df[::-1],          # balik agar rank 1 di atas
            x="Importance",
            y="Fitur",
            orientation="h",
            text=imp_df[::-1]["Importance"].apply(lambda v: f"{v:.1%}"),
            color="Importance",
            color_continuous_scale="Blues",
            title="Top 3 Fitur Berpengaruh",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            xaxis_title="Importance Score",
            yaxis_title="",
            height=220,
            margin=dict(l=0, r=30, t=40, b=0),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Tabel ringkasan
        for rank, (fname, fimp) in enumerate(feat_imp[:3], 1):
            label = FEATURE_LABELS.get(fname, fname)
            val   = input_data.get(fname, "-")
            st.markdown(
                f"**{rank}. {label}** — nilai input: `{val}` "
                f"| kontribusi model: **{fimp:.1%}**"
            )

    # ── Tabel lengkap ─────────────────────────────────────────────────────────
    with st.expander("Lihat detail input lengkap", expanded=False):
        st.dataframe(result.rename(columns=FEATURE_LABELS))
