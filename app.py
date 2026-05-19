import streamlit as st
import pandas as pd

from utils.scoring import score_dataframe
from utils.schema import FEATURES, FEATURE_LABELS

st.set_page_config(
    page_title="Dashboard PA",
    layout="wide"
)

st.title("Dashboard Prioritas Verifikasi Klaim")

st.warning(
    "Output model adalah indikasi risiko untuk prioritas verifikasi, bukan keputusan fraud final."
)
with open("data/batch_template.csv", "rb") as file:
    st.download_button(
        label="Download Template CSV",
        data=file,
        file_name="batch_template.csv",
        mime="text/csv"
    )

uploaded_file = st.file_uploader(
    "Upload CSV klaim",
    type=["csv"]
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("Preview Data")
    st.dataframe(df.head().rename(columns=FEATURE_LABELS))

    missing_cols = [col for col in FEATURES if col not in df.columns]

    if missing_cols:
        readable_missing = [FEATURE_LABELS.get(col, col) for col in missing_cols]

        st.error("Format CSV belum sesuai.")
        st.write("Kolom yang belum ada:")
        for col in readable_missing:
            st.markdown(f"- {col}")

        st.info("Silakan download template CSV di atas, lalu isi data sesuai format tersebut.")
    else:
        result = score_dataframe(df)

        st.subheader("Ringkasan Hasil")

        total_claim = len(result)
        high_priority = (result["priority"] == "High Priority").sum()
        low_priority = (result["priority"] == "Low Priority").sum()
        avg_risk = result["risk_percent"].mean().round(2)

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Klaim", total_claim)
        col2.metric("High Priority", high_priority)
        col3.metric("Low Priority", low_priority)
        col4.metric("Rata-rata Risiko", f"{avg_risk}%")

        st.subheader("Hasil Risk Scoring")  
        output_cols = ["priority", "risk_percent", "risk_score"]
        other_cols = [col for col in result.columns if col not in output_cols]

        result = result[output_cols + other_cols]

        display_result = result.rename(columns=FEATURE_LABELS)
        st.dataframe(display_result)

        csv = result.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download Hasil CSV",
            data=csv,
            file_name="hasil_scoring.csv",
            mime="text/csv"
        )
else:
    st.info("Upload file CSV untuk mulai scoring.")
