import streamlit as st

st.set_page_config(
    page_title="Dashboard PA",
    layout="wide"
)

st.title("Dashboard Prioritas Verifikasi Klaim")

st.write("""
Prototype dashboard untuk membantu prioritas verifikasi klaim
berdasarkan hasil scoring model machine learning.
""")

st.warning(
    "Output model adalah indikasi risiko untuk prioritas verifikasi, bukan keputusan fraud final."
)

st.subheader("Navigasi")

st.markdown("""
Silakan gunakan menu di sidebar:

- **Overview** untuk penjelasan dashboard.
- **Single Claim Scoring** untuk scoring satu klaim.
- **Batch Upload** untuk scoring banyak klaim dari CSV.
""")
