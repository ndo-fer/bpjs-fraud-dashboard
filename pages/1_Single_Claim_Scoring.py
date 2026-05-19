import streamlit as st
import pandas as pd

from utils.scoring import score_dataframe
from utils.schema import FEATURE_LABELS

st.set_page_config(
    page_title="Single Claim Scoring",
    layout="wide"
)

st.title("Single Claim Scoring")
st.write("Input data satu klaim untuk mendapatkan skor risiko.")

st.warning(
    "Output model adalah indikasi risiko untuk prioritas verifikasi, bukan keputusan fraud final."
)

col1, col2 = st.columns(2)

with col1:
    fktp_hist_count_before = st.number_input("Riwayat Kunjungan FKTP", min_value=0, value=0)
    flag_kelas_upgrade = st.selectbox("Upgrade Kelas", [0, 1], format_func=lambda x: "Ya" if x == 1 else "Tidak")
    flag_status_nonaktif = st.selectbox("Status Kepesertaan Nonaktif", [0, 1], format_func=lambda x: "Ya" if x == 1 else "Tidak")
    jumlah_diagnosis_sekunder = st.number_input("Jumlah Diagnosis Sekunder", min_value=0, value=0)
    lama_rawat_hari = st.number_input("Lama Rawat (Hari)", min_value=0, value=0)

with col2:
    nonkap_hist_count_before = st.number_input("Riwayat Non-Kapitasi", min_value=0, value=0)
    severity_level = st.selectbox("Severity Level", [1, 2, 3])
    tarif_disetujui = st.number_input("Tarif Disetujui", min_value=0, value=0, step=100000)
    total_special_cmg = st.number_input("Total Special CMG", min_value=0, value=0)
    usia = st.number_input("Usia", min_value=0, max_value=120, value=30)

input_data = {
    "fktp_hist_count_before": fktp_hist_count_before,
    "flag_kelas_upgrade": flag_kelas_upgrade,
    "flag_status_nonaktif": flag_status_nonaktif,
    "jumlah_diagnosis_sekunder": jumlah_diagnosis_sekunder,
    "lama_rawat_hari": lama_rawat_hari,
    "nonkap_hist_count_before": nonkap_hist_count_before,
    "severity_level": severity_level,
    "tarif_disetujui": tarif_disetujui,
    "total_special_cmg": total_special_cmg,
    "usia": usia,
}

if st.button("Hitung Skor Risiko"):
    df = pd.DataFrame([input_data])
    result = score_dataframe(df)

    priority = result.iloc[0]["priority"]
    risk_percent = result.iloc[0]["risk_percent"]

    st.subheader("Hasil Scoring")

    c1, c2 = st.columns(2)
    c1.metric("Prioritas Verifikasi", priority)
    c2.metric("Persentase Risiko", f"{risk_percent}%")

    st.dataframe(result.rename(columns=FEATURE_LABELS))
